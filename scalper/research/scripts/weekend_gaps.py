"""Gap de fin de semana (último close viernes -> primer open domingo) en datos Yahoo 5m. Uso: python3 -I weekend_gaps.py <data_dir>"""
import sys, os, json
import pandas as pd, numpy as np
D = sys.argv[1]
for n in ["EURUSD", "GBPUSD", "GC", "NQ", "ES"]:
    j = json.load(open(os.path.join(D, "yahoo", n + ".json")))["chart"]["result"][0]
    q = j["indicators"]["quote"][0]
    df = pd.DataFrame({"o": q["open"], "c": q["close"]}, index=pd.to_datetime(j["timestamp"], unit="s", utc=True)).dropna()
    dt = df.index.to_series().diff()
    idx = np.where(dt > pd.Timedelta(hours=36))[0]
    g = [abs(df.o.iloc[i] / df.c.iloc[i - 1] - 1) * 1e4 for i in idx]
    print(f"{n}: n={len(g)} gap medio={np.mean(g):.1f} bps mediana={np.median(g):.1f} max={np.max(g):.1f}")
