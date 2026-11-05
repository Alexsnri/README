"""Do the information agents improve the out-of-sample result?

Takes the walk-forward OOS trades of each strategy that passed and applies each agent as a filter declared
BEFORE looking at the results (a single rule per agent, no parameter tuning):
  Trend        trade in the direction of the 1h trend (EMA20 vs EMA50 of the last closed 1h bars)
  Correlation  US500 must confirm: its move since the cash open has the same sign as the trade
  News         no entries on FOMC days between 13:55 and 14:45 NY (the 8:30 window is already in the schedule)
  Big Money    trade in the direction of the weekly change in the asset managers' net position (CFTC COT,
               NASDAQ MINI), using only reports already published (Tuesday's report counts from the Monday after)
  Retail       no history exists for Capital.com sentiment -> it cannot be backtested; it only gets recorded
Criterion to stay ON: more total growth (sum of log(1+1%*R)) than without the filter, and better in at least
2 of every 3 OOS years.
"""
import json
import os
import sys

import httpx
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
from data import load_1m  # noqa: E402
from bot import indicators as ind  # noqa: E402

OUT = os.path.join(HERE, "results")


def trend_dir(inst):
    df5 = ind.resample(load_1m(inst))
    h1 = df5["c"].resample("1h", label="right", closed="left").last().dropna()
    d = np.sign(ind.ema(h1, 20) - ind.ema(h1, 50))
    return d   # index = end of the 1h bar (already closed)


def us500_from_open():
    df5 = ind.resample(load_1m("US500"))
    nyf = ind.ny_frame(df5)
    cash = (nyf["min"] >= 570) & (nyf["min"] < 960)
    d = df5[cash]
    op = d["o"].groupby(nyf.loc[cash, "date"].values).transform("first")
    r = np.sign(d["c"] / op - 1)
    r.index = r.index + pd.Timedelta(minutes=5)   # known at the bar close
    return r


def cot_dir():
    cache = os.path.join(ROOT, "data", "cot_nasdaq.json")
    if not os.path.exists(cache):
        url = ("https://publicreporting.cftc.gov/resource/gpe5-46if.json?$where=market_and_exchange_names%20like%20"
               "'NASDAQ%20MINI%25'&$limit=5000&$order=report_date_as_yyyy_mm_dd")
        json.dump(httpx.get(url, timeout=60).json(), open(cache, "w"))
    rows = json.load(open(cache))
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["report_date_as_yyyy_mm_dd"]).dt.tz_localize("America/New_York")
    df = df.drop_duplicates("date").set_index("date").sort_index()
    net = df["asset_mgr_positions_long"].astype(float) - df["asset_mgr_positions_short"].astype(float)
    chg = np.sign(net.diff())
    chg.index = chg.index + pd.Timedelta(days=6)   # usable from the Monday after the report
    return chg.tz_convert("UTC")


def asof(series, times):
    s = series.sort_index()
    idx = s.index.searchsorted(times, side="right") - 1
    vals = np.where(idx >= 0, s.to_numpy()[np.clip(idx, 0, None)], np.nan)
    return vals


def score(R):
    return float(np.log1p(0.01 * R).sum())


def main():
    oos = pd.read_parquet(os.path.join(OUT, "oos_trades.parquet"))
    rank = pd.read_csv(os.path.join(OUT, "ranking.csv"))
    passed = rank[rank["verdict"].isin(["DEPLOY", "REFINE"])]
    fomc = set(json.load(open(os.path.join(ROOT, "bot", "data", "fomc.json")))["decision_14h_ny"])
    cot = cot_dir()
    s500 = us500_from_open()
    rows = []
    for _, p in passed.iterrows():
        tr = oos[(oos["strat"] == p["strat"]) & (oos["inst"] == p["inst"])].copy()
        t = pd.DatetimeIndex(tr["t_in"])
        ny = t.tz_convert("America/New_York")
        filters = {
            "Trend": asof(trend_dir(p["inst"]), t) == tr["dir"].to_numpy(),
            "Correlation (US500 confirma)": asof(s500, t) == tr["dir"].to_numpy() if p["inst"] != "US500" else None,
            "News (FOMC)": ~np.array([(d.isoformat() in fomc) and (13 * 60 + 55 <= m < 14 * 60 + 45)
                                      for d, m in zip(ny.date, ny.hour * 60 + ny.minute)]),
            "Big Money (COT asset managers)": asof(cot, t) == tr["dir"].to_numpy() if p["inst"] in ("US100",) else None,
        }
        base = score(tr["R"])
        years = tr["t_in"].dt.year
        for name, keep in filters.items():
            if keep is None:
                continue
            keep = np.asarray(keep, dtype=bool)
            kept, removed = tr[keep], tr[~keep]
            better_years = sum(score(kept[years[keep] == y]["R"]) > score(tr[years == y]["R"]) for y in years.unique())
            gain = score(kept["R"]) - base
            on = gain > 0 and better_years >= 2 / 3 * years.nunique()
            rows.append(dict(strat=p["strat"], inst=p["inst"], agente=name, n_base=len(tr), n_kept=len(kept),
                             E_base=tr["R"].mean(), E_kept=kept["R"].mean() if len(kept) else np.nan,
                             E_removed=removed["R"].mean() if len(removed) else np.nan,
                             log_growth_change=gain, better_years=f"{better_years}/{years.nunique()}",
                             decision="ON" if on else "OFF"))
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(OUT, "agentes_info.csv"), index=False)
    print(res.round(3).to_string())


if __name__ == "__main__":
    main()
