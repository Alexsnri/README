"""Loads the 1-minute history of each instrument (UTC) and caches it."""
import glob
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from bot.instruments import INSTRUMENTS  # noqa: E402

DATA = os.path.join(ROOT, "data")


def load_1m(name: str) -> pd.DataFrame:
    cache = os.path.join(DATA, "cache", f"{name}_1m.parquet")
    if os.path.exists(cache):
        return pd.read_parquet(cache)
    src, sym = INSTRUMENTS[name].data
    files = sorted(glob.glob(os.path.join(DATA, src, sym, "*.parquet")))
    df = pd.concat([pd.read_parquet(f)[["o", "h", "l", "c"]] for f in files])
    if src == "histdata":
        # The download stored "label + 5 h" as UTC. The real labels are New York time WITH DST: verified minute
        # by minute against Dukascopy (UTC) in January, July and October 2026 (identical prices).
        label = (df.index.tz_convert("UTC") - pd.Timedelta(hours=5)).tz_localize(None)
        idx = pd.DatetimeIndex(label).tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT")
        df = df[~idx.isna()]
        df.index = idx[~idx.isna()].tz_convert("UTC")
    df = df[~df.index.duplicated()].sort_index()
    df = df[(df["h"] >= df["l"]) & (df["c"] > 0)]
    df = df[df.index >= "2021-01-04"]
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    df.to_parquet(cache)
    return df
