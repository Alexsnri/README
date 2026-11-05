# Valida el motor: en un paseo aleatorio sintetico, toda politica debe dar gross ~ 0.
import sys, numpy as np, pandas as pd
sys.path.insert(0, sys.argv[1])
import importlib.util
spec = importlib.util.spec_from_file_location("ss", sys.argv[1] + "/stops_study.py")
sys.argv = ["x", "/nonexistent", "/dev/null"]
ss = importlib.util.module_from_spec(spec); spec.loader.exec_module(ss)
rng = np.random.default_rng(7)
nb, sub = 130000, 30
inc = rng.standard_normal(nb*sub) * 0.0005/np.sqrt(sub)
lp = np.log(60000) + np.cumsum(inc)
P = np.exp(lp).reshape(nb, sub)
o = np.r_[60000, P[:-1, -1]]; h = np.maximum(P.max(1), o); l = np.minimum(P.min(1), o); c = P[:, -1]
df = pd.DataFrame(dict(o=o, h=h, l=l, c=c), index=pd.date_range("2026-01-01", periods=nb, freq="1min", tz="UTC"))
ss.load = lambda sym: df
import io
out = io.StringIO()
for tf in ("1m","5m"):
    for e in ("random","breakout"):
        ss.run("SYN", tf, e, 0.0, out)
print(out.getvalue())
