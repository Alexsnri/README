# (1) diferencias pareadas vs politica (a) con bootstrap por dia; (2) ruido y estudio grueso en datos Yahoo (oro, NQ, ES, EURUSD, GBPUSD).
import sys, json, numpy as np, pandas as pd, importlib.util
scripts, binance, yahoo = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("ss", scripts + "/stops_study.py")
sys.argv = ["x", binance, "/dev/null"]
ss = importlib.util.module_from_spec(spec); spec.loader.exec_module(ss)
rng = np.random.default_rng(99)
KEY = ["b_BE@0.5","c_BE@1.0","e1_BE@1+trail1.0","e2_BE@1+trail2.0","e4_trail1.0_sinBE_tp3","f1_parcial50@1","f2_parcial50@1+BE","g_escalones0.5_tp3"]

def trades(df1, tf, entry, cost_frac, T, floor_mult=3.34, path_df=None):
    dfs = df1 if tf == "1m" else ss.resample5(df1)
    pdf = df1 if path_df is None else path_df
    A = ss.atr(dfs).values
    step = pd.Timedelta(tf.replace("m","min"))
    pos_next = pdf.index.searchsorted(dfs.index + step)
    ns = len(dfs)
    if entry == "random":
        sel = np.arange(30, ns-1); sel = sel[rng.random(len(sel)) < 1/3]; d = rng.choice([-1.0,1.0], len(sel))
    else:
        c = dfs.c.values; hh = dfs.h.rolling(20).max().shift(1).values; ll = dfs.l.rolling(20).min().shift(1).values
        sig = np.where(c > hh, 1.0, np.where(c < ll, -1.0, 0.0)); sel=[]; d=[]; last=-10**9
        for i in range(30, ns-1):
            if sig[i]!=0 and i-last>=20: sel.append(i); d.append(sig[i]); last=i
        sel=np.array(sel); d=np.array(d)
    idx = pos_next[sel]; g = idx + T < len(pdf)
    # evitar entradas cuyo camino cruce un hueco de mercado (> 15 min sin datos)
    ti = pdf.index.values
    idx, d, a0 = idx[g], d[g], A[sel][g]
    span = (ti[idx + T - 1] - ti[idx]) / np.timedelta64(1, "m")
    ok = span <= (T * (5 if path_df is not None else 1)) * 1.2
    idx, d, a0 = idx[ok], d[ok], a0[ok]
    E0 = pdf.o.values[idx]
    if floor_mult: a0 = np.maximum(a0, floor_mult * cost_frac * E0)
    paths, E, atr_at, idx = ss.build_paths(pdf, idx, d, a0, T)
    cost_atr = cost_frac * E / atr_at
    days = pdf.index[idx].floor("D").values.astype("int64")
    out = {}
    for name, pol in ss.P.items():
        pnl, _ = ss.simulate(paths, cost_atr, pol, 0.5 * cost_atr)
        out[name] = (pnl - cost_atr) / ss.SL
    return out, days, np.median(atr_at / E) * 1e4, np.median(cost_atr) / ss.SL

def paired(out, days, label):
    ud = np.unique(days); grp = {x: np.where(days == x)[0] for x in ud}
    base = out["a_fijo_1.5/1.5"]
    s = f"{label}: E[R](a)={base.mean():+.3f} sd={base.std():.2f} | dif vs (a) [IC95 bootstrap por dia]:\n"
    for k in KEY:
        dif = out[k] - base; bs = []
        for _ in range(400):
            ii = np.concatenate([grp[p] for p in rng.choice(ud, len(ud))]); bs.append(dif[ii].mean())
        lo, hi = np.percentile(bs, [2.5, 97.5])
        s += f"    {k:24s} {dif.mean():+.3f} [{lo:+.3f},{hi:+.3f}]  sdR={out[k].std():.2f}  P(R>=0)={np.mean(out[k] >= -1e-6):.2f}\n"
    return s

def load_y(name):
    r = json.load(open(f"{yahoo}/{name}.json"))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    df = pd.DataFrame(dict(o=q["open"], h=q["high"], l=q["low"], c=q["close"]), index=pd.to_datetime(r["timestamp"], unit="s", utc=True)).dropna()
    df = df[(df.h >= df.l) & (df.h > 0)]
    return df

res = []
for sym, cost in (("BTCUSDT", 0.0003), ("ETHUSDT", 0.0005)):
    df1 = ss.load(sym)
    for entry in ("random", "breakout"):
        o, dd, a, c = trades(df1, "5m", entry, cost, 180)
        res.append(paired(o, dd, f"{sym} 5m {entry} costo={cost*1e4:.0f}bps N={len(dd)} ATRef={a:.1f}bps costo/R={c:.2f}"))
# Ruido Yahoo
res.append("\n# Ruido (Yahoo, ~7 dias 1m y ~60 dias 5m; solo horas con datos)\n")
for nm in ("GC", "NQ", "ES", "EURUSD", "GBPUSD"):
    for suf in ("_1m", ""):
        try:
            df = load_y(nm + suf)
        except Exception as ex:
            res.append(f"{nm}{suf}: error {ex}\n"); continue
        a = ss.atr(df); rngb = (df.h - df.l) / df.c * 1e4
        ac = np.log(df.c).diff().autocorr(1)
        res.append(f"{nm}{suf}: barras={len(df)} {df.index[0].date()}..{df.index[-1].date()} rango p50={rngb.median():.2f}bps ATR14 mediana={np.nanmedian(a/df.c)*1e4:.2f}bps autocorr1={ac:+.3f}\n")
# Estudio grueso con barras 5m de Yahoo (camino tambien en 5m: menos preciso)
res.append("\n# Estudio grueso Yahoo 5m (ATR y camino en 5m; T=36 barras=3h)\n")
for nm, cost in (("GC", 0.0001), ("NQ", 0.0001), ("EURUSD", 0.00006)):
    df = load_y(nm)
    df5 = df  # ya es 5m
    for entry in ("random", "breakout"):
        # con TF=1m sobre df5 tratamos cada barra 5m como 'barra' de senal y de camino
        o, dd, a, c = trades(df5, "1m", entry, cost, 36, path_df=None) if False else (None,None,None,None)
        dfs = df5; A = ss.atr(dfs).values; ns = len(dfs)
        if entry == "random":
            sel = np.arange(30, ns-37); sel = sel[rng.random(len(sel)) < 1/2]; d = rng.choice([-1.0,1.0], len(sel))
        else:
            cc = dfs.c.values; hh = dfs.h.rolling(20).max().shift(1).values; ll = dfs.l.rolling(20).min().shift(1).values
            sig = np.where(cc > hh, 1.0, np.where(cc < ll, -1.0, 0.0)); sel=[]; d=[]; last=-10**9
            for i in range(30, ns-37):
                if sig[i]!=0 and i-last>=20: sel.append(i); d.append(sig[i]); last=i
            sel=np.array(sel); d=np.array(d)
        idx = sel + 1
        ti = dfs.index.values; span = (ti[idx+35]-ti[idx])/np.timedelta64(1,"m"); ok = span <= 36*5*1.2
        idx, d, a0 = idx[ok], d[ok], A[sel][ok]
        E0 = dfs.o.values[idx]; a0 = np.maximum(a0, 3.34*cost*E0)
        paths, E, atr_at, idx = ss.build_paths(dfs, idx, d, a0, 36)
        cost_atr = cost*E/atr_at; days = dfs.index[idx].floor("D").values.astype("int64")
        out = {n: (ss.simulate(paths, cost_atr, p, 0.5*cost_atr)[0]-cost_atr)/ss.SL for n,p in ss.P.items()}
        res.append(paired(out, days, f"{nm} 5m {entry} costo={cost*1e4:.1f}bps N={len(E)} ATRef={np.median(atr_at/E)*1e4:.1f}bps costo/R={np.median(cost_atr)/ss.SL:.2f}"))
open(scripts + "/paired_output.txt", "w").write("".join(res))
print("".join(res))
