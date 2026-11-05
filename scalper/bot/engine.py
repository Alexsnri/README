"""Trading flow with hard handoffs, each agent with a single job:

  Scout -> Filter -> Analyst -> Risk -> Executor        (entries, at each 5-minute close)
  Stop Manager                                          (at each 1-minute close and each tick of the stream)
  Reconciliation                                        (every 10 s: is the stop really on the server?)
  Logger                                                (everything to file + SQLite + dashboard)

"Shadow" arms go through the same flow but the Executor fills them in paper with the live bid/ask.
"""
import asyncio
import math
import statistics
import time
from collections import deque
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from . import analyst, filters, schedule
from . import strategies as S
from .capital import ApiError
from .config import profile
from .instruments import INSTRUMENTS
from .risk import DealingRules, RiskManager, RiskState, floor_step, position_size
from .stops import update_stop

MAX_BARS5 = 12 * 24 * 30


class Bars:
    """Builds 1m and 5m bars (mid) from the quotes."""

    def __init__(self, inst):
        self.inst = inst
        self.b5 = deque(maxlen=MAX_BARS5)   # (t_start, o, h, l, c)
        self.cur1 = None
        self.cur5 = None
        self.m1 = deque(maxlen=240)         # last 4 h of 1m bars (dashboard chart)

    def seed(self, rows):
        for r in rows:
            self.b5.append((int(r["t"]), r["o"], r["h"], r["l"], r["c"]))

    def update(self, ts, mid):
        """Returns (closed_1m, closed_5m) if this quote closed a bar."""
        closed1 = closed5 = None
        t1 = int(ts // 60 * 60)
        t5 = int(ts // 300 * 300)
        if self.cur1 and t1 != self.cur1[0]:
            closed1 = tuple(self.cur1)
            self.m1.append(closed1)
            self.cur1 = None
        if self.cur5 and t5 != self.cur5[0]:
            closed5 = tuple(self.cur5)
            if not self.b5 or self.b5[-1][0] < closed5[0]:
                self.b5.append(closed5)
            self.cur5 = None
        for cur_name, t in (("cur1", t1), ("cur5", t5)):
            cur = getattr(self, cur_name)
            if cur is None:
                setattr(self, cur_name, [t, mid, mid, mid, mid])
            else:
                cur[2] = max(cur[2], mid)
                cur[3] = min(cur[3], mid)
                cur[4] = mid
        return closed1, closed5

    def df5(self):
        if not self.b5:
            return pd.DataFrame(columns=list("ohlc"))
        a = np.array(self.b5, dtype=float)
        idx = pd.to_datetime(a[:, 0].astype("int64"), unit="s", utc=True)
        return pd.DataFrame(a[:, 1:], index=idx, columns=["o", "h", "l", "c"])


class Engine:
    def __init__(self, cfg, store, log, hub, broker, info, learner, notify=None):
        self.cfg, self.store, self.log, self.hub, self.br = cfg, store, log, hub, broker
        self.info, self.learner = info, learner
        self.notify = notify or (lambda *a, **k: None)
        self.now = getattr(broker, "now", time.time)
        self.arms = []
        for a in cfg["brazos"]:
            cls = S.BY_CODE[a["estrategia"]]
            st = cls(**a.get("params", {}))
            self.arms.append({"key": f"{a['estrategia']}-{a['instrumento']}", "inst": a["instrumento"], "strat": st,
                              "policy": cfg["stop_manager"]["politicas"][a.get("politica_stop", "fijo")],
                              "policy_name": a.get("politica_stop", "fijo")})
        self.instruments = sorted({a["inst"] for a in self.arms} | {"US500", "US100"})
        self.bars = {i: Bars(i) for i in self.instruments}
        self.quotes = {}          # inst -> (bid, ask, ts)
        self.spreads = {i: deque(maxlen=3000) for i in self.instruments}
        self.rules = {}
        self.decimals = {}
        self.positions = {p["deal_id"]: p for p in store.positions()}
        rs = store.kv_get("risk_state")
        self.risk = RiskManager(profile(cfg), RiskState(**rs) if rs else None)
        self.paused = bool(store.kv_get("paused", False))
        self.account = {"balance": None, "upl": None, "available": None}
        self.start_balance = store.kv_get("start_balance")
        self.flow = deque(maxlen=12)
        self.last_filter = None
        self.last_score = None
        self.stop_hist = {}       # deal_id -> [(ts, level, reason)]
        self.status = "arrancando"
        self.errors = deque(maxlen=20)
        self.started = time.time()
        self.last_slot = None
        self._shadow_seq = int(store.kv_get("shadow_seq", 0))

    # ================================================================ startup
    async def startup(self):
        self.log("INICIO", "-", f"DEMO · perfil {self.cfg['perfil']} · brazos vivos: "
                 + ", ".join(a["key"] for a in self.arms if self.learner.modes.get(a["key"]) == "vivo"))
        await self.br.login()
        await self.refresh_account()
        await self._demo_balance()
        for inst in self.instruments:
            await self._load_rules(inst)
            await self._backfill(inst)
        await self.reconcile(first=True)
        self.status = "operando" if not self.paused else "pausado"

    async def _demo_balance(self):
        target = self.cfg.get("demo", {}).get("saldo_inicial")
        if not target or self.store.kv_get("demo_ajustada"):
            if self.start_balance is None and self.account["balance"] is not None:
                self.start_balance = self.account["balance"]
                self.store.kv_set("start_balance", self.start_balance)
            return
        bal = self.account["balance"]
        if bal is not None and abs(bal - target) > 0.01 and not self.store.trades():
            try:
                await self.br.top_up(round(target - bal, 2))
                self.log("CUENTA", "-", f"demo ajustada de ${bal:,.2f} a ${target:,.2f}")
                await self.refresh_account()
            except ApiError as e:
                self.log("ERROR", "-", f"no pude ajustar la demo a ${target} ({e}); ajústala en la app de "
                         "Capital.com → Demo → Saldo. Sigo con el saldo actual.", "error")
        self.store.kv_set("demo_ajustada", True)
        self.start_balance = self.account["balance"]
        self.store.kv_set("start_balance", self.start_balance)

    async def _load_rules(self, inst):
        epic = INSTRUMENTS[inst].epic
        try:
            m = await self.br.market(epic)
        except ApiError as e:
            self.log("ERROR", inst, f"no pude leer reglas de {epic}: {e}", "error")
            m = {}
        dr = m.get("dealingRules", {})
        ins = m.get("instrument", {})
        snap = m.get("snapshot", {})
        price = snap.get("bid") or 1.0

        def dist(rule):
            if not rule:
                return 0.0
            v = float(rule.get("value", 0))
            return v / 100 * price if rule.get("unit") == "PERCENTAGE" else v

        mf = ins.get("marginFactor")
        mf = (mf / 100 if ins.get("marginFactorUnit", "PERCENTAGE") == "PERCENTAGE" else mf) if mf else 0.05
        self.rules[inst] = DealingRules(
            min_size=float(dr.get("minDealSize", {}).get("value", 0.01)),
            step=float(dr.get("minSizeIncrement", {}).get("value", dr.get("minDealSize", {}).get("value", 0.01))),
            max_size=float(dr.get("maxDealSize", {}).get("value", 1e9)),
            min_stop_dist=dist(dr.get("minStopOrProfitDistance")),
            margin_factor=float(mf),
            value_per_point=float(ins.get("lotSize") or 1.0))
        self.decimals[inst] = int(round(math.log10(snap.get("decimalPlacesFactor", 100)))) if snap else 2
        r = self.rules[inst]
        self.log("REGLAS", inst, f"mín {r.min_size} paso {r.step} stop mín {r.min_stop_dist:g} margen "
                 f"{r.margin_factor * 100:.1f}%")

    async def _backfill(self, inst):
        """5m history from the API (25 days, in chunks of 1000 bars) + what is saved in SQLite."""
        saved = self.store.bars(inst, since_t=self.now() - 30 * 86400)
        have = {r["t"] for r in saved}
        epic = INSTRUMENTS[inst].epic
        end = datetime.fromtimestamp(self.now(), timezone.utc)
        start = end - timedelta(days=25)
        rows = []
        t = start
        while t < end:
            t2 = min(end, t + timedelta(days=3))
            try:
                ps = await self.br.prices(epic, "MINUTE_5", t.strftime("%Y-%m-%dT%H:%M:%S"),
                                          t2.strftime("%Y-%m-%dT%H:%M:%S"))
            except ApiError as e:
                self.log("ERROR", inst, f"historial: {e}", "error")
                ps = []
            for p in ps:
                ts = pd.Timestamp(p["snapshotTimeUTC"], tz="UTC").timestamp()
                if int(ts) in have:
                    continue
                mid = lambda k: (p[k]["bid"] + p[k]["ask"]) / 2
                rows.append({"t": int(ts), "o": mid("openPrice"), "h": mid("highPrice"), "l": mid("lowPrice"),
                             "c": mid("closePrice")})
            t = t2
        for r in rows:
            self.store.add_bar(inst, r["t"], r["o"], r["h"], r["l"], r["c"])
        allrows = sorted(saved + rows, key=lambda r: r["t"])
        self.bars[inst].seed(allrows)
        self.log("DATOS", inst, f"{len(allrows)} velas de 5m cargadas")

    # ================================================================ quotes
    async def on_quote(self, epic, bid, ask, ts):
        inst = next((i for i in self.instruments if INSTRUMENTS[i].epic == epic), None)
        if not inst:
            return
        self.quotes[inst] = (bid, ask, ts)
        self.spreads[inst].append(ask - bid)
        if int(ts) % 60 == 0 or len(self.spreads[inst]) % 50 == 0:
            self.store.x("INSERT INTO spreads VALUES(?,?,?,?)", (ts, inst, bid, ask))
        await self._shadow_ticks(inst, bid, ask, ts)
        c1, c5 = self.bars[inst].update(ts, (bid + ask) / 2)
        if c1:
            await self.on_1m(inst, c1)
        if c5:
            self.store.add_bar(inst, *c5)
            await self.on_5m(inst, c5)
        self.hub.publish("quote", {"inst": inst, "bid": bid, "ask": ask, "ts": ts})

    # ================================================================ Stop Manager
    async def on_1m(self, inst, bar):
        bid, ask, _ = self.quotes[inst]
        for p in [p for p in self.positions.values() if p["instrumento"] == inst]:
            d = p["dir"]
            if schedule.must_flatten(datetime.fromtimestamp(self.now(), timezone.utc), inst, INSTRUMENTS[inst].family):
                await self.close(p, "cierre por horario")
                continue
            close_side = bid if d > 0 else ask
            if d * (close_side - p["best"]) > 0:
                p["best"] = close_side
            arm = self._arm(p["arm"])
            pol = arm["policy"] if arm else self.cfg["stop_manager"]["politicas"]["fijo"]
            spread = ask - bid
            new = update_stop(d, p["entry"], p["stop"], p["best"], p["atr"], pol["be_trig"], 0.6 * spread,
                              pol["trail_mult"], pol["trail_start"])
            if d * (new - p["stop"]) > self.cfg["stop_manager"]["paso_minimo_atr"] * p["atr"]:
                reason = "break-even + costos" if abs(new - (p["entry"] + d * 0.6 * spread)) < 1e-9 else "trailing"
                await self.move_stop(p, new, reason)
            if p["deal_id"] in self.positions:
                self.store.save_position(p)

    async def move_stop(self, p, new, reason):
        """The stop only moves in favor. Every move is sent to Capital.com (server-side stop) and confirmed."""
        d = p["dir"]
        if d * (new - p["stop"]) <= 0:
            return False
        new = round(new, self.decimals.get(p["instrumento"], 2))
        old = p["stop"]
        ok = True
        if not p["shadow"]:
            try:
                await self.br.update_position(p["deal_id"], new, p.get("tp"))
                srv = await self._server_position(p["deal_id"])
                ok = srv is not None and abs(float(srv["position"].get("stopLevel") or 0) - new) < 10 ** -self.decimals.get(p["instrumento"], 2) * 2
            except ApiError as e:
                self.log("ERROR", p["instrumento"], f"no pude mover el stop: {e}", "error")
                return False
        p["stop"] = new
        p["moves"] = p.get("moves", 0) + 1
        self.stop_hist.setdefault(p["deal_id"], []).append((self.now(), new, reason))
        self.store.x("INSERT INTO stop_moves(deal_id,ts,old,new,razon,confirmado) VALUES(?,?,?,?,?,?)",
                     (p["deal_id"], self.now(), old, new, reason, int(ok)))
        tag = " (sombra)" if p["shadow"] else ("" if ok else " (SIN CONFIRMAR)")
        self.log("MOVE", p["instrumento"], f"stop → {new:g} ({reason}){tag}")
        self.store.save_position(p)
        return ok

    # ================================================================ Scout (5m close)
    async def on_5m(self, inst, bar):
        df = self.bars[inst].df5()
        if len(df) < 300:
            return
        for arm in [a for a in self.arms if a["inst"] == inst]:
            try:
                sig = arm["strat"].signals(df, INSTRUMENTS[inst].family)
            except Exception as e:  # a strategy failure must not stop the others
                self.log("ERROR", inst, f"{arm['key']}: {type(e).__name__}: {e}", "error")
                continue
            last = sig.iloc[-1]
            pos = next((p for p in self.positions.values() if p["arm"] == arm["key"]), None)
            if pos:
                pos["bars_held"] = pos.get("bars_held", 0) + 1
                if (pos["dir"] > 0 and last["exit_long"]) or (pos["dir"] < 0 and last["exit_short"]):
                    await self.close(pos, "salida de la estrategia")
                elif pos["bars_held"] >= pos.get("max_bars", 10_000):
                    await self.close(pos, "tiempo")
                continue
            if int(last["entry"]) != 0 and np.isfinite(last["stop_dist"]):
                await self.pipeline(arm, int(last["entry"]), float(last["stop_dist"]),
                                    float(last["tp_dist"]) if np.isfinite(last["tp_dist"]) else None,
                                    int(last["max_bars"]), df)

    async def pipeline(self, arm, direction, stop_dist, tp_dist, max_bars, df):
        inst = arm["inst"]
        shadow = self.learner.modes.get(arm["key"]) != "vivo" or self.paused
        now = self.now()
        ts = datetime.fromtimestamp(now, timezone.utc)
        side = "COMPRA" if direction > 0 else "VENTA"
        item = {"ts": now, "inst": inst, "arm": arm["key"], "dir": direction, "etapa": "scout", "resultado": "",
                "sombra": shadow}
        self.flow.appendleft(item)
        self.log("SETUP", inst, f"{arm['key']} {side}" + (" (sombra)" if shadow else ""))
        q = self.quotes.get(inst)
        if not q:
            item["resultado"] = "sin precio"
            return
        bid, ask, qts = q
        from . import indicators as ind
        atr_s = ind.atr(df)
        atr = float(atr_s.iloc[-1])
        hist = atr_s.iloc[-12 * 24 * 20:]
        pct = float((hist < atr).mean() * 100)
        typ = statistics.median(self.spreads[inst]) if len(self.spreads[inst]) > 100 else \
            INSTRUMENTS[inst].spread_bps / 1e4 * (bid + ask) / 2
        su = filters.Setup(inst, arm["key"], direction, now, ask - bid, atr, pct, typ,
                           has_position=any((p["arm"] == arm["key"]) if shadow else
                                            (p["instrumento"] == inst and not p["shadow"])
                                            for p in self.positions.values()),
                           session_ok=schedule.can_enter(ts, inst), news_block=self.info.news_block(inst, now),
                           market_open=(now - qts) < 120, quote_age=now - qts)
        ok, rules = filters.evaluate(su, self.cfg["filtro"])
        self.last_filter = {"inst": inst, "arm": arm["key"], "dir": direction, "ok": ok,
                            "reglas": [{"regla": r, "ok": o, "valor": v} for r, o, v in rules], "ts": now}
        item["etapa"] = "filter"
        if not ok:
            bad = next(r for r in rules if not r[1])
            item["resultado"] = f"descartado: {bad[0]}"
            self.log("KILL", inst, f"{bad[0]} ({bad[2]})")
            return
        a = self.learner.arms.get(arm["key"])
        readings = self.info.readings(inst)
        sc, parts = analyst.score(su, arm_validated=True, learner_p=a.p_positive if a else 0.5,
                                  info_readings=readings, cfg=self.cfg["analyst"])
        self.last_score = {"inst": inst, "arm": arm["key"], "score": sc, "umbral": self.cfg["analyst"]["umbral"],
                           "partes": parts, "ts": now, "dir": direction}
        item["etapa"] = "analyst"
        self.log("SCORE", inst, f"{arm['key']} {sc} " + ("→ executor" if sc >= self.cfg['analyst']['umbral']
                                                       else f"< {self.cfg['analyst']['umbral']}"))
        if sc < self.cfg["analyst"]["umbral"]:
            item["resultado"] = f"score {sc} bajo"
            return
        # ---- Risk
        rules_i = self.rules.get(inst, DealingRules())
        stop_dist = max(stop_dist, rules_i.min_stop_dist * 1.05)
        ref = ask if direction > 0 else bid
        equity = self.account["balance"] or self.start_balance or 100.0
        mult = self.learner.mult.get(arm["key"], 1.0)
        pct = self.risk.risk_pct(schedule.risk_multiplier(ts), mult)
        size, risk_usd, why = position_size(equity, pct, stop_dist, rules_i, slip=0.5 * (ask - bid))
        item["etapa"] = "risk"
        if size <= 0:
            item["resultado"] = why
            self.log("KILL", inst, f"risk: {why}")
            return
        live_pos = [p for p in self.positions.values() if p["shadow"] == shadow]
        margin = size * ref * rules_i.value_per_point * rules_i.margin_factor
        if shadow:
            ok_r, why_r = (not any(p["arm"] == arm["key"] for p in live_pos), "posición sombra abierta")
        else:
            ok_r, why_r = self.risk.check(now, equity, live_pos, risk_usd, inst, margin,
                                          self.account.get("available"))
        if not ok_r:
            item["resultado"] = why_r
            self.log("KILL", inst, f"risk: {why_r}")
            return
        item["etapa"] = "executor"
        await self.open(arm, inst, direction, size, ref, stop_dist, tp_dist, atr, max_bars, risk_usd, ask - bid,
                        shadow, item, pct)

    # ================================================================ Executor
    async def open(self, arm, inst, direction, size, ref, stop_dist, tp_dist, atr, max_bars, risk_usd, spread,
                   shadow, item, pct):
        dec = self.decimals.get(inst, 2)
        stop = round(ref - direction * stop_dist, dec)
        tp = round(ref + direction * tp_dist, dec) if tp_dist else None
        side = "COMPRA" if direction > 0 else "VENTA"
        if shadow:
            self._shadow_seq += 1
            self.store.kv_set("shadow_seq", self._shadow_seq)
            deal, level = f"sombra-{self._shadow_seq}", ref
        else:
            try:
                r = await self.br.open_position(INSTRUMENTS[inst].epic, direction, size, stop, tp)
                conf = await self.br.confirm(r.get("dealReference", ""))
            except ApiError as e:
                item["resultado"] = f"error: {e}"
                self.log("ERROR", inst, f"orden rechazada: {e}", "error")
                await self.reconcile()   # in case it was executed anyway
                return
            if conf.get("dealStatus") != "ACCEPTED":
                item["resultado"] = f"rechazada: {conf.get('reason', 'sin confirmación')}"
                self.log("ERROR", inst, f"orden no aceptada: {conf.get('reason', conf.get('dealStatus', '?'))}", "error")
                await self.reconcile()
                return
            deals = conf.get("affectedDeals") or [{}]
            deal = deals[0].get("dealId") or conf.get("dealId")
            level = float(conf.get("level") or ref)
        slip = direction * (level - ref)
        p = {"deal_id": deal, "arm": arm["key"], "instrumento": inst, "dir": direction, "size": size, "entry": level,
             "stop": stop, "stop0": stop, "tp": tp, "atr": atr, "opened": self.now(),
             "best": level - direction * spread, "shadow": int(shadow), "risk_usd": risk_usd, "ref": ref,
             "spread_in": spread, "slip_in": slip, "max_bars": max_bars, "bars_held": 0, "moves": 0,
             "risk_pct": pct}
        self.positions[deal] = p
        self.stop_hist[deal] = [(self.now(), stop, "stop inicial")]
        self.store.save_position(p)
        item["resultado"] = "abierta" + (" (sombra)" if shadow else "")
        tag = " (sombra)" if shadow else ""
        self.log("ENTER", inst, f"{side} {size:g} @ {level:g} · stop {stop:g}" + (f" · tp {tp:g}" if tp else "")
                 + f" · riesgo ${risk_usd:.2f} ({pct:.2f}%) · spread {spread:g} · slip {slip:+g}{tag}")
        self.log("STOP", inst, f"stop {stop:g} puesto en el servidor antes de entrar" if not shadow
                 else f"stop {stop:g} (sombra)")

    async def close(self, p, reason):
        if p["deal_id"] not in self.positions:
            return
        inst = p["instrumento"]
        bid, ask, _ = self.quotes.get(inst, (p["entry"], p["entry"], 0))
        level = bid if p["dir"] > 0 else ask
        if not p["shadow"]:
            try:
                r = await self.br.close_position(p["deal_id"])
                conf = await self.br.confirm(r.get("dealReference", ""))
                level = float(conf.get("level") or level)
            except ApiError as e:
                if e.status == 404:   # it was already closed (stop/TP): reconciliation records it
                    await self.reconcile()
                    return
                self.log("ERROR", inst, f"no pude cerrar: {e}", "error")
                return
        await self._record_close(p, level, reason)

    async def _record_close(self, p, level, reason):
        d = p["dir"]
        r_mult = d * (level - p["entry"]) / abs(p["entry"] - p["stop0"]) if p["entry"] != p["stop0"] else 0.0
        rules_i = self.rules.get(p["instrumento"], DealingRules())
        pnl = d * (level - p["entry"]) * p["size"] * rules_i.value_per_point
        costs = (p.get("spread_in", 0) + max(0.0, -p.get("slip_in", 0))) * p["size"] * rules_i.value_per_point
        t = {"deal_id": p["deal_id"], "arm": p["arm"], "instrumento": p["instrumento"], "dir": d, "size": p["size"],
             "entry": p["entry"], "exit": level, "stop0": p["stop0"], "opened": p["opened"], "closed": self.now(),
             "pnl": pnl, "r": r_mult, "motivo": reason, "spread_in": p.get("spread_in"), "slip_in": p.get("slip_in"),
             "costos": costs, "shadow": p["shadow"], "moves": p.get("moves", 0)}
        self.store.add_trade(t)
        self.positions.pop(p["deal_id"], None)
        self.store.drop_position(p["deal_id"])
        kind = "WIN" if pnl > 0 else ("CERO" if abs(r_mult) < 0.05 else "LOSS")
        tag = " (sombra)" if p["shadow"] else ""
        self.log("EXIT", p["instrumento"], f"{kind} {pnl:+.2f} USD ({r_mult:+.2f}R) · {reason}{tag}")
        self.learner.on_trade(p["arm"], r_mult)
        for ev in self.risk.on_close(self.now(), r_mult, shadow=bool(p["shadow"])):
            self.log("BREAK", p["instrumento"], ev, "warn")
            self.notify(f"⚠️ {ev}")
        self.store.kv_set("risk_state", self.risk.s.__dict__)
        if not p["shadow"]:
            await self.refresh_account()
            bal = self.account.get("balance")
            self.notify(f"{'✅' if pnl > 0 else '❌'} {p['instrumento']} {kind} {pnl:+.2f} USD ({r_mult:+.2f}R) · "
                        f"{reason}" + (f"\nBalance Capital.com: ${bal:,.2f}" if bal is not None else ""))

    async def _shadow_ticks(self, inst, bid, ask, ts):
        """Shadow positions: the stop/TP is simulated with the live bid/ask (worst case, like the backtest)."""
        for p in [p for p in self.positions.values() if p["shadow"] and p["instrumento"] == inst]:
            px = bid if p["dir"] > 0 else ask
            if p["dir"] * (px - p["stop"]) <= 0:
                await self._record_close(p, p["stop"] - p["dir"] * 0.5 * (ask - bid), "stop")
            elif p.get("tp") and p["dir"] * (px - p["tp"]) >= 0:
                await self._record_close(p, p["tp"], "objetivo")

    # ================================================================ Reconciliation
    async def _server_position(self, deal_id):
        for sp in await self.br.positions():
            if sp["position"]["dealId"] == deal_id:
                return sp
        return None

    async def reconcile(self, first=False):
        """Compares our positions against Capital.com's. If the stop is missing, it puts it back first (protect)."""
        try:
            server = {sp["position"]["dealId"]: sp for sp in await self.br.positions()}
        except ApiError as e:
            self.log("ERROR", "-", f"no pude leer posiciones: {e}", "error")
            return
        for deal, p in list(self.positions.items()):
            if p["shadow"]:
                continue
            sp = server.get(deal)
            if sp is None:
                level, why = await self._closing_info(deal, p)
                await self._record_close(p, level, why)
                continue
            srv_stop = sp["position"].get("stopLevel")
            if not srv_stop:
                self.log("ERROR", p["instrumento"], "¡posición sin stop en el servidor! lo vuelvo a poner", "error")
                try:
                    await self.br.update_position(deal, p["stop"], p.get("tp"))
                except ApiError as e:
                    self.log("ERROR", p["instrumento"], f"no pude reponer el stop: {e}", "error")
        known = set(self.positions)
        for deal, sp in server.items():
            if deal in known:
                continue
            pos, mkt = sp["position"], sp.get("market", {})
            inst = next((i for i in INSTRUMENTS if INSTRUMENTS[i].epic == mkt.get("epic")), mkt.get("epic", "?"))
            d = 1 if pos.get("direction") == "BUY" else -1
            lvl = float(pos["level"])
            stop = pos.get("stopLevel")
            if not stop:
                df = self.bars[inst].df5() if inst in self.bars else None
                from . import indicators as ind
                atr = float(ind.atr(df).iloc[-1]) if df is not None and len(df) > 20 else lvl * 0.002
                stop = round(lvl - d * 2 * atr, self.decimals.get(inst, 2))
                try:
                    await self.br.update_position(deal, stop, pos.get("profitLevel"))
                    self.log("STOP", inst, f"posición sin stop: puse stop {stop:g}", "warn")
                except ApiError as e:
                    self.log("ERROR", inst, f"posición sin stop y no pude ponerlo: {e}", "error")
            p = {"deal_id": deal, "arm": "manual", "instrumento": inst, "dir": d, "size": float(pos["size"]),
                 "entry": lvl, "stop": float(stop), "stop0": float(stop), "tp": pos.get("profitLevel"),
                 "atr": abs(lvl - float(stop)) / 2, "opened": self.now(), "best": lvl, "shadow": 0,
                 "risk_usd": abs(lvl - float(stop)) * float(pos["size"]), "spread_in": 0, "slip_in": 0, "moves": 0}
            self.positions[deal] = p
            self.store.save_position(p)
            self.log("ADOPT", inst, f"posición del servidor adoptada {deal} (stop {float(stop):g})", "warn")
        if first:
            n = sum(1 for p in self.positions.values() if not p["shadow"])
            self.log("RECON", "-", f"{n} posiciones vivas verificadas con el servidor")

    async def _closing_info(self, deal, p):
        try:
            acts = await self.br.activity(last_period=86400, deal_id=deal)
        except ApiError:
            acts = []
        for a in acts:
            src = a.get("source")
            lvl = a.get("level") or (a.get("details") or {}).get("level")
            if lvl and a.get("status", "ACCEPTED") in ("ACCEPTED", "EXECUTED"):
                why = {"SL": "stop en servidor", "TP": "objetivo en servidor", "CLOSE_OUT": "cierre por margen",
                       "USER": "cerrada a mano", "DEALER": "cerrada por el bróker", "SYSTEM": "sistema"}.get(src, src)
                return float(lvl), why
        bid, ask, _ = self.quotes.get(p["instrumento"], (p["stop"], p["stop"], 0))
        return (p["stop"] if p["stop"] else (bid if p["dir"] > 0 else ask)), "cerrada en el servidor (sin detalle)"

    async def refresh_account(self):
        try:
            b = await self.br.balance()
            if b:
                self.account.update(b)
                self.store.x("INSERT INTO equity VALUES(?,?,?)", (self.now(), b.get("balance"), b.get("upl")))
        except ApiError as e:
            self.log("ERROR", "-", f"balance: {e}", "error")

    def _arm(self, key):
        return next((a for a in self.arms if a["key"] == key), None)

    # ================================================================ periodic loops
    async def loop_reconcile(self):
        while True:
            await asyncio.sleep(10)
            await self.reconcile()

    async def loop_account(self):
        while True:
            await self.refresh_account()
            self.hub.publish("state", self.snapshot_light())
            await asyncio.sleep(30)

    async def loop_keepalive(self):
        while True:
            await asyncio.sleep(240)
            try:
                await self.br.ping()
            except ApiError as e:
                self.log("ERROR", "-", f"ping: {e}; renuevo sesión", "error")
                try:
                    await self.br.login()
                except ApiError:
                    pass

    async def tick_schedule(self):
        """Scheduler: slot changes, mandatory closes and stale positions (also without quotes)."""
        now = datetime.fromtimestamp(self.now(), timezone.utc)
        slot = schedule.slot_at(now)
        if slot != self.last_slot:
            active = schedule.DEFAULT_ROTATION.get(slot, [])
            self.log("SLOT", "-", f"{slot}: " + (", ".join(active) if active else "sin entradas nuevas"))
            self.last_slot = slot
        for p in list(self.positions.values()):
            if schedule.must_flatten(now, p["instrumento"], INSTRUMENTS.get(p["instrumento"], INSTRUMENTS["US100"]).family):
                await self.close(p, "cierre por horario")

    def snapshot_light(self):
        return {"account": self.account, "status": self.status, "paused": self.paused}
