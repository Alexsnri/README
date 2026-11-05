import sys, numpy as np, importlib.util
spec = importlib.util.spec_from_file_location("ss", sys.argv[1] + "/stops_study.py")
sys.argv = ["x", "/nonexistent", "/dev/null"]
ss = importlib.util.module_from_spec(spec); spec.loader.exec_module(ss)
rng = np.random.default_rng(1)
N, T, sub = 40000, 60, 30
for atr_true in (1.0,):
    inc = rng.standard_normal((N, T*sub)) * (1/np.sqrt(sub)) * 0.8  # 1m sigma = 0.8 ATR
    p = np.cumsum(inc, 1).reshape(N, T, sub)
    o = np.concatenate([np.zeros((N,1)), p[:, :-1, -1]], 1)
    h = np.maximum(p.max(2), o); l = np.minimum(p.min(2), o); c = p[:, :, -1]
    paths = dict(o=o, h=h, l=l, c=c); cost = np.zeros(N)
    for name, pol in ss.P.items():
        pnl, nb = ss.simulate(paths, cost, pol)
        print(f"{name:24s} gross_R={pnl.mean()/1.5:+.4f}  se={pnl.std()/1.5/np.sqrt(N):.4f}")
