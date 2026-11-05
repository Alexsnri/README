"""Descarga velas de 1 minuto de HistData.com (gratis, formato ASCII M1).

HistData dice que sus horas están en "EST sin horario de verano", pero comparando minuto a minuto contra Dukascopy
(UTC) en enero, julio y octubre de 2026 los precios coinciden exactos solo si se leen como hora de Nueva York CON
horario de verano. lab/data.py hace esa corrección.
Aquí se guarda el índice como "etiqueta + 5 h" en UTC, tal cual se descargó.
Uso: python -I lab/histdata.py XAUUSD SPXUSD NSXUSD EURUSD GBPUSD
"""
import io, os, re, sys, time, zipfile
import httpx, pandas as pd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "histdata")
BASE = "https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/{p}/{y}"
H = {"User-Agent": "Mozilla/5.0"}


def get(cl, sym, y, m=None):
    tag = f"{y}" if m is None else f"{y}-{m:02d}"
    path = os.path.join(OUT, sym, f"{tag}.parquet")
    if os.path.exists(path):
        return
    page = BASE.format(p=sym.lower(), y=y) + ("" if m is None else f"/{m}")
    for k in range(5):
        try:
            html = cl.get(page, timeout=60).text
            form = dict(re.findall(r'name="(tk|date|datemonth|platform|timeframe|fxpair)" id="\w+" value="([^"]*)"', html))
            if "tk" not in form:
                print("sin formulario", sym, tag, flush=True); return
            r = cl.post("https://www.histdata.com/get.php", data=form, headers={"Referer": page}, timeout=180)
            if r.status_code == 200 and r.content[:2] == b"PK":
                break
        except httpx.HTTPError:
            pass
        time.sleep(10 * (k + 1))
    else:
        print("FALLO", sym, tag, flush=True); return
    z = zipfile.ZipFile(io.BytesIO(r.content))
    name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    df = pd.read_csv(z.open(name), sep=";", header=None, names=["t", "o", "h", "l", "c", "v"])
    df.index = pd.to_datetime(df["t"], format="%Y%m%d %H%M%S").dt.tz_localize("Etc/GMT+5").dt.tz_convert("UTC")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df[["o", "h", "l", "c"]].astype(float).to_parquet(path)
    print("ok", sym, tag, len(df), flush=True)
    time.sleep(3)


if __name__ == "__main__":
    with httpx.Client(headers=H, follow_redirects=True) as cl:
        for sym in sys.argv[1:]:
            for y in range(2021, 2026):
                get(cl, sym, y)
            for m in range(1, 11):
                get(cl, sym, 2026, m)
