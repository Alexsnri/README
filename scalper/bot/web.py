"""Live dashboard server (aiohttp + WebSocket). Protected with a password; never sends credentials to the frontend."""
import asyncio
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone

from aiohttp import WSMsgType, web

from . import report, schedule
from .instruments import INSTRUMENTS

STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
LOGIN = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport"
content="width=device-width,initial-scale=1"><title>Scalper DEMO</title><style>
body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0b0f1a;color:#e6e9f2;
font:16px ui-monospace,Menlo,monospace}form{background:#121828;border:1px solid #243049;border-radius:14px;
padding:28px;width:min(340px,90vw)}h1{font-size:20px;margin:0 0 6px}p{color:#8a94ad;font-size:13px}
input,button{width:100%;box-sizing:border-box;padding:12px;border-radius:10px;border:1px solid #243049;
background:#0b0f1a;color:#e6e9f2;font:inherit;margin-top:10px}button{background:#7c5cff;border:0;font-weight:700}
.b{display:inline-block;background:#f5b041;color:#111;border-radius:6px;padding:2px 8px;font-size:12px;font-weight:700}
</style></head><body><form method="post" action="/login"><h1>Scalper <span class="b">DEMO</span></h1>
<p>Escribe la contraseña del dashboard (DASHBOARD_PASSWORD).</p>%ERR%<input type="password" name="pw"
autocomplete="current-password" autofocus><button>Entrar</button></form></body></html>"""


class Web:
    def __init__(self, cfg, engine, learner, info, log, store, password, pairing_code):
        self.cfg, self.eng, self.learner, self.info, self.log, self.store = cfg, engine, learner, info, log, store
        self.pw = password
        self.code = pairing_code
        salt = store.kv_get("cookie_salt")
        if not salt:
            salt = __import__("secrets").token_hex(16)
            store.kv_set("cookie_salt", salt)
        self.secret = hashlib.sha256(f"cookie:{salt}:{password}".encode()).hexdigest()
        self.fails = {}   # ip -> [timestamps of failed attempts]
        self.heartbeat = time.time()
        self.app = web.Application()
        r = self.app.router
        r.add_get("/health", self.health)
        r.add_get("/login", self.login_page)
        r.add_post("/login", self.login_post)
        r.add_get("/", self.index)
        r.add_get("/api/state", self.api_state)
        r.add_get("/api/report", self.api_report)
        r.add_post("/api/cmd", self.api_cmd)
        r.add_get("/ws", self.ws)
        r.add_static("/static", STATIC)
        r.add_get("/manifest.webmanifest", lambda req: web.FileResponse(os.path.join(STATIC, "manifest.webmanifest")))
        r.add_get("/sw.js", lambda req: web.FileResponse(os.path.join(STATIC, "sw.js")))
        self.commands = {}

    # ---------------------------------------------------------------- auth
    def _ok(self, req):
        c = req.cookies.get("s", "")
        return hmac.compare_digest(c, self.secret)

    async def login_page(self, req):
        return web.Response(text=LOGIN.replace("%ERR%", ""), content_type="text/html")

    async def login_post(self, req):
        ip = req.headers.get("X-Forwarded-For", req.remote or "?").split(",")[0].strip()
        now = time.time()
        recent = [t for t in self.fails.get(ip, []) if now - t < 900]
        if len(recent) >= 5:
            return web.Response(text=LOGIN.replace("%ERR%", '<p style="color:#ff6b81">Demasiados intentos. '
                                'Espera 15 minutos.</p>'), content_type="text/html", status=429)
        data = await req.post()
        await asyncio.sleep(0.5)
        if hmac.compare_digest(str(data.get("pw", "")), self.pw):
            self.fails.pop(ip, None)
            resp = web.HTTPFound("/")
            resp.set_cookie("s", self.secret, max_age=90 * 86400, httponly=True, samesite="Lax",
                            secure=req.secure or req.headers.get("X-Forwarded-Proto") == "https")
            raise resp
        self.fails[ip] = recent + [now]
        if len(self.fails) > 1000:
            self.fails.clear()
        self.log("SEGUR", "-", f"intento de acceso fallido al dashboard ({len(recent) + 1}/5)", "warn")
        return web.Response(text=LOGIN.replace("%ERR%", '<p style="color:#ff6b81">Contraseña incorrecta</p>'),
                            content_type="text/html")

    async def health(self, req):
        age = time.time() - self.heartbeat
        return web.json_response({"ok": age < 180, "estado": self.eng.status, "latido_seg": round(age)},
                                 status=200 if age < 180 else 503)

    async def index(self, req):
        if not self._ok(req):
            raise web.HTTPFound("/login")
        return web.FileResponse(os.path.join(STATIC, "index.html"), headers={"Cache-Control": "no-cache"})

    async def api_state(self, req):
        if not self._ok(req):
            raise web.HTTPUnauthorized()
        return web.json_response(self.snapshot(), dumps=lambda o: json.dumps(o, default=str))

    async def api_report(self, req):
        if not self._ok(req):
            raise web.HTTPUnauthorized()
        rep = report.build(self.store, self.learner, self.eng.account, self.eng.start_balance, self.eng.now())
        return web.json_response({"reporte": rep, "texto": report.to_text(rep)}, dumps=lambda o: json.dumps(o, default=str))

    async def api_cmd(self, req):
        if not self._ok(req):
            raise web.HTTPUnauthorized()
        body = await req.json()
        h = self.commands.get("/" + str(body.get("cmd", "")))
        if not h:
            return web.json_response({"ok": False, "msg": "comando desconocido"})
        msg = await h(*([body["arg"]] if body.get("arg") else []))
        return web.json_response({"ok": True, "msg": msg})

    async def ws(self, req):
        if not self._ok(req):
            raise web.HTTPUnauthorized()
        ws = web.WebSocketResponse(heartbeat=30)
        await ws.prepare(req)
        q = self.eng.hub.subscribe()
        await ws.send_str(json.dumps({"kind": "snapshot", "data": self.snapshot()}, default=str))
        last_full = time.time()
        last_quote = {}
        try:
            while not ws.closed:
                try:
                    ev = await asyncio.wait_for(q.get(), timeout=2.0)
                    if ev["kind"] == "quote":
                        i = ev["data"]["inst"]
                        if time.time() - last_quote.get(i, 0) < 1.0:
                            continue
                        last_quote[i] = time.time()
                    await ws.send_str(json.dumps(ev, default=str))
                except asyncio.TimeoutError:
                    pass
                if time.time() - last_full > 3:
                    await ws.send_str(json.dumps({"kind": "snapshot", "data": self.snapshot()}, default=str))
                    last_full = time.time()
        except (ConnectionResetError, RuntimeError):
            pass
        finally:
            self.eng.hub.unsubscribe(q)
        return ws

    # ---------------------------------------------------------------- state
    def snapshot(self):
        e = self.eng
        now = e.now()
        t0 = report.day_start(now)
        ev_today = self.store.q("SELECT evento, COUNT(*) n FROM events WHERE ts>=? GROUP BY evento", (t0,))
        cnt = {r["evento"]: r["n"] for r in ev_today}
        last_move = self.store.q("SELECT hhmm,instrumento,detalle FROM events WHERE evento='MOVE' ORDER BY id DESC LIMIT 1")
        live = [p for p in e.positions.values() if not p["shadow"]]
        shadow = [p for p in e.positions.values() if p["shadow"]]
        main_inst = live[0]["instrumento"] if live else (shadow[0]["instrumento"] if shadow else "US100")
        rep = report.build(self.store, self.learner, e.account, e.start_balance, now)
        slot = schedule.slot_at(datetime.fromtimestamp(now, timezone.utc))
        prof = self.cfg["perfiles"][self.cfg["perfil"]]
        rs = e.risk.s
        lead = max(self.learner.snapshot(), key=lambda a: (a["modo"] == "vivo", a["p_pos"]), default=None)

        def pos_view(p):
            if not p:
                return None
            q = e.quotes.get(p["instrumento"])
            px = (q[0] if p["dir"] > 0 else q[1]) if q else p["entry"]
            rules = e.rules.get(p["instrumento"])
            vpp = rules.value_per_point if rules else 1.0
            return {**{k: p.get(k) for k in ("deal_id", "arm", "instrumento", "dir", "size", "entry", "stop", "stop0",
                                              "tp", "atr", "opened", "shadow", "risk_usd", "moves", "spread_in", "slip_in")},
                    "precio": px, "upl": p["dir"] * (px - p["entry"]) * p["size"] * vpp,
                    "r_actual": p["dir"] * (px - p["entry"]) / abs(p["entry"] - p["stop0"]) if p["entry"] != p["stop0"] else 0,
                    "stops": e.stop_hist.get(p["deal_id"]) or [(r["ts"], r["new"], r["razon"]) for r in self.store.q(
                        "SELECT ts,new,razon FROM stop_moves WHERE deal_id=? ORDER BY id", (p["deal_id"],))]}

        chart = [{"t": b[0], "c": b[4]} for b in e.bars[main_inst].m1] if main_inst in e.bars else []
        eq = self.store.q("SELECT ts,balance,upl FROM equity ORDER BY ts DESC LIMIT 2000")[::-1]
        step = max(1, len(eq) // 300)
        trades_live = self.store.trades(shadow=False)
        cum, curve = 0.0, []
        for t in trades_live:
            cum += t["pnl"] or 0
            curve.append({"t": t["closed"], "pnl": cum})
        info_main = self.info.readings(main_inst) if main_inst in e.bars else {}
        return {
            "demo": True, "ahora": now, "hora_cdmx": schedule.cdmx_str(datetime.fromtimestamp(now, timezone.utc)),
            "estado": e.status, "pausado": e.paused, "perfil": self.cfg["perfil"], "franja": slot,
            "activos_franja": schedule.DEFAULT_ROTATION.get(slot, []), "codigo_telegram": self.code,
            "stream": getattr(getattr(e, "stream", None), "connected", None), "uptime": time.time() - e.started,
            "cuenta": {"balance": e.account.get("balance"), "no_realizado": e.account.get("upl"),
                       "disponible": e.account.get("available"), "inicial": e.start_balance},
            "riesgo": {"pct": e.risk.risk_pct(), "dia_R": rs.day_r, "semana_R": rs.week_r, "racha": rs.streak,
                       "pausa_hasta": rs.pause_until, "dia_detenido": rs.halted_day, "medio_tamano": rs.half_size,
                       "trades_vivos": rs.live_trades, "perfil": prof},
            "conteos": {"setups": cnt.get("SETUP", 0), "killed": cnt.get("KILL", 0), "scores": cnt.get("SCORE", 0),
                        "entradas": cnt.get("ENTER", 0), "moves": cnt.get("MOVE", 0), "salidas": cnt.get("EXIT", 0),
                        "lineas": self.log.line_no},
            "ultimo_move": last_move[0] if last_move else None,
            "flujo": list(e.flow), "filtro": e.last_filter, "score": e.last_score,
            "posiciones": [pos_view(p) for p in live], "sombras": [pos_view(p) for p in shadow],
            "grafica": {"inst": main_inst, "velas": chart},
            "equity": [{"t": r["ts"], "b": r["balance"], "u": r["upl"]} for r in eq[::step]],
            "pnl_acumulado": curve[-300:],
            "stats": {"dia": rep["dia"], "acumulado": rep["acumulado"], "sombra": rep["sombra"]},
            "vs_backtest": rep["vs_backtest"],
            "learner": self.learner.snapshot(), "learner_cambios": self.learner.changes(6),
            "learner_lider": lead,
            "lectura": {"inst": main_inst, "agentes": info_main, "eventos": self.info.next_events(4)},
            "stop_politica": {a["key"]: a["policy_name"] for a in e.arms},
            "log": self.log.tail(40),
            "errores": [x for x in self.log.tail(200) if x["nivel"] == "error"][-5:],
            "instrumentos": {i: {"bid": q[0], "ask": q[1], "spread": q[1] - q[0], "edad": now - q[2]}
                             for i, q in e.quotes.items()},
        }

    async def start(self, port):
        runner = web.AppRunner(self.app, access_log=None)
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", port).start()
        self.log("WEB", "-", f"dashboard en el puerto {port}")
