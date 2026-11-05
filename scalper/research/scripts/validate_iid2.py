# Mecanismo del sesgo: llenar stops exactamente al nivel ignora el "overshoot" del precio discreto.
import sys, numpy as np, importlib.util
spec = importlib.util.spec_from_file_location("ss", sys.argv[1] + "/stops_study.py")
sys.argv = ["x", "/nonexistent", "/dev/null"]
ss = importlib.util.module_from_spec(spec); spec.loader.exec_module(ss)
rng = np.random.default_rng(2)
T = 60
for sub in (5, 30, 300):
    res = {k: [] for k in ("a_fijo_1.5/1.5", "e1_BE@1+trail1.0", "e4_trail1.0_sinBE_tp3")}
    for chunk in range(10):
        N = 3000
        inc = rng.standard_normal((N, T*sub)) * (1/np.sqrt(sub)) * 0.8
        p = np.cumsum(inc, 1).reshape(N, T, sub)
        o = np.concatenate([np.zeros((N,1)), p[:, :-1, -1]], 1)
        h = np.maximum(p.max(2), o); l = np.minimum(p.min(2), o); c = p[:, :, -1]
        for k in res:
            pnl, _ = ss.simulate(dict(o=o,h=h,l=l,c=c), np.zeros(N), ss.P[k]); res[k].append(pnl/1.5)
    print("sub=",sub, {k: f"{np.concatenate(v).mean():+.4f}" for k,v in res.items()}, "overshoot teorico ~", round(0.5826*0.8/np.sqrt(sub)/1.5,4),"R por salida en stop")
