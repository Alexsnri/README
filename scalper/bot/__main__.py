"""Starts the bot: `python -m bot`.

Internal watchdog: each agent runs as a supervised task; if one crashes it gets restarted with backoff and logged
as ERROR. If the main loop stops ticking for 5 min, the process exits with an error so the platform (Railway /
Docker with restart=always) restarts it; on startup it picks up the state (positions, stops, Learner, breakers)
from SQLite and checks it against Capital.com before doing anything else.
"""
import asyncio
import hashlib
import os
import signal
import sys
import time
from datetime import datetime, timezone

import pandas as pd

from . import config, report, schedule
from .config import profile
from .engine import Engine
from .info import Info
from .instruments import INSTRUMENTS
from .learner import Learner
from .logger import Hub, Logger
from .store import Store
from .telegram import Telegram
from .web import Web


async def supervise(name, factory, log, stop_event):
    backoff = 2
    while not stop_event.is_set():
        t0 = time.time()
        try:
            await factory()
            if stop_event.is_set():
                return
            log("ERROR", "-", f"tarea {name} terminó sola; la reinicio", "error")
        except asyncio.CancelledError:
            return
        except Exception as e:
            log("ERROR", "-", f"tarea {name} se cayó: {type(e).__name__}: {e}; reinicio en {backoff}s", "error")
        if time.time() - t0 > 300:
            backoff = 2
        await asyncio.sleep(backoff)
        backoff = min(300, backoff * 2)


def make_broker(cfg, log):
    if cfg["sim"]:
        from .fakebroker import FakeBroker
        sys.path.insert(0, os.path.join(config.ROOT, "lab"))
        from data import load_1m
        start = os.environ.get("SIM_START", "2026-10-05")
        data = {i: load_1m(i) for i in ("US100", "US500")}
        data = {i: d[d.index >= pd.Timestamp(start, tz="UTC") - pd.Timedelta(days=30)] for i, d in data.items()}
        return FakeBroker(data, start=start, speed=float(os.environ.get("SIM_SPEED", "300")))
    if cfg["has_credentials"]:
        from .capital import CapitalClient
        return CapitalClient(os.environ["CAPITAL_API_KEY"], os.environ["CAPITAL_IDENTIFIER"],
                             os.environ["CAPITAL_API_PASSWORD"], log)
    return None


async def amain():
    cfg = config.load()
    store = Store(os.path.join(cfg["data_dir"], "bot.db"))
    cfg["perfil"] = store.kv_get("perfil", cfg["perfil"])
    hub = Hub()
    log = Logger(store, hub, os.path.join(cfg["data_dir"], "logs"))
    pw = config.dashboard_password(store)
    code = str(int(hashlib.sha256(("tg:" + pw).encode()).hexdigest(), 16) % 1_000_000).zfill(6)
    tg = Telegram(store, log, code)
    log.listeners.append(tg.on_log)
    broker = make_broker(cfg, log)
    bt = report.backtest_expectation().get("brazos", {})
    learner = Learner(cfg["learner"], cfg["brazos"], {k: v.get("E_oos", 0.0) for k, v in bt.items()}, store, log)
    holder = {}
    info = Info(cfg, lambda: holder["eng"], broker, log, store)

    class NoBroker:   # no credentials: the dashboard explains how to set them up
        def now(self):
            return time.time()
    engine = Engine(cfg, store, log, hub, broker or NoBroker(), info, learner, notify=tg.send)
    holder["eng"] = engine
    log.now = engine.now
    webapp = Web(cfg, engine, learner, info, log, store, pw, code)
    stop_event = asyncio.Event()

    # ---------------- commands (Telegram and dashboard)
    async def c_estado(*a):
        await engine.refresh_account() if broker else None
        b = engine.account.get("balance")
        pos = [p for p in engine.positions.values() if not p["shadow"]]
        txt = [f"Estado: {engine.status}{' (PAUSADO)' if engine.paused else ''} · perfil {cfg['perfil']} · franja "
               f"{schedule.slot_at(datetime.now(timezone.utc))}"]
        if b is not None:
            txt.append(f"Balance Capital.com DEMO: ${b:,.2f} · no realizado {engine.account.get('upl') or 0:+.2f}")
        for p in pos:
            txt.append(f"{p['instrumento']} {'COMPRA' if p['dir'] > 0 else 'VENTA'} {p['size']:g} @ {p['entry']:g} · "
                       f"stop {p['stop']:g}")
        if not pos:
            txt.append("Sin posiciones abiertas.")
        return "\n".join(txt)

    async def c_pausa(*a):
        engine.paused = True
        store.kv_set("paused", True)
        engine.status = "pausado"
        log("PAUSA", "-", "pausado por el usuario (las abiertas siguen con su stop)")
        return "⏸ Pausado. Las posiciones abiertas siguen protegidas con su stop en el servidor."

    async def c_reanudar(*a):
        engine.paused = False
        store.kv_set("paused", False)
        engine.status = "operando"
        log("PAUSA", "-", "reanudado por el usuario")
        return "▶️ Reanudado."

    async def c_perfil(*a):
        if not a or a[0] not in cfg["perfiles"]:
            return f"Perfil actual: {cfg['perfil']}. Usa /perfil normal o /perfil agresivo"
        cfg["perfil"] = a[0]
        store.kv_set("perfil", a[0])
        engine.risk.p = profile(cfg)
        log("PERFIL", "-", f"perfil → {a[0]} ({engine.risk.p['riesgo_por_trade_pct']}% por trade)")
        return f"Perfil {a[0]}: {engine.risk.p['riesgo_por_trade_pct']}% por trade."

    async def c_reporte(*a):
        return report.to_text(report.build(store, learner, engine.account, engine.start_balance, engine.now()))

    async def c_promover(*a):
        if not a or a[0] not in learner.arms:
            return "Uso: /promover S1-US500 (brazos: " + ", ".join(learner.arms) + ")"
        learner.promote(a[0])
        return f"{a[0]} pasa a vivo con medio riesgo."

    cmds = {"/estado": c_estado, "/pausa": c_pausa, "/reanudar": c_reanudar, "/perfil": c_perfil,
            "/reporte": c_reporte, "/promover": c_promover}
    tg.handlers.update(cmds)
    webapp.commands.update(cmds)
    await webapp.start(cfg["port"])
    log("SEGUR", "-", "solo DEMO: " + cfg["api_url"])
    if not os.environ.get("DASHBOARD_PASSWORD"):
        log("SEGUR", "-", "DASHBOARD_PASSWORD no está definida: se generó una y se guardó en la base (ver LEEME)")

    tasks = []

    def spawn(name, factory):
        tasks.append(asyncio.create_task(supervise(name, factory, log, stop_event)))

    if tg.enabled:
        spawn("telegram-envio", tg.sender)
        spawn("telegram-comandos", tg.poller)

    if broker is None:
        engine.status = "sin credenciales"
        log("ERROR", "-", "faltan CAPITAL_API_KEY / CAPITAL_IDENTIFIER / CAPITAL_API_PASSWORD; el bot no opera hasta "
            "configurarlas (ver LEEME.md)", "error")
    else:
        backoff = 5
        while True:
            try:
                await engine.startup()
                break
            except Exception as e:
                engine.status = "error al arrancar"
                log("ERROR", "-", f"arranque: {type(e).__name__}: {e}; reintento en {backoff}s", "error")
                await asyncio.sleep(backoff)
                backoff = min(300, backoff * 2)
        tg.send(f"🤖 Bot DEMO arrancado · perfil {cfg['perfil']} · balance "
                f"${engine.account.get('balance') or 0:,.2f}. Dashboard listo.")
        if cfg["sim"]:
            async def replay():
                await broker.run(engine.on_quote, until=os.environ.get("SIM_END"))
                log("SIM", "-", "fin del replay")
                if os.environ.get("SIM_EXIT"):
                    stop_event.set()
                else:
                    await asyncio.Event().wait()
            spawn("replay", replay)
        else:
            from .capital import Stream
            engine.stream = Stream(broker, [INSTRUMENTS[i].epic for i in engine.instruments], engine.on_quote, log)
            spawn("stream", engine.stream.run)
            spawn("keepalive", engine.loop_keepalive)
            spawn("info", lambda: info.loop(engine.instruments))
        spawn("reconciliacion", engine.loop_reconcile)
        spawn("cuenta", engine.loop_account)

    async def scheduler():
        last_prune = 0
        while True:
            webapp.heartbeat = time.time()
            if broker is not None:
                await engine.tick_schedule()
                now = datetime.fromtimestamp(engine.now(), timezone.utc).astimezone(schedule.CDMX)
                hh = cfg["reportes"]["resumen_diario_hora_cdmx"]
                if now.strftime("%H:%M") >= hh and store.kv_get("ultimo_resumen") != now.date().isoformat():
                    store.kv_set("ultimo_resumen", now.date().isoformat())
                    rep = report.build(store, learner, engine.account, engine.start_balance, engine.now())
                    report.write_daily(os.path.join(cfg["data_dir"], "reports"), rep)
                    tg.send(report.to_text(rep))
                    log("RESUM", "-", "resumen diario enviado")
            if time.time() - last_prune > 86400:
                store.prune()
                last_prune = time.time()
            await asyncio.sleep(10 if not cfg["sim"] else 1)

    spawn("scheduler", scheduler)

    async def watchdog():
        while True:
            await asyncio.sleep(60)
            if time.time() - webapp.heartbeat > 300:
                log("ERROR", "-", "el bot dejó de latir 5 min: reinicio el proceso", "error")
                os._exit(3)

    spawn("watchdog", watchdog)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass
    await stop_event.wait()
    log("FIN", "-", "apagado ordenado (las posiciones quedan con su stop en el servidor)")
    for t in tasks:
        t.cancel()


def main():
    try:
        asyncio.run(amain())
    except config.NotDemoError as e:
        print(f"ALTO: {e}", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
