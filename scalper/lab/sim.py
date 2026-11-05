"""Trade simulator on 1-minute bars with real costs.

- Signal at the 5m bar close; entry at the open of the next 1m bar, paying half the spread.
- Spread by instrument and time of day: published spread x widening by slot x `cost_mult`
  (1.25 base, 2.0 stress).
- Stops: checked against the bid (long) or the ask (short) of each minute; if the stop and the target fall in
  the same minute, the stop is assumed (worst case). A stop fill pays an extra `slip_frac` x spread of
  slippage, and a gap fills at the open. The stop moves at each 1m close (`bot.stops.update_stop`).
- Mandatory flattening at the rollover/close (schedule) and no entries outside the allowed slots.
- The trade result is in R = P&L / initial stop distance, already net of costs.
"""
import os
import sys

import numpy as np
import pandas as pd
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from bot import indicators as ind  # noqa: E402
from bot import schedule  # noqa: E402
from bot.instruments import INSTRUMENTS  # noqa: E402
from bot.stops import update_stop  # noqa: E402

_update = njit(cache=True)(update_stop)


@njit(cache=True)
def _run(ent_i, ent_dir, ent_stop, ent_tp, ent_maxb, ent_atr, j0_arr,
         o, h, l, c, sp, flat, ok, b5, last5, exl, exs, lvl_l, lvl_s,
         be_trig, trail_mult, trail_start, slip_frac, ignore_sched):
    n = len(ent_i)
    rec = np.full((n, 8), np.nan)
    busy = -1
    m = len(o)
    for k in range(n):
        j0 = j0_arr[k]
        if j0 < 0 or j0 <= busy:
            continue
        if not ignore_sched and ((not ok[j0]) or flat[j0]):
            continue
        d = ent_dir[k]
        s0 = sp[j0]
        entry = o[j0] + d * s0 / 2.0
        sd = max(ent_stop[k], 4.0 * s0)
        stop = entry - d * sd
        tp = np.nan
        if ent_tp[k] == ent_tp[k] and ent_tp[k] > 0:
            tp = entry + d * ent_tp[k]
        atr = ent_atr[k]
        be_buf = slip_frac * s0 + 0.1 * s0
        best = o[j0] - d * s0 / 2.0
        moved = 0
        reason = 0
        px = np.nan
        j = j0
        while j < m:
            s = sp[j]
            xo = o[j] - d * s / 2.0
            xh = h[j] - d * s / 2.0
            xl = l[j] - d * s / 2.0
            xc = c[j] - d * s / 2.0
            adverse = xl if d > 0 else xh
            favor = xh if d > 0 else xl
            if j > j0 and d * (xo - stop) <= 0:
                px = xo - d * slip_frac * s
                reason = 1
                break
            if d * (adverse - stop) <= 0:
                px = stop - d * slip_frac * s
                reason = 1 if moved == 0 else 4
                break
            if tp == tp and d * (favor - tp) >= 0:
                px = tp
                reason = 2
                break
            if d * (xc - best) > 0:
                best = xc
            ns = _update(d, entry, stop, best, atr, be_trig, be_buf, trail_mult, trail_start)
            if ns != stop:
                moved += 1
                stop = ns
            if flat[j] and not ignore_sched:
                px = xc
                reason = 5
                break
            if last5[j]:
                bi = b5[j]
                lv = lvl_l[bi] if d > 0 else lvl_s[bi]
                if lv == lv and d * (lv - stop) > 0:
                    if d * (xc - lv) <= 0:      # the level is already crossed: close at market
                        px = xc
                        reason = 4
                        break
                    stop = lv                    # structural stop (only in favor), server-side
                    moved += 1
                if (d > 0 and exl[bi]) or (d < 0 and exs[bi]):
                    px = xc
                    reason = 3
                    break
                if bi - ent_i[k] >= ent_maxb[k]:
                    px = xc
                    reason = 6
                    break
            j += 1
        if j >= m:
            break
        r = d * (px - entry) / sd
        cost = (s0 / 2.0 + sp[j] / 2.0 + (slip_frac * sp[j] if reason in (1, 4) else 0.0)) / sd
        rec[k, 0] = j0
        rec[k, 1] = j
        rec[k, 2] = d
        rec[k, 3] = r
        rec[k, 4] = cost
        rec[k, 5] = reason
        rec[k, 6] = moved
        rec[k, 7] = sd / entry * 1e4
        busy = j
    return rec


REASONS = {1: "stop", 2: "objetivo", 3: "salida estrategia", 4: "stop movido (BE/trailing)", 5: "cierre por horario",
           6: "tiempo"}


class Market:
    """Instrument data ready for the simulation."""

    def __init__(self, name, df1, cost_mult=1.25):
        self.name = name
        self.inst = INSTRUMENTS[name]
        self.df1 = df1
        self.df5 = ind.resample(df1)
        t1 = df1.index
        self.t1 = t1
        self.o, self.h, self.l, self.c = (df1[k].to_numpy(np.float64) for k in "ohlc")
        self.base_sp = self.inst.spread_bps / 1e4 * self.c * schedule.spread_multiplier(t1, self.inst.family)
        self.set_cost(cost_mult)
        self.flat = schedule.flatten_mask(t1, name, self.inst.family)
        self.ok = schedule.entry_mask(t1, name)
        floor5 = t1.floor("5min")
        self.b5 = np.searchsorted(self.df5.index.values, floor5.values).astype(np.int64)
        self.last5 = np.append(self.b5[1:] != self.b5[:-1], True)
        start = np.searchsorted(t1.values, self.df5.index.values)
        nxt = np.append(start[1:], len(t1))
        # entry at the first minute after the 5m bar closes, only if it comes right after (no gap)
        bar_end = self.df5.index.values + np.timedelta64(5, "m")
        okgap = np.zeros(len(nxt), dtype=bool)
        valid = nxt < len(t1)
        okgap[valid] = (t1.values[nxt[valid]] - bar_end[valid]) <= np.timedelta64(2, "m")
        self.j0_of_bar = np.where(okgap, nxt, -1).astype(np.int64)
        self.atr5 = ind.atr(self.df5).to_numpy(np.float64)

    def set_cost(self, cost_mult):
        self.cost_mult = cost_mult
        self.sp = self.base_sp * cost_mult


def _col(sig, name):
    return sig[name].to_numpy(np.float64) if name in sig else np.full(len(sig), np.nan)


def simulate(mk: Market, sig: pd.DataFrame, policy: dict, slip_frac=0.5, ignore_schedule=False) -> pd.DataFrame:
    e = sig["entry"].to_numpy()
    idx = np.nonzero((e != 0) & np.isfinite(sig["stop_dist"].to_numpy()) & (sig["stop_dist"].to_numpy() > 0))[0]
    if len(idx) == 0:
        return pd.DataFrame(columns=["t_in", "t_out", "dir", "R", "cost_R", "reason", "moves", "stop_bps"])
    rec = _run(idx.astype(np.int64), e[idx].astype(np.float64), sig["stop_dist"].to_numpy(np.float64)[idx],
               sig["tp_dist"].to_numpy(np.float64)[idx], sig["max_bars"].to_numpy(np.int64)[idx],
               mk.atr5[idx], mk.j0_of_bar[idx],
               mk.o, mk.h, mk.l, mk.c, mk.sp, mk.flat, mk.ok, mk.b5, mk.last5,
               sig["exit_long"].to_numpy(np.bool_), sig["exit_short"].to_numpy(np.bool_),
               _col(sig, "lvl_long"), _col(sig, "lvl_short"),
               policy["be_trig"], policy["trail_mult"], policy["trail_start"], slip_frac, ignore_schedule)
    rec = rec[~np.isnan(rec[:, 0])]
    tr = pd.DataFrame(rec, columns=["j0", "j1", "dir", "R", "cost_R", "reason", "moves", "stop_bps"])
    tr["t_in"] = mk.t1[tr["j0"].astype(int)]
    tr["t_out"] = mk.t1[tr["j1"].astype(int)]
    tr["inst"] = mk.name
    return tr.drop(columns=["j0", "j1"])
