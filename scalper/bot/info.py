"""Information agents. Each one gives a "reading" per instrument for the dashboard and for the Analyst.

The weight of each agent comes from config.yaml and was decided with the out-of-sample backtest
(lab/info_agents.py). Today they all weigh 0 in the score; News also acts as a hard block (protection).
"""
import asyncio
import json
import os
import time
from datetime import datetime, timedelta, timezone

import httpx
import numpy as np

from . import indicators as ind
from .instruments import INSTRUMENTS
from .schedule import NY

HERE = os.path.dirname(os.path.abspath(__file__))
FF_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
COT_URL = ("https://publicreporting.cftc.gov/resource/gpe5-46if.json?$where=market_and_exchange_names%20like%20"
           "'{m}%25'&$limit=3&$order=report_date_as_yyyy_mm_dd%20DESC")
COT_MARKETS = {"US100": "NASDAQ MINI", "US500": "E-MINI S%26P 500 -"}
NEWS_CCY = {"index": {"USD"}, "metal": {"USD"}, "crypto": {"USD"}, "fx": {"USD"}}
FX_CCY = {"EURUSD": {"EUR"}, "GBPUSD": {"GBP"}}


class Info:
    def __init__(self, cfg, engine_ref, broker, log, store):
        self.cfg = cfg["agentes_info"]
        self.eng = engine_ref           # lambda: engine (for its bars)
        self.br, self.log, self.store = broker, log, store
        self.events = []                # [(ts, ccy, title, impact)]
        self.fomc = set(json.load(open(os.path.join(HERE, "data", "fomc.json")))["decision_14h_ny"])
        self.cot = {}
        self.sentiment = {}
        self.funding = {}
        self.http = httpx.AsyncClient(timeout=20)
        self.last_news = 0

    # ---------------------------------------------------------------- News
    async def refresh_news(self):
        try:
            r = await self.http.get(FF_URL, headers={"User-Agent": "scalper-demo-bot"})
            evs = []
            for e in r.json():
                if e.get("impact") != "High":
                    continue
                ts = datetime.fromisoformat(e["date"]).timestamp()
                evs.append((ts, e.get("country"), e.get("title"), e.get("impact")))
            self.events = evs
            self.last_news = time.time()
            self.store.kv_set("news_cache", evs)
        except Exception as e:
            self.events = self.events or self.store.kv_get("news_cache", [])
            self.log("ERROR", "-", f"calendario: {type(e).__name__} (uso el último guardado)", "error")

    def news_block(self, inst, now):
        c = self.cfg["news"]
        if not c.get("activo") or not c.get("bloqueo"):
            return ""
        fam = INSTRUMENTS[inst].family
        ccys = NEWS_CCY.get(fam, {"USD"}) | FX_CCY.get(inst, set())
        for ts, ccy, title, _ in self.events:
            if ccy in ccys and ts - c["antes_min"] * 60 <= now <= ts + c["despues_min"] * 60:
                return f"{ccy} {title} {datetime.fromtimestamp(ts, NY):%H:%M} NY"
        ny = datetime.fromtimestamp(now, timezone.utc).astimezone(NY)
        if ny.date().isoformat() in self.fomc:
            t = ny.replace(hour=14, minute=0, second=0, microsecond=0)
            if t - timedelta(minutes=c["fomc_antes_min"]) <= ny <= t + timedelta(minutes=c["fomc_despues_min"]):
                return "FOMC 14:00 NY"
        return ""

    def next_events(self, n=4):
        now = time.time()
        fut = sorted(e for e in self.events if e[0] > now - 900)[:n]
        return [{"hora_ny": datetime.fromtimestamp(t, NY).strftime("%a %H:%M"), "moneda": c, "evento": ti}
                for t, c, ti, _ in fut]

    # ---------------------------------------------------------------- Big Money
    async def refresh_cot(self):
        for inst, m in COT_MARKETS.items():
            try:
                rows = (await self.http.get(COT_URL.format(m=m.replace(" ", "%20")))).json()
                if len(rows) >= 2:
                    net = [float(r["asset_mgr_positions_long"]) - float(r["asset_mgr_positions_short"]) for r in rows[:2]]
                    self.cot[inst] = {"fecha": rows[0]["report_date_as_yyyy_mm_dd"][:10], "neto": net[0],
                                      "cambio": net[0] - net[1]}
            except Exception as e:
                self.log("ERROR", inst, f"COT: {type(e).__name__}", "error")
        try:
            r = (await self.http.get("https://www.okx.com/api/v5/public/funding-rate?instId=BTC-USDT-SWAP")).json()
            self.funding["BTCUSD"] = float(r["data"][0]["fundingRate"])
        except Exception:
            pass

    # ---------------------------------------------------------------- Retail
    async def refresh_sentiment(self, instruments):
        try:
            rows = await self.br.sentiment([INSTRUMENTS[i].epic for i in instruments])
            for r in rows:
                inst = next((i for i in instruments if INSTRUMENTS[i].epic == r.get("marketId")), None)
                if inst:
                    self.sentiment[inst] = float(r.get("longPositionPercentage", 50))
                    self.store.x("INSERT INTO sentiment VALUES(?,?,?)", (time.time(), inst, self.sentiment[inst]))
        except Exception as e:
            self.log("ERROR", "-", f"sentimiento: {type(e).__name__}", "error")

    # ---------------------------------------------------------------- readings
    def readings(self, inst):
        eng = self.eng()
        out = {}
        df = eng.bars[inst].df5() if inst in eng.bars else None
        # Trend: alignment 5m/15m/1h/4h (EMA20 vs EMA50)
        tf = {}
        if df is not None and len(df) > 300:
            for name, rule in (("5m", None), ("15m", "15min"), ("1h", "1h"), ("4h", "4h")):
                c = df["c"] if rule is None else df["c"].resample(rule).last().dropna()
                if len(c) > 55:
                    tf[name] = int(np.sign(ind.ema(c, 20).iloc[-1] - ind.ema(c, 50).iloc[-1]))
            nyf = ind.ny_frame(df)
            twap = ind.session_twap(df, nyf["date"])
            vw = "sobre VWAP" if df["c"].iloc[-1] > twap.iloc[-1] else "bajo VWAP"
        else:
            vw = "sin datos"
        agree = sum(tf.values())
        tdir = int(np.sign(agree)) if abs(agree) >= 3 else None
        arrows = " ".join(f"{k}{'↑' if v > 0 else '↓'}" for k, v in tf.items())
        out["trend"] = {"texto": f"{arrows or 'calculando'} · {vw}", "dir": tdir,
                        "peso": self.cfg["trend"]["peso"], "razon": self.cfg["trend"]["razon"]}
        # Big Money
        if inst in self.cot:
            c = self.cot[inst]
            out["big_money"] = {"texto": f"COT {c['fecha']}: asset managers neto {c['neto']:+,.0f} "
                                         f"({'+' if c['cambio'] >= 0 else ''}{c['cambio']:,.0f} sem.)",
                                "dir": int(np.sign(c["cambio"])) or None}
        elif inst in self.funding:
            out["big_money"] = {"texto": f"funding BTC perp {self.funding[inst] * 100:+.4f}%/8h", "dir": None}
        else:
            out["big_money"] = {"texto": "sin dato aplicable", "dir": None}
        out["big_money"].update(peso=self.cfg["big_money"]["peso"], razon=self.cfg["big_money"]["razon"])
        # Retail (contrarian if extreme)
        s = self.sentiment.get(inst)
        rdir = (-1 if s > 65 else 1 if s < 35 else None) if s is not None else None
        out["retail"] = {"texto": f"clientes Capital.com {s:.0f}% largos" if s is not None else "sin dato",
                         "dir": rdir, "peso": self.cfg["retail"]["peso"], "razon": self.cfg["retail"]["razon"]}
        # News
        blk = self.news_block(inst, eng.now())
        nxt = self.next_events(1)
        out["news"] = {"texto": (f"BLOQUEO: {blk}" if blk else "libre") +
                       (f" · próximo: {nxt[0]['moneda']} {nxt[0]['evento']} {nxt[0]['hora_ny']} NY" if nxt else ""),
                       "dir": None, "peso": 0, "razon": self.cfg["news"]["razon"], "bloqueo": bool(blk),
                       "guardia": bool(self.cfg["news"].get("bloqueo"))}
        # Correlation
        other = "US500" if inst != "US500" else "US100"
        txt, cdir = "sin datos", None
        if df is not None and other in eng.bars and len(df) > 120:
            d2 = eng.bars[other].df5()
            j = df["c"].pct_change().to_frame("a").join(d2["c"].pct_change().to_frame("b"), how="inner").dropna().tail(96)
            if len(j) > 30:
                rho = j["a"].corr(j["b"])
                mv = d2["c"].iloc[-1] / d2["c"].iloc[-13] - 1 if len(d2) > 13 else 0
                cdir = int(np.sign(mv)) or None
                txt = f"ρ(8h) con {other} {rho:+.2f} · {other} {mv * 100:+.2f}% 1h"
        out["correlation"] = {"texto": txt, "dir": cdir, "peso": self.cfg["correlation"]["peso"],
                              "razon": self.cfg["correlation"]["razon"]}
        return out

    async def loop(self, instruments):
        n = 0
        while True:
            try:
                if time.time() - self.last_news > 3600:
                    await self.refresh_news()
                if n % 96 == 0:
                    await self.refresh_cot()
                if n % 3 == 0:
                    await self.refresh_sentiment(instruments)
            except Exception as e:
                self.log("ERROR", "-", f"agentes de información: {type(e).__name__}", "error")
            n += 1
            await asyncio.sleep(300)
