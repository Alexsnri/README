"""Volatilidad intradía por hora. Uso: python3 -I hourly_vol.py <data_dir>
Binance 1m (BTC, ETH, PAXG) y Yahoo 5m/1m (EURUSD, GBPUSD, GC, NQ, ES).
Las horas se agrupan en hora de Nueva York (ET) y se reportan en CDMX invierno (ET-1, vigente desde 2026-11-01)."""
import sys, glob, json, os
import pandas as pd
import numpy as np

D = sys.argv[1]
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

def load_binance(sym):
    fs = sorted(glob.glob(os.path.join(D, "binance", f"{sym}-1m-*.csv")))
    df = pd.concat([pd.read_csv(f, header=None) for f in fs])
    t = df[0].astype("int64")
    unit = "us" if t.iloc[0] > 1e14 else "ms"
    df.index = pd.to_datetime(t, unit=unit, utc=True)
    df = df.rename(columns={1: "o", 2: "h", 3: "l", 4: "c", 7: "qv"})[["o", "h", "l", "c", "qv"]]
    return df.sort_index()

def load_yahoo(name):
    j = json.load(open(os.path.join(D, "yahoo", name + ".json")))["chart"]["result"][0]
    q = j["indicators"]["quote"][0]
    df = pd.DataFrame({"o": q["open"], "h": q["high"], "l": q["low"], "c": q["close"]},
                      index=pd.to_datetime(j["timestamp"], unit="s", utc=True)).dropna()
    df = df[(df.h > 0) & (df.l > 0)]
    return df

def bps_range(df):
    return (df.h - df.l) / df.c * 1e4

def resample5(df):
    r = df.resample("5min").agg({"o": "first", "h": "max", "l": "min", "c": "last"}).dropna()
    return r

def by_et_hour(series, mask=None):
    s = series if mask is None else series[mask]
    et = s.index.tz_convert("America/New_York")
    g = s.groupby(et.hour)
    return g.mean()

def table(name, r1=None, r5=None, qv=None, weekday_only=True):
    out = {}
    for lab, r in (("1m", r1), ("5m", r5)):
        if r is None:
            continue
        et = r.index.tz_convert("America/New_York")
        m = et.dayofweek < 5 if weekday_only else np.ones(len(r), bool)
        out[f"{lab}_bps_lv"] = r[m].groupby(et[m].hour).mean()
        out[f"{lab}_bps_p50"] = r[m].groupby(et[m].hour).median()
        out[f"n_{lab}"] = r[m].groupby(et[m].hour).size()
    t = pd.DataFrame(out)
    t.index.name = "ET_h"
    t.insert(0, "CDMX_inv_h", (t.index - 1) % 24)
    t.insert(1, "UTC_inv_h", (t.index + 5) % 24)
    print(f"\n=== {name} (lun-vie, por hora ET; CDMX invierno = ET-1; UTC = ET+5) ===")
    print(t.round(2).to_string())
    return t

res = {}
for sym in ["BTCUSDT", "ETHUSDT", "PAXGUSDT", "EURUSDT"]:
    df = load_binance(sym)
    r1 = bps_range(df)
    r5 = bps_range(resample5(df))
    et = df.index.tz_convert("America/New_York")
    wd = et.dayofweek < 5
    t = table(sym + " Binance (3 meses ago-oct 2026)", r1, r5)
    # volumen por hora (share)
    qv = df.qv.groupby(et.hour).mean()
    print("volumen medio/min por hora ET (USD, todos los días):", (qv / 1e6).round(2).to_dict())
    # semana vs fin de semana (UTC calendario)
    utcdow = df.index.dayofweek
    r5i = r5.index.dayofweek
    print("1m rango medio bps  L-V vs Sáb vs Dom:",
          round(r1[utcdow < 5].mean(), 2), round(r1[utcdow == 5].mean(), 2), round(r1[utcdow == 6].mean(), 2))
    print("5m rango medio bps  L-V vs Sáb vs Dom:",
          round(r5[r5i < 5].mean(), 2), round(r5[r5i == 5].mean(), 2), round(r5[r5i == 6].mean(), 2))
    print("volumen/min medio (M USD) L-V vs Sáb vs Dom:",
          round(df.qv[utcdow < 5].mean() / 1e6, 3), round(df.qv[utcdow == 5].mean() / 1e6, 3), round(df.qv[utcdow == 6].mean() / 1e6, 3))
    # fin de semana por hora (sab+dom, UTC) 5m
    we = r5[r5i >= 5]
    print("fin de semana 5m bps por hora CDMX (UTC-6):",
          we.groupby((we.index.hour - 6) % 24).mean().round(1).to_dict())
    # retorno viernes 16:00 ET -> domingo 18:00 ET (equivalente al gap de CFDs tradicionales)
    c = df.c
    gaps = []
    for fri in pd.date_range(df.index[0].date(), df.index[-1].date(), freq="W-FRI"):
        a = pd.Timestamp(fri.date()).tz_localize("America/New_York") + pd.Timedelta(hours=17)
        b = a + pd.Timedelta(hours=49)
        try:
            pa = c.asof(a.tz_convert("UTC")); pb = c.asof(b.tz_convert("UTC"))
            if pd.notna(pa) and pd.notna(pb):
                gaps.append(abs(pb / pa - 1) * 1e4)
        except Exception:
            pass
    print(f"|mov| vie17ET->dom18ET (bps): n={len(gaps)} media={np.mean(gaps):.0f} mediana={np.median(gaps):.0f} max={np.max(gaps):.0f}")
    res[sym] = t

for name in ["EURUSD", "GBPUSD", "GC", "NQ", "ES"]:
    d5 = load_yahoo(name)
    r5 = bps_range(d5)
    r1 = None
    try:
        d1 = load_yahoo(name + "_1m")
        r1 = bps_range(d1)
    except Exception as e:
        print("sin 1m", name, e)
    print(f"\n{name}: 5m de {d5.index[0]} a {d5.index[-1]}  ({len(d5)} barras)")
    res[name] = table(name + " Yahoo", r1, r5)

# resumen por bloque CDMX invierno (ET-1)
blocks = {"Asia 18-02": list(range(18, 24)) + [0, 1], "Londres 02-07": list(range(2, 7)),
          "Solape 07-11": list(range(7, 11)), "NY tarde 11-15": list(range(11, 15)),
          "Cierre 15-17": [15, 16]}
rows = {}
for k, t in res.items():
    tt = t.set_index("CDMX_inv_h")
    rows[k] = {b: round(tt.loc[[h for h in hs if h in tt.index], "5m_bps_lv"].mean(), 2) for b, hs in blocks.items()}
    if "1m_bps_lv" in tt:
        rows[k].update({b + " 1m": round(tt.loc[[h for h in hs if h in tt.index], "1m_bps_lv"].mean(), 2) for b, hs in blocks.items()})
print("\n=== Rango medio 5m (bps) por bloque CDMX invierno, L-V ===")
print(pd.DataFrame(rows).T.to_string())
