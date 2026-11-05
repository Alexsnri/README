"""Simulated broker (BOT_SIM=1): replays real 1-minute history as if it were the Capital.com stream.

It is used for the end-to-end tests and to see the dashboard without credentials. It has the same interface as
CapitalClient. Server-side stops/TPs execute on the simulated bid/ask; the clock advances with the replay.
"""
import asyncio
import os
import time

import numpy as np
import pandas as pd

from .instruments import INSTRUMENTS


class FakeBroker:
    def __init__(self, data: dict, start: str, speed=120.0, balance=100.0, warmup_days=25):
        """data = {inst: 1m DataFrame (UTC, o h l c)}; start = timestamp where the replay begins."""
        self.data = data
        self.t0 = pd.Timestamp(start, tz="UTC")
        self.clock = self.t0.timestamp()
        self.speed = speed
        self.balance_v = balance
        self.pos = {}
        self.confirms = {}
        self.acts = []
        self.n = 0
        self.warmup = warmup_days
        self.streaming_host = "sim"
        self.session_info = {"accountType": "CFD", "sim": True}
        self.cst = "sim"
        self.done = False

    def now(self):
        return self.clock

    # ---------------------------------------------------------------- API
    async def login(self):
        return {}

    async def ping(self):
        return {"status": "OK"}

    async def balance(self):
        upl = sum(self._upl(p) for p in self.pos.values())
        return {"balance": round(self.balance_v, 2), "upl": round(upl, 2), "available": self.balance_v + upl,
                "deposit": 0, "currency": "USD"}

    async def top_up(self, amount):
        self.balance_v += amount
        return {"successful": True}

    async def market(self, epic):
        inst = next(i for i in INSTRUMENTS if INSTRUMENTS[i].epic == epic)
        df = self.data.get(inst)
        px = float(df["c"].iloc[0]) if df is not None else 100.0
        fam = INSTRUMENTS[inst].family
        mins = {"index": (0.001 if inst == "US100" else 0.01), "metal": 0.01, "fx": 100, "crypto": 0.0001}[fam]
        return {"dealingRules": {"minDealSize": {"value": mins}, "minSizeIncrement": {"value": mins},
                                 "maxDealSize": {"value": 1e6},
                                 "minStopOrProfitDistance": {"unit": "PERCENTAGE", "value": 0.05}},
                "instrument": {"marginFactor": 1 if fam != "crypto" else 5, "marginFactorUnit": "PERCENTAGE",
                               "lotSize": 1},
                "snapshot": {"bid": px, "decimalPlacesFactor": 100000 if fam == "fx" else 100}}

    async def prices(self, epic, resolution="MINUTE_5", start=None, end=None, max_=1000):
        inst = next(i for i in INSTRUMENTS if INSTRUMENTS[i].epic == epic)
        df = self.data.get(inst)
        if df is None:
            return []
        a = pd.Timestamp(start, tz="UTC")
        b = min(pd.Timestamp(end, tz="UTC"), self.t0)
        d = df[(df.index >= a) & (df.index < b)]
        r5 = d.resample("5min").agg({"o": "first", "h": "max", "l": "min", "c": "last"}).dropna()
        sp = INSTRUMENTS[inst].spread_bps / 1e4
        out = []
        for t, row in r5.iterrows():
            half = row["c"] * sp / 2
            mk = lambda v: {"bid": v - half, "ask": v + half}
            out.append({"snapshotTimeUTC": t.strftime("%Y-%m-%dT%H:%M:%S"), "openPrice": mk(row["o"]),
                        "highPrice": mk(row["h"]), "lowPrice": mk(row["l"]), "closePrice": mk(row["c"])})
        return out[-max_:]

    async def sentiment(self, ids):
        return [{"marketId": i, "longPositionPercentage": 55.0, "shortPositionPercentage": 45.0} for i in ids]

    async def positions(self):
        out = []
        for d, p in self.pos.items():
            out.append({"position": {"dealId": d, "direction": "BUY" if p["dir"] > 0 else "SELL", "size": p["size"],
                                     "level": p["level"], "stopLevel": p["stop"], "profitLevel": p["tp"],
                                     "upl": self._upl(p)},
                        "market": {"epic": INSTRUMENTS[p["inst"]].epic, "marketStatus": "TRADEABLE"}})
        return out

    def _quote(self, inst):
        return self.last.get(inst)

    def _upl(self, p):
        q = self.last.get(p["inst"])
        if not q:
            return 0.0
        px = q[0] if p["dir"] > 0 else q[1]
        return p["dir"] * (px - p["level"]) * p["size"]

    async def open_position(self, epic, direction, size, stop_level, profit_level=None):
        inst = next(i for i in INSTRUMENTS if INSTRUMENTS[i].epic == epic)
        bid, ask = self.last[inst]
        lvl = ask if direction > 0 else bid
        self.n += 1
        deal, ref = f"D{self.n}", f"R{self.n}"
        self.pos[deal] = {"inst": inst, "dir": direction, "size": size, "level": lvl, "stop": stop_level,
                          "tp": profit_level}
        self.confirms[ref] = {"dealStatus": "ACCEPTED", "level": lvl, "affectedDeals": [{"dealId": deal}],
                              "dealId": deal}
        return {"dealReference": ref}

    async def confirm(self, ref, tries=8):
        return self.confirms.get(ref, {})

    async def update_position(self, deal, stop_level, profit_level=None):
        if deal in self.pos:
            self.pos[deal]["stop"] = stop_level
            self.pos[deal]["tp"] = profit_level
        return {"dealReference": "U"}

    async def close_position(self, deal):
        from .capital import ApiError
        p = self.pos.pop(deal, None)
        if not p:
            raise ApiError("not found", 404)
        bid, ask = self.last[p["inst"]]
        lvl = bid if p["dir"] > 0 else ask
        self.balance_v += p["dir"] * (lvl - p["level"]) * p["size"]
        self.n += 1
        self.confirms[f"C{self.n}"] = {"dealStatus": "ACCEPTED", "level": lvl}
        return {"dealReference": f"C{self.n}"}

    async def activity(self, last_period=3600, deal_id=None):
        return [a for a in self.acts if a["dealId"] == deal_id]

    # ---------------------------------------------------------------- replay
    async def run(self, on_quote, until=None):
        """Emits 4 quotes per minute (open, high/low, close) for each instrument, in time order."""
        self.last = {}
        frames = []
        for inst, df in self.data.items():
            d = df[df.index >= self.t0]
            if until:
                d = d[d.index < pd.Timestamp(until, tz="UTC")]
            frames.append(d.assign(inst=inst))
        allm = pd.concat(frames).sort_index()
        wall0 = time.monotonic()
        sim0 = self.clock
        for t, row in allm.iterrows():
            inst = row["inst"]
            sp = row["c"] * INSTRUMENTS[inst].spread_bps / 1e4
            base = t.timestamp()
            path = [row["o"], row["l"], row["h"], row["c"]] if row["c"] >= row["o"] else \
                [row["o"], row["h"], row["l"], row["c"]]
            for k, mid in enumerate(path):
                self.clock = base + 15 * k + 1
                bid, ask = mid - sp / 2, mid + sp / 2
                self.last[inst] = (bid, ask)
                self._server_stops(inst, bid, ask)
                await on_quote(INSTRUMENTS[inst].epic, bid, ask, self.clock)
            if self.speed:
                lag = (self.clock - sim0) / self.speed - (time.monotonic() - wall0)
                if lag > 0:
                    await asyncio.sleep(lag)
            else:
                await asyncio.sleep(0)
        self.done = True

    def _server_stops(self, inst, bid, ask):
        for d, p in list(self.pos.items()):
            if p["inst"] != inst:
                continue
            px = bid if p["dir"] > 0 else ask
            hit = None
            if p["stop"] is not None and p["dir"] * (px - p["stop"]) <= 0:
                hit, src = p["stop"], "SL"
            elif p["tp"] and p["dir"] * (px - p["tp"]) >= 0:
                hit, src = p["tp"], "TP"
            if hit is not None:
                self.balance_v += p["dir"] * (hit - p["level"]) * p["size"]
                self.acts.append({"dealId": d, "source": src, "level": hit, "status": "ACCEPTED"})
                del self.pos[d]
