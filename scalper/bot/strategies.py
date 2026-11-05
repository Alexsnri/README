"""Candidate strategies (research/03). Each one turns 5-minute bars into signals.

The same code runs in the backtest and live: live, the Scout calls `signals()` on the latest bars and acts only
on the row of the bar that just closed. Every strategy returns a DataFrame aligned to the bars with:
  entry       +1 long, -1 short, 0 nothing (decided at that bar's close)
  stop_dist   initial stop distance in price (server-side stop)
  tp_dist     take-profit distance in price, or NaN
  max_bars    5-minute bars until the time stop
  exit_long / exit_short   strategy exit at that bar's close
"""
import itertools

import numpy as np
import pandas as pd

from . import indicators as ind

CASH_OPEN, CASH_CLOSE = 9 * 60 + 30, 16 * 60


def _empty(df):
    out = pd.DataFrame(index=df.index)
    out["entry"] = 0
    out["stop_dist"] = np.nan
    out["tp_dist"] = np.nan
    out["max_bars"] = 10_000
    out["exit_long"] = False
    out["exit_short"] = False
    return out


class Strategy:
    code = "S?"
    name = ""
    instruments = ()
    grid = {}

    def __init__(self, **params):
        self.params = {k: v[0] for k, v in self.grid.items()}
        self.params.update(params)

    @classmethod
    def configs(cls):
        keys = list(cls.grid)
        for vals in itertools.product(*[cls.grid[k] for k in keys]):
            yield cls(**dict(zip(keys, vals)))

    @property
    def key(self):
        return self.code + "(" + ",".join(f"{k}={v}" for k, v in self.params.items()) + ")"

    def signals(self, df: pd.DataFrame, family: str) -> pd.DataFrame:
        raise NotImplementedError


class DonchianScalp(Strategy):
    """S0: classic 5m channel breakout scalp. Baseline to measure what costs do to a scalp."""
    code, name = "S0", "Scalp breakout"
    instruments = ("US100", "US500", "GOLD", "EURUSD", "GBPUSD", "BTCUSD", "ETHUSD")
    grid = {"n": [12, 24]}

    def signals(self, df, family):
        out = _empty(df)
        a = ind.atr(df)
        hi = df["h"].rolling(self.params["n"]).max().shift(1)
        lo = df["l"].rolling(self.params["n"]).min().shift(1)
        out.loc[df["c"] > hi, "entry"] = 1
        out.loc[df["c"] < lo, "entry"] = -1
        out["stop_dist"] = 1.5 * a
        out["tp_dist"] = 1.5 * a
        out["max_bars"] = 12
        return out


class NoiseArea(Strategy):
    """S1: intraday momentum "Noise Area + VWAP" (Zarattini, Aziz & Barbon 2024). Index cash session."""
    code, name = "S1", "Noise Area + VWAP"
    instruments = ("US100", "US500")
    grid = {"m": [1.0, 1.25], "check": [30, 15], "stop_atr": [2.0, 3.0], "exit": ["check", "stop"]}
    lookback = 14

    def signals(self, df, family):
        out = _empty(df)
        nyf = ind.ny_frame(df)
        cash = (nyf["min"] >= CASH_OPEN) & (nyf["min"] < CASH_CLOSE)
        d = df[cash]
        f = nyf[cash]
        if d.empty:
            return out
        day_open = d["o"].where(f["min"] == CASH_OPEN).groupby(f["date"].values).transform("first")
        last_close = d["c"].where(f["min"] == CASH_CLOSE - 5).groupby(f["date"].values).transform("last")
        daily_close = last_close.groupby(f["date"].values).first()
        prev_close = pd.Series(f["date"].map(daily_close.shift(1)).values, index=d.index)
        t = f["min"] - CASH_OPEN
        move = (d["c"] / day_open - 1).abs()
        piv = pd.DataFrame({"date": f["date"].values, "t": t.values, "mv": move.values}).pivot_table(
            index="date", columns="t", values="mv")
        sig = piv.rolling(self.lookback, min_periods=self.lookback).mean().shift(1)
        sigma = sig.stack().rename("s")
        key = pd.MultiIndex.from_arrays([f["date"].values, t.values])
        s = pd.Series(sigma.reindex(key).values, index=d.index)
        ref_hi = np.maximum(day_open, prev_close.fillna(day_open))
        ref_lo = np.minimum(day_open, prev_close.fillna(day_open))
        ub = ref_hi * (1 + self.params["m"] * s)
        lb = ref_lo * (1 - self.params["m"] * s)
        twap = ind.session_twap(d, f["date"])
        close_min = f["min"] + 5
        check = (close_min % self.params["check"] == 0) & (close_min >= 10 * 60) & (close_min <= 15 * 60 + 30)
        ent = pd.Series(0, index=d.index)
        ent[check & (d["c"] > ub)] = 1
        ent[check & (d["c"] < lb)] = -1
        out.loc[d.index, "entry"] = ent
        a = ind.atr(df)
        out["stop_dist"] = self.params["stop_atr"] * a
        eod = f["min"] == CASH_CLOSE - 10   # bar 15:50-15:55
        if self.params["exit"] == "check":
            # as published: exit if at a check the price closes back inside max(UB, VWAP)
            xl = check & (d["c"] < np.maximum(ub, twap))
            xs = check & (d["c"] > np.minimum(lb, twap))
        else:
            # Stop Manager variant: the server-side stop follows max(UB, VWAP) at each 5m close
            xl = xs = pd.Series(False, index=d.index)
            out["lvl_long"] = np.nan
            out["lvl_short"] = np.nan
            out.loc[d.index, "lvl_long"] = np.maximum(ub, twap).values
            out.loc[d.index, "lvl_short"] = np.minimum(lb, twap).values
        out.loc[d.index, "exit_long"] = (xl | eod).values
        out.loc[d.index, "exit_short"] = (xs | eod).values
        out.loc[out["stop_dist"].isna(), "entry"] = 0
        return out


class OpeningRange(Strategy):
    """S2: opening range breakout (NY open for indices, London open for FX)."""
    code, name = "S2", "Opening Range Breakout"
    instruments = ("US100", "US500", "EURUSD", "GBPUSD")
    grid = {"n": [5, 15, 30], "tp_r": [2.0, 0.0]}

    def signals(self, df, family):
        out = _empty(df)
        if family == "index":
            nyf = ind.ny_frame(df)
            mins, day = nyf["min"], nyf["date"]
            open_m, end_m, last_entry = CASH_OPEN, CASH_CLOSE - 5, CASH_CLOSE - 65
        else:
            lon = df.index.tz_convert("Europe/London")
            mins = pd.Series(lon.hour * 60 + lon.minute, index=df.index)
            day = pd.Series(lon.date, index=df.index)
            open_m, end_m, last_entry = 8 * 60, 17 * 60 - 5, 15 * 60   # until 12:00 NY ~ 17:00 London
        n = self.params["n"]
        in_or = (mins >= open_m) & (mins < open_m + n)
        orh = df["h"].where(in_or).groupby(day.values).transform("max")
        orl = df["l"].where(in_or).groupby(day.values).transform("min")
        after = (mins >= open_m + n) & (mins <= last_entry)
        a = ind.atr(df)
        up = after & (df["c"] > orh)
        dn = after & (df["c"] < orl)
        raw = pd.Series(np.where(up, 1, np.where(dn, -1, 0)), index=df.index)
        first = raw.ne(0) & (raw.ne(0).astype(int).groupby(day.values).cumsum() == 1)
        ent = raw.where(first, 0)
        stop = np.where(ent > 0, df["c"] - orl, orh - df["c"])
        stop = np.maximum(stop, 0.5 * a)
        ent[(stop > 4 * a)] = 0
        out["entry"] = ent
        out["stop_dist"] = stop
        if self.params["tp_r"] > 0:
            out["tp_dist"] = self.params["tp_r"] * stop
        eod = mins == end_m
        out["exit_long"] = eod.values
        out["exit_short"] = eod.values
        return out


class LastHalfHour(Strategy):
    """S3: last-half-hour momentum (Gao, Han, Li & Zhou 2018). The first half hour (from yesterday's close to
    10:00 NY) predicts the last one. Enters at 15:30 NY, exits at 15:55."""
    code, name = "S3", "Momentum media hora final"
    instruments = ("US100", "US500")
    grid = {"confirm": [False, True], "thresh": [False, True]}

    def signals(self, df, family):
        out = _empty(df)
        nyf = ind.ny_frame(df)
        day = nyf["date"].values
        close_at = lambda m: df["c"].where(nyf["min"] == m - 5).groupby(day).transform("last")
        p10, p15, p1530 = close_at(10 * 60), close_at(15 * 60), close_at(15 * 60 + 30)
        daily_close = df["c"].where(nyf["min"] == CASH_CLOSE - 5).groupby(day).last()
        prev = pd.Series(nyf["date"].map(daily_close.shift(1)).values, index=df.index)
        r1 = p10 / prev - 1
        r12 = p1530 / p15 - 1
        sig = np.sign(r1)
        if self.params["confirm"]:
            sig = sig.where(np.sign(r12) == sig, 0)
        if self.params["thresh"]:
            daily_r1 = r1.groupby(day).first()
            sd = daily_r1.rolling(20, min_periods=10).std().shift(1)
            sdv = pd.Series(nyf["date"].map(sd).values, index=df.index)
            sig = sig.where(r1.abs() > 0.5 * sdv, 0)
        at = nyf["min"] == 15 * 60 + 25
        out["entry"] = sig.where(at, 0).fillna(0).astype(int)
        out["stop_dist"] = 2.0 * ind.atr(df)
        eod = nyf["min"] == CASH_CLOSE - 10
        out["exit_long"] = eod.values
        out["exit_short"] = eod.values
        return out


class VwapRevert(Strategy):
    """S4: reversion to the session VWAP (TWAP) only when there is no trend (low ADX)."""
    code, name = "S4", "Reversion a VWAP"
    instruments = ("EURUSD", "GOLD", "US100")
    grid = {"z": [2.0, 2.5], "adx_max": [20, 25], "max_bars": [12, 24]}

    def signals(self, df, family):
        out = _empty(df)
        nyf = ind.ny_frame(df)
        key = nyf["date"] if family == "index" else nyf["tday"]
        twap = ind.session_twap(df, key)
        dev = df["c"] - twap
        z = dev / dev.rolling(60, min_periods=30).std()
        n_in = df["c"].groupby(key.values).cumcount()
        calm = ind.adx(df) < self.params["adx_max"]
        ok = calm & (n_in >= 12)
        out.loc[ok & (z < -self.params["z"]), "entry"] = 1
        out.loc[ok & (z > self.params["z"]), "entry"] = -1
        out["stop_dist"] = 1.5 * ind.atr(df)
        out["max_bars"] = self.params["max_bars"]
        out["exit_long"] = (df["c"] >= twap).values
        out["exit_short"] = (df["c"] <= twap).values
        return out


class CryptoFade(Strategy):
    """S5: fade extreme 1-hour moves in BTC/ETH (short-term reversal, De Nicola 2021)."""
    code, name = "S5", "Contra-movimiento cripto"
    instruments = ("BTCUSD", "ETHUSD")
    grid = {"k": [2.0, 3.0], "max_bars": [12, 48], "stop_atr": [2.5, 4.0]}

    def signals(self, df, family):
        out = _empty(df)
        r = df["c"] / df["c"].shift(12) - 1
        sd = r.rolling(8640, min_periods=2000).std()
        k = self.params["k"]
        out.loc[r < -k * sd, "entry"] = 1
        out.loc[r > k * sd, "entry"] = -1
        out["stop_dist"] = self.params["stop_atr"] * ind.atr(df)
        out["max_bars"] = self.params["max_bars"]
        return out


class BtcSeason(Strategy):
    """S6: CONTROL. Long BTC from 21:00 to 23:00 UTC. If it "wins" after costs, suspect the backtest."""
    code, name = "S6", "Control estacionalidad BTC"
    instruments = ("BTCUSD",)
    grid = {"x": [0]}
    ignore_schedule = True

    def signals(self, df, family):
        out = _empty(df)
        h = df.index.hour * 60 + df.index.minute
        out.loc[h == 20 * 60 + 55, "entry"] = 1
        out["stop_dist"] = 4.0 * ind.atr(df)
        out["exit_long"] = h == 22 * 60 + 55
        return out


ALL = [DonchianScalp, NoiseArea, OpeningRange, LastHalfHour, VwapRevert, CryptoFade, BtcSeason]
BY_CODE = {c.code: c for c in ALL}
