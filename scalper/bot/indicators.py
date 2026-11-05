"""Indicators over 5-minute bars (DataFrame with a UTC index and columns o, h, l, c)."""
import numpy as np
import pandas as pd

from .schedule import NY


def resample(df1: pd.DataFrame, rule="5min") -> pd.DataFrame:
    agg = df1[["o", "h", "l", "c"]].resample(rule, label="left", closed="left").agg(
        {"o": "first", "h": "max", "l": "min", "c": "last"})
    return agg.dropna()


def atr(df: pd.DataFrame, n=14) -> pd.Series:
    pc = df["c"].shift(1)
    tr = pd.concat([df["h"] - df["l"], (df["h"] - pc).abs(), (df["l"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def adx(df: pd.DataFrame, n=14) -> pd.Series:
    up = df["h"].diff()
    dn = -df["l"].diff()
    pdm = np.where((up > dn) & (up > 0), up, 0.0)
    ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = atr(df, n)
    pdi = 100 * pd.Series(pdm, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    ndi = 100 * pd.Series(ndm, index=df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    dx = 100 * (pdi - ndi).abs() / (pdi + ndi).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False).mean()


def ny_frame(df: pd.DataFrame) -> pd.DataFrame:
    """NY clock columns: date (NY session day), minute of day, weekday."""
    ny = df.index.tz_convert(NY)
    out = pd.DataFrame(index=df.index)
    out["date"] = ny.date
    out["min"] = ny.hour * 60 + ny.minute
    out["wd"] = ny.weekday
    # FX/gold trading day starts at 18:00 NY
    out["tday"] = (ny + pd.Timedelta(hours=6)).date
    return out


def session_twap(df: pd.DataFrame, key: pd.Series) -> pd.Series:
    """TWAP of the typical price since the start of the session in `key`. Capital.com CFDs have no real volume,
    so the "VWAP" is time-weighted, the same in the backtest and live."""
    tp = (df["h"] + df["l"] + df["c"]) / 3
    g = tp.groupby(key.values)
    return g.cumsum() / g.cumcount().add(1)


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()
