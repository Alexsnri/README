"""Descarga velas de 1 minuto de data.binance.vision (archivo público) y las guarda en parquet por mes."""
import io, os, sys, zipfile
import httpx, pandas as pd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "binance")
COLS = ["t", "o", "h", "l", "c", "v", "ct", "qv", "n", "tb", "tq", "x"]


def month(sym, y, m):
    p = os.path.join(OUT, sym, f"{y}-{m:02d}.parquet")
    if os.path.exists(p):
        return
    url = f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1m/{sym}-1m-{y}-{m:02d}.zip"
    r = httpx.get(url, timeout=120)
    if r.status_code != 200:
        print("sin datos", url, r.status_code); return
    z = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_csv(z.open(z.namelist()[0]), header=None, names=COLS)
    t = df["t"].astype("int64")
    unit = "us" if t.iloc[0] > 1e14 else "ms"   # desde 2025 Binance usa microsegundos
    df.index = pd.to_datetime(t, unit=unit, utc=True)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    df[["o", "h", "l", "c", "v", "n"]].astype(float).to_parquet(p)
    print("ok", sym, y, m, len(df), flush=True)


if __name__ == "__main__":
    for sym in sys.argv[1:]:
        for y in range(2021, 2027):
            for m in range(1, 13):
                if (y, m) < (2021, 11) or (y, m) > (2026, 10):
                    continue
                month(sym, y, m)
