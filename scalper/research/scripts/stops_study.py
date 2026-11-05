"""Estudio de politicas de salida (Stop Manager) sobre velas 1m de Binance (BTCUSDT, ETHUSDT).
Uso: python3 -I stops_study.py <data_dir> <out_txt>
- Entradas: (1) aleatorias (direccion por moneda al aire) y (2) breakout 20 barras.
- ATR14 del timeframe de senal (1m o 5m), fijo al entrar. Trayectoria simulada SIEMPRE en velas 1m.
- Supuestos conservadores intrabarra: stop antes que target/parcial en la misma vela; BE/trailing
  se actualizan al cierre de la vela 1m (aplican desde la siguiente). Gap: si la apertura cruza el stop, fill en apertura.
- Costo round-trip = spread (CFD sin comision) como fraccion del precio.
"""
import sys, glob, os
import numpy as np, pandas as pd

DATA, OUT = sys.argv[1], sys.argv[2]
rng = np.random.default_rng(12345)

def load(sym):
    fs = sorted(glob.glob(os.path.join(DATA, f"{sym}-1m-2026-*.csv")))
    fs = [f for f in fs if any(m in f for m in ("2026-08", "2026-09", "2026-10"))]
    df = pd.concat([pd.read_csv(f, header=None, usecols=[0,1,2,3,4]) for f in fs])
    df.columns = ["t","o","h","l","c"]
    ts = df.t.values
    unit = "us" if ts[0] > 1e14 else "ms"
    df.index = pd.to_datetime(ts, unit=unit, utc=True)
    return df[["o","h","l","c"]].astype(float).sort_index()

def atr(df, n=14):
    pc = df.c.shift(1)
    tr = np.maximum(df.h - df.l, np.maximum((df.h - pc).abs(), (df.l - pc).abs()))
    return tr.ewm(alpha=1/n, adjust=False).mean()

def resample5(df):
    return df.resample("5min", label="left", closed="left").agg({"o":"first","h":"max","l":"min","c":"last"}).dropna()

# ---------------- politicas ----------------
# cada politica: dict(sl, tp, be, trail, step, partial, part_be)
P = {
 "a_fijo_1.5/1.5":        dict(tp=1.5),
 "b_BE@0.5":              dict(tp=1.5, be=0.5),
 "c_BE@1.0":              dict(tp=1.5, be=1.0),
 "d_BE@1.5(=nunca)":      dict(tp=1.5, be=1.49),   # practicamente nunca antes del TP
 "e1_BE@1+trail1.0":      dict(tp=None, be=1.0, trail=1.0),
 "e2_BE@1+trail2.0":      dict(tp=None, be=1.0, trail=2.0),
 "e3_BE@1+trail3.0":      dict(tp=None, be=1.0, trail=3.0),
 "e4_trail1.0_sinBE_tp3": dict(tp=3.0, trail_from_start=1.0),
 "f1_parcial50@1":        dict(tp=1.5, partial=1.0),
 "f2_parcial50@1+BE":     dict(tp=1.5, partial=1.0, part_be=True),
 "g_escalones0.5_tp3":    dict(tp=3.0, step=0.5),
}
SL = 1.5

def simulate(paths, cost_atr, pol, slip_atr=None):
    """paths: dict of arrays N x T normalizados (unidades ATR, direccion 'long'). Devuelve pnl bruto en ATR (tamano 1)."""
    op, hi, lo, cl = paths["o"], paths["h"], paths["l"], paths["c"]
    N, T = op.shape
    stop = np.full(N, -SL)
    tp = pol.get("tp"); tp = np.inf if tp is None else tp
    be = pol.get("be"); trail = pol.get("trail"); tfs = pol.get("trail_from_start")
    step = pol.get("step"); partial = pol.get("partial"); part_be = pol.get("part_be", False)
    active = np.ones(N, bool); size = np.ones(N); pnl = np.zeros(N); mfe = np.zeros(N)
    be_on = np.zeros(N, bool); part_done = np.zeros(N, bool); nbars = np.full(N, T)
    if slip_atr is None: slip_atr = np.zeros(N)
    for t in range(T):
        a = active
        o, h, l = op[:, t], hi[:, t], lo[:, t]
        # 1) stop (gap -> apertura)
        gap = a & (o <= stop); hit = a & ~gap & (l <= stop)
        px = np.where(gap, o, stop) - slip_atr  # deslizamiento de la orden stop (orden a mercado al dispararse)
        ex = gap | hit
        pnl[ex] += size[ex] * px[ex]; active = active & ~ex; nbars[ex] = t + 1
        a = active
        # 2) parcial
        if partial is not None:
            pp = a & ~part_done & (h >= partial)
            fill = np.maximum(o, partial)
            pnl[pp] += 0.5 * fill[pp]; size[pp] = 0.5; part_done |= pp
            if part_be:
                stop[pp] = np.maximum(stop[pp], cost_atr[pp])
        # 3) target
        th = a & (h >= tp)
        fill = np.maximum(o, tp)
        pnl[th] += size[th] * fill[th]; active = active & ~th; nbars[th] = t + 1
        a = active
        # 4) actualizar stop al cierre de la vela (aplica desde la siguiente)
        mfe = np.where(a, np.maximum(mfe, h), mfe)
        if be is not None:
            trig = a & (mfe >= be)
            stop[trig] = np.maximum(stop[trig], cost_atr[trig]); be_on |= trig
            if trail is not None:
                tr = a & be_on
                stop[tr] = np.maximum(stop[tr], mfe[tr] - trail)
        if tfs is not None:
            stop[a] = np.maximum(stop[a], mfe[a] - tfs)
        if step is not None:
            k = np.floor(mfe / step) * step
            lock = np.where(mfe >= 1.0, np.maximum(k - 1.0, 0) , -np.inf)
            lock = np.where(lock == 0, cost_atr, lock)
            m = a & np.isfinite(lock)
            stop[m] = np.maximum(stop[m], lock[m])
    # salida por tiempo al cierre
    rem = active
    pnl[rem] += size[rem] * cl[rem, -1]
    return pnl, nbars

def build_paths(df1, idx, direction, atr_at, T):
    """idx: posicion (en df1) de la primera vela 1m de la operacion; entrada al open de esa vela."""
    O, H, L, C = (df1[k].values for k in "ohlc")
    n = len(O)
    ok = idx + T < n
    idx, direction, atr_at = idx[ok], direction[ok], atr_at[ok]
    E = O[idx]
    J = idx[:, None] + np.arange(T)[None, :]
    d = direction[:, None]; A = atr_at[:, None]; Ec = E[:, None]
    o = (O[J] - Ec) * d / A; c = (C[J] - Ec) * d / A
    h_ = np.where(d > 0, H[J] - Ec, -(L[J] - Ec)) / A
    l_ = np.where(d > 0, L[J] - Ec, -(H[J] - Ec)) / A
    return dict(o=o, h=h_, l=l_, c=c), E, atr_at, idx

def stats(pnl_atr, cost_atr, atr_px, E, days):
    net_atr = pnl_atr - cost_atr
    R = net_atr / SL
    bps = net_atr * atr_px / E * 1e4
    eq = np.cumsum(R); dd = np.max(np.maximum.accumulate(eq) - eq)
    # bootstrap por dia (bloques) para IC de la expectativa
    ud = np.unique(days); g = {d_: np.where(days == d_)[0] for d_ in ud}
    bs = []
    for _ in range(300):
        pick = rng.choice(ud, len(ud))
        ii = np.concatenate([g[p] for p in pick]); bs.append(R[ii].mean())
    lo_, hi_ = np.percentile(bs, [2.5, 97.5])
    return dict(n=len(R), ER=R.mean(), ER_lo=lo_, ER_hi=hi_, Ebps=bps.mean(), sdR=R.std(),
                win=(R > 1e-6).mean(), ge0=(R >= -1e-6).mean(), maxDD_R=dd, gross_R=(pnl_atr/SL).mean())

def run(sym, tf, entry, cost_frac, out, slip_mult=0.5, floor_mult=3.34):
    df1 = load(sym)
    if tf == "1m":
        dfs = df1; T = 60
    else:
        dfs = resample5(df1); T = 180
    A = atr(dfs).values
    # mapa de cada vela de senal -> posicion en df1 de la vela 1m siguiente al cierre de la vela de senal
    pos_next = df1.index.searchsorted(dfs.index + pd.Timedelta(tf.replace("m","min")))
    ns = len(dfs)
    if entry == "random":
        every = 10 if tf == "1m" else 3
        sel = np.arange(30, ns - 1)
        sel = sel[rng.random(len(sel)) < 1.0/every]
        direction = rng.choice([-1.0, 1.0], len(sel))
    else:  # breakout 20 barras con enfriamiento 20 barras
        c = dfs.c.values; hh = dfs.h.rolling(20).max().shift(1).values; ll = dfs.l.rolling(20).min().shift(1).values
        sig = np.where(c > hh, 1.0, np.where(c < ll, -1.0, 0.0))
        sel, direction, last = [], [], -10**9
        for i in range(30, ns - 1):
            if sig[i] != 0 and i - last >= 20:
                sel.append(i); direction.append(sig[i]); last = i
        sel = np.array(sel); direction = np.array(direction)
    idx = pos_next[sel]; atr_at = A[sel]
    good = idx < len(df1)
    a0 = atr_at[good]
    E0 = df1.o.values[idx[good]]
    atr_raw = a0.copy()
    if floor_mult:  # piso: 1.5*ATR >= 5*costo  -> costo <= 0.2R
        a0 = np.maximum(a0, floor_mult * cost_frac * E0)
    paths, E, atr_at, idx = build_paths(df1, idx[good], direction[good], a0, T)
    floored = np.mean(a0[:len(E)] > atr_raw[:len(E)]) if len(E) else 0
    cost_atr = cost_frac * E / atr_at
    slip_atr = slip_mult * cost_atr
    days = df1.index[idx].floor("D").values.astype("int64")
    rows = []
    for name, pol in P.items():
        pnl, nb = simulate(paths, cost_atr, pol, slip_atr)
        s = stats(pnl, cost_atr, atr_at, E, days); s["policy"] = name; s["hold"] = nb.mean()
        rows.append(s)
    r = pd.DataFrame(rows).set_index("policy")
    hdr = (f"\n### {sym} TF={tf} entrada={entry} costo_rt={cost_frac*1e4:.1f}bps  N={len(E)}  "
           f"ATRef_mediana={np.median(atr_at/E)*1e4:.1f}bps  costo/R mediano={np.median(cost_atr)/SL:.3f}R  slip={slip_mult}xcosto  piso_ATR={floor_mult} (aplicado en {floored:.0%})  max_hold={T}min")
    out.write(hdr + "\n")
    out.write(r[["n","gross_R","ER","ER_lo","ER_hi","Ebps","sdR","win","ge0","maxDD_R","hold"]].round(3).to_string() + "\n")
    out.flush()
    return r

def mae_analysis(sym, tf, out):
    """MAE (en ATR) de operaciones ganadoras bajo politica (a) con entrada breakout, y P(volver a BE | MFE>=x)."""
    df1 = load(sym)
    dfs = df1 if tf == "1m" else resample5(df1); T = 60 if tf == "1m" else 180
    A = atr(dfs).values
    pos_next = df1.index.searchsorted(dfs.index + pd.Timedelta(tf.replace("m","min")))
    for entry in ("random", "breakout"):
        ns = len(dfs)
        if entry == "random":
            sel = np.arange(30, ns-1); sel = sel[rng.random(len(sel)) < 1/5]; direction = rng.choice([-1.0,1.0], len(sel))
        else:
            c = dfs.c.values; hh = dfs.h.rolling(20).max().shift(1).values; ll = dfs.l.rolling(20).min().shift(1).values
            sig = np.where(c > hh, 1.0, np.where(c < ll, -1.0, 0.0)); sel=[];direction=[];last=-10**9
            for i in range(30, ns-1):
                if sig[i]!=0 and i-last>=20: sel.append(i);direction.append(sig[i]);last=i
            sel=np.array(sel);direction=np.array(direction)
        idx = pos_next[sel]; g = idx < len(df1)
        paths, E, atr_at, idx = build_paths(df1, idx[g], direction[g], A[sel][g], T)
        hi, lo, cl = paths["h"], paths["l"], paths["c"]
        N = hi.shape[0]
        # primera vela que toca -1.5 o +1.5
        hitS = (lo <= -SL); hitT = (hi >= SL)
        fS = np.where(hitS.any(1), hitS.argmax(1), 10**6); fT = np.where(hitT.any(1), hitT.argmax(1), 10**6)
        win = fT < fS
        mae_w = np.array([(-lo[i, :fT[i]+1].min()) for i in np.where(win)[0]])
        out.write(f"\n### MAE {sym} TF={tf} entrada={entry} N={N} ganadoras(TP antes de SL)={win.mean():.3f}\n")
        out.write("  MAE de ganadoras (ATR) p25/p50/p75/p90: " + " / ".join(f"{q:.2f}" for q in np.percentile(mae_w,[25,50,75,90])) + "\n")
        # P(regresa a entrada antes de TP | MFE alcanzo x antes de SL)
        for x in (0.25, 0.5, 0.75, 1.0, 1.25):
            cnt=0; back=0
            for i in range(N):
                end = min(fS[i], fT[i], T-1)
                hx = np.where(hi[i, :end+1] >= x)[0]
                if len(hx)==0 or (fS[i] <= hx[0]): continue
                if fT[i] == hx[0]: continue  # alcanzo x y TP en la misma vela
                cnt += 1
                seg_end = min(fT[i], T-1)
                if (lo[i, hx[0]+1:seg_end+1] <= 0).any() and ( (np.where(lo[i, hx[0]+1:]<=0)[0][0]+hx[0]+1) < fT[i]):
                    back += 1
            rw = (SL - x)/SL
            out.write(f"  MFE>={x:.2f}ATR: n={cnt}  P(regresa a 0 antes de TP)={back/max(cnt,1):.3f}  (paseo aleatorio teorico={rw:.3f})\n")
    out.flush()

def noise(sym, out):
    df1 = load(sym); r1 = np.log(df1.c).diff().dropna()
    d5 = resample5(df1); r5 = np.log(d5.c).diff().dropna()
    def vr(r, q):
        rq = r.rolling(q).sum().dropna()[::q]
        return rq.var() / (q * r.var())
    rng_bps = ((df1.h - df1.l) / df1.c * 1e4)
    out.write(f"\n### Ruido {sym}: rango 1m p50={rng_bps.median():.2f}bps media={rng_bps.mean():.2f}bps | ATR14(1m) mediana={np.nanmedian(atr(df1)/df1.c)*1e4:.2f}bps | ATR14(5m) mediana={np.nanmedian(atr(d5)/d5.c)*1e4:.2f}bps\n")
    out.write(f"  autocorr lag1 1m={r1.autocorr(1):.4f}  5m={r5.autocorr(1):.4f} | VR(5) de 1m={vr(r1,5):.3f}  VR(15)={vr(r1,15):.3f}  VR(60)={vr(r1,60):.3f}\n")
    out.flush()

if __name__ == "__main__":
    with open(OUT, "w") as out:
        for sym in ("BTCUSDT", "ETHUSDT", "PAXGUSDT"):
            noise(sym, out)
        for sym in ("BTCUSDT", "ETHUSDT"):
            mae_analysis(sym, "5m", out)
        out.write("\n\n======== PRINCIPAL: slip=0.5x costo, piso ATR (costo<=0.2R) ========\n")
        for sym, cost in (("BTCUSDT", 0.0003), ("ETHUSDT", 0.0005)):
            for tf in ("1m", "5m"):
                for entry in ("random", "breakout"):
                    run(sym, tf, entry, cost, out)
        out.write("\n\n======== SENSIBILIDAD ========\n")
        for entry in ("random", "breakout"):
            run("BTCUSDT", "5m", entry, 0.0003, out, slip_mult=0.0)         # sin deslizamiento (optimista)
            run("BTCUSDT", "1m", entry, 0.0003, out, floor_mult=None)       # 1m sin piso
            for c in (0.0, 0.0005):
                run("BTCUSDT", "5m", entry, c, out)
