"""Calibra rango 5m de FX a partir del rango diario. Uso: python3 -I daily_calib.py <data_dir>
Idea: ratio k = (rango medio 5m L-V) / (rango diario medio) medido en GC y NQ (datos 5m fiables),
luego rango5m_FX ~= k * rango_diario_FX, repartido por bloque con la forma horaria de EURUSDT (Binance)."""
import sys, os, json, glob
import pandas as pd, numpy as np

D = sys.argv[1]

def yahoo(name):
    j = json.load(open(os.path.join(D, "yahoo", name + ".json")))["chart"]["result"][0]
    q = j["indicators"]["quote"][0]
    df = pd.DataFrame({"h": q["high"], "l": q["low"], "c": q["close"]},
                      index=pd.to_datetime(j["timestamp"], unit="s", utc=True)).dropna()
    return df[(df.h > 0) & (df.l > 0)]

daily = {}
for n in ["EURUSD", "GBPUSD", "GC", "NQ", "ES"]:
    d = yahoo(n + "_1d")
    rng = ((d.h - d.l) / d.c * 1e4)
    daily[n] = rng.mean()
    print(f"{n}: rango diario medio {rng.mean():.1f} bps, mediana {rng.median():.1f} bps, n={len(d)}  (precio ult {d.c.iloc[-1]:.5g})")

ks = {}
for n in ["GC", "NQ", "ES"]:
    d5 = yahoo(n)
    r5 = (d5.h - d5.l) / d5.c * 1e4
    et = r5.index.tz_convert("America/New_York")
    m = et.dayofweek < 5
    ks[n] = r5[m].mean() / daily[n]
    print(f"{n}: rango 5m medio {r5[m].mean():.2f} bps -> k = {ks[n]:.4f}")
k = np.mean(list(ks.values()))
print(f"k medio = {k:.4f}")

# forma horaria EURUSDT (Binance) para FX
fs = sorted(glob.glob(os.path.join(D, "binance", "EURUSDT-1m-*.csv")))
df = pd.concat([pd.read_csv(f, header=None) for f in fs])
t = df[0].astype("int64")
df.index = pd.to_datetime(t, unit="us" if t.iloc[0] > 1e14 else "ms", utc=True)
r = df.resample("5min").agg({1: "first", 2: "max", 3: "min", 4: "last"}).dropna()
r5 = (r[2] - r[3]) / r[4] * 1e4
et = r5.index.tz_convert("America/New_York")
m = et.dayofweek < 5
prof = r5[m].groupby(et[m].hour).mean()
prof = prof / prof.mean()
blocks = {"Asia 18-02": list(range(19, 24)) + [0, 1, 2], "Londres 02-07": [3, 4, 5, 6, 7],
          "Solape 07-11": [8, 9, 10, 11], "NY tarde 11-15": [12, 13, 14, 15], "Cierre 15-17": [16, 17]}
# (horas ET; CDMX invierno = ET-1)
for n in ["EURUSD", "GBPUSD"]:
    base = k * daily[n]
    print(n, "rango 5m medio estimado", round(base, 2), "bps;",
          {b: round(base * prof.loc[h].mean(), 2) for b, h in blocks.items()})
