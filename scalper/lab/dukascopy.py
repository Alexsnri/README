"""Descarga velas de 1 minuto BID y ASK de Dukascopy (datos públicos) para tener spread real por minuto.

Uso: python -I lab/dukascopy.py SIMBOLO AAAA-MM-DD AAAA-MM-DD
Guarda data/duka/SIMBOLO/AAAA-MM-DD.parquet con columnas o,h,l,c (bid) y ao,ah,al,ac (ask), v.
"""
import lzma, os, struct, sys, time
from datetime import date, datetime, timedelta, timezone

import numpy as np
import pandas as pd
import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "duka")
URL = "https://datafeed.dukascopy.com/datafeed/{s}/{y}/{m:02d}/{d:02d}/{side}_candles_min_1.bi5"
SCALE = {"EURUSD": 1e5, "GBPUSD": 1e5, "XAUUSD": 1e3, "USA500IDXUSD": 1e3, "USATECHIDXUSD": 1e3,
         "BTCUSD": 1e1, "ETHUSD": 1e1, "DOLLARIDXUSD": 1e3, "USA30IDXUSD": 1e3}


def fetch(client, sym, day, side):
    url = URL.format(s=sym, y=day.year, m=day.month - 1, d=day.day, side=side)
    for k in range(9):
        try:
            r = client.get(url, timeout=40)
            if r.status_code == 200:
                return r.content
            if r.status_code == 404:
                return b""
        except httpx.HTTPError:
            pass
        time.sleep(min(300, 5 * 2 ** k))
    print("FALLO", url, flush=True)
    return None


def parse(raw, day, scale):
    if raw is None:
        return None
    if not raw:
        return pd.DataFrame()
    b = lzma.decompress(raw)
    n = len(b) // 24
    a = np.frombuffer(b[: n * 24], dtype=">i4").reshape(n, 6)
    vol = np.frombuffer(b[: n * 24], dtype=">f4").reshape(n, 6)[:, 5]
    t0 = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    idx = pd.to_datetime([t0 + timedelta(seconds=int(s)) for s in a[:, 0]])
    return pd.DataFrame({"o": a[:, 1] / scale, "c": a[:, 2] / scale, "l": a[:, 3] / scale,
                         "h": a[:, 4] / scale, "v": vol.astype(float)}, index=idx)


def main(sym, d0, d1):
    os.makedirs(os.path.join(OUT, sym), exist_ok=True)
    scale = SCALE[sym]
    day = date.fromisoformat(d0)
    end = date.fromisoformat(d1)
    with httpx.Client(headers={"User-Agent": "Mozilla/5.0"}, http2=False) as cl:
        while day <= end:
            p = os.path.join(OUT, sym, f"{day}.parquet")
            if not os.path.exists(p) and (day.weekday() < 5 or sym in ("BTCUSD", "ETHUSD") or day.weekday() == 6):
                bid = parse(fetch(cl, sym, day, "BID"), day, scale)
                time.sleep(1.0)
                ask = parse(fetch(cl, sym, day, "ASK"), day, scale)
                time.sleep(1.0)
                if bid is None or ask is None:
                    day += timedelta(days=1)
                    continue
                if len(bid) and len(ask):
                    df = bid.join(ask[["o", "h", "l", "c"]].add_prefix("a"), how="inner")
                    df = df[df["v"] > 0]
                    df.to_parquet(p)
                else:
                    pd.DataFrame().to_parquet(p)
            day += timedelta(days=1)


if __name__ == "__main__":
    if sys.argv[1] == "all":  # all AAAA-MM-DD AAAA-MM-DD : todos los símbolos, mes por mes hacia atrás
        syms = ["USA500IDXUSD", "USATECHIDXUSD", "XAUUSD", "EURUSD", "GBPUSD", "DOLLARIDXUSD"]
        d0, d1 = date.fromisoformat(sys.argv[2]), date.fromisoformat(sys.argv[3])
        m_end = d1
        while m_end >= d0:
            m_start = max(d0, m_end.replace(day=1))
            for s in syms:
                main(s, str(m_start), str(m_end))
                print("OK", s, m_start, flush=True)
            m_end = m_start - timedelta(days=1)
    else:
        main(*sys.argv[1:4])
