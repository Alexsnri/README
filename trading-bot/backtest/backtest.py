"""
Backtest del sistema "Hydra" (misma lógica que el EA de MT5 y el script de TradingView).

Datos: velas diarias (Yahoo Finance JSON). Señales al cierre, ejecución en la apertura siguiente.
Incluye costo por operación (spread + comisión aproximados) para no inflar resultados.

Uso: python backtest.py <carpeta_datos> [riesgo_por_trade_pct]
"""
import json, sys, os, math
import numpy as np
import pandas as pd

# Símbolo de datos -> (nombre Exness, clase, costo ida+vuelta en fracción del precio)
UNIVERSE = {
    "EURUSDX": ("EURUSD", "fx", 0.00012), "GBPUSDX": ("GBPUSD", "fx", 0.00015),
    "USDJPYX": ("USDJPY", "fx", 0.00012), "AUDUSDX": ("AUDUSD", "fx", 0.00015),
    "USDCADX": ("USDCAD", "fx", 0.00015), "GCF": ("XAUUSD", "metal", 0.00025),
    "SIF": ("XAGUSD", "metal", 0.0006), "CLF": ("USOIL", "energy", 0.0006),
    "GSPC": ("US500", "index", 0.0002), "NDX": ("USTEC", "index", 0.0002),
    "DJI": ("US30", "index", 0.0002), "GDAXI": ("DE30", "index", 0.0003),
    "BTC-USD": ("BTCUSD", "crypto", 0.0015),
}

def load(path):
    d = json.load(open(path))["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    df = pd.DataFrame({"o": q["open"], "h": q["high"], "l": q["low"], "c": q["close"]},
                      index=pd.to_datetime(d["timestamp"], unit="s").normalize())
    df = df.dropna()
    df = df[(df.h >= df.l) & (df.c > 0)]
    return df[~df.index.duplicated(keep="last")]

def atr(df, n=20):
    pc = df.c.shift()
    tr = pd.concat([df.h - df.l, (df.h - pc).abs(), (df.l - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()

def rsi(c, n=2):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))

def indicators(df):
    df = df.copy()
    df["atr"] = atr(df)
    df["dc_hi"] = df.h.rolling(55).max().shift()   # canal Donchian de entrada (excluye la vela actual)
    df["dc_lo"] = df.l.rolling(55).min().shift()
    df["ex_hi"] = df.h.rolling(20).max().shift()   # canal de salida
    df["ex_lo"] = df.l.rolling(20).min().shift()
    df["sma200"] = df.c.rolling(200).mean()
    df["sma5"] = df.c.rolling(5).mean()
    df["ema50"] = df.c.ewm(span=50, adjust=False).mean()
    df["ema200"] = df.c.ewm(span=200, adjust=False).mean()
    df["rsi2"] = rsi(df.c, 2)
    df["mom"] = sum(np.sign(df.c / df.c.shift(n) - 1) for n in (21, 63, 126, 252)) / 4
    return df

# ---------------- Estrategias: devuelven (dirección, stop) o None ----------------
def s_donchian(r, cls):
    # Breakout de 55 días (Tortugas) filtrado por tendencia larga
    if r.c > r.dc_hi and r.ema50 > r.ema200: return 1, r.c - 2.5 * r.atr
    if r.c < r.dc_lo and r.ema50 < r.ema200 and cls != "index": return -1, r.c + 2.5 * r.atr
    return None

def s_tsmom(r, cls):
    # Momentum de series de tiempo (Moskowitz-Ooi-Pedersen): consenso de 4 horizontes
    if r.mom >= 0.75 and r.c > r.ema50: return 1, r.c - 3 * r.atr
    if r.mom <= -0.75 and r.c < r.ema50 and cls != "index": return -1, r.c + 3 * r.atr
    return None

def s_meanrev(r, cls):
    # RSI(2) de Connors: comprar retrocesos en tendencia alcista (índices y oro)
    if cls in ("index", "metal") and r.c > r.sma200 and r.rsi2 < 10: return 1, r.c - 2.5 * r.atr
    return None

STRATS = {"donchian": s_donchian, "tsmom": s_tsmom, "meanrev": s_meanrev}

class Learner:
    """Aprendizaje adaptativo: cada brazo (estrategia x símbolo) recibe un multiplicador de riesgo
    según la expectativa de sus últimos N trades en múltiplos de R. Nunca llega a cero (sigue
    explorando con poco riesgo) y nunca pasa de 1.5x (para no apostar de más a una racha)."""
    def __init__(self, window=30, min_trades=8):
        self.hist, self.window, self.min_trades = {}, window, min_trades
    def mult(self, arm):
        h = self.hist.get(arm, [])[-self.window:]
        if len(h) < self.min_trades: return 1.0
        e = np.mean(h)
        return float(np.clip(1 + e, 0.25, 1.5))
    def update(self, arm, r_mult):
        self.hist.setdefault(arm, []).append(r_mult)

def run(data, risk=0.01, start_eq=5000.0, learn=True, max_heat=0.06, dd_brake=0.20, lev=10):
    dates = sorted(set().union(*[d.index for d in data.values()]))
    rows = {sym: {t: r for t, r in zip(df.index, df.itertuples(index=False))} for sym, df in data.items()}
    eq, peak = start_eq, start_eq
    pos = {}       # (sym, strat) -> dict
    learner = Learner()
    curve, trades = [], []
    for t in dates:
        # 1) gestionar posiciones abiertas con la vela de hoy
        for key in list(pos):
            sym, st = key
            r = rows[sym].get(t)
            if r is None: continue
            p = pos[key]
            if t <= p["entry_date"]: continue
            p["bars"] += 1
            exit_px = None
            # stop intradía
            if p["dir"] == 1 and r.l <= p["stop"]: exit_px = min(r.o, p["stop"])
            if p["dir"] == -1 and r.h >= p["stop"]: exit_px = max(r.o, p["stop"])
            if exit_px is None:
                # salidas al cierre
                if st == "meanrev" and (r.c > r.sma5 or p["bars"] >= 10): exit_px = r.c
                elif st == "donchian" and ((p["dir"] == 1 and r.c < r.ex_lo) or (p["dir"] == -1 and r.c > r.ex_hi)): exit_px = r.c
                elif st == "tsmom" and ((p["dir"] == 1 and r.mom <= 0) or (p["dir"] == -1 and r.mom >= 0)): exit_px = r.c
                else:  # trailing stop por ATR (sólo a favor)
                    k = 2.5 if st != "tsmom" else 3.0
                    if st != "meanrev":
                        if p["dir"] == 1: p["stop"] = max(p["stop"], r.c - k * r.atr)
                        else: p["stop"] = min(p["stop"], r.c + k * r.atr)
            if exit_px is not None:
                cost = p["cost"] * exit_px * p["size"]
                pnl = p["dir"] * (exit_px - p["entry"]) * p["size"] - cost
                eq += pnl
                rm = pnl / p["risk_usd"]
                learner.update(key, rm)
                trades.append(dict(sym=sym, strat=st, dir=p["dir"], entry_date=p["entry_date"], exit_date=t, pnl=pnl, R=rm))
                del pos[key]
        # 2) equity a mercado
        mtm = eq
        for (sym, st), p in pos.items():
            r = rows[sym].get(t)
            if r is not None: p["last"] = r.c
            mtm += p["dir"] * (p["last"] - p["entry"]) * p["size"]
        peak = max(peak, mtm)
        dd = 1 - mtm / peak
        curve.append((t, mtm))
        if mtm <= start_eq * 0.02: break  # cuenta quemada
        # 3) nuevas señales al cierre de hoy; entrada en la apertura siguiente (aprox. al cierre + costo)
        heat = sum(p["risk_usd"] for p in pos.values()) / max(mtm, 1)
        brake = 0.5 if dd > dd_brake else 1.0   # freno de drawdown: mitad de riesgo
        for sym in data:
            r = rows[sym].get(t)
            if r is None or any(math.isnan(v) for v in r): continue
            name, cls, cst = UNIVERSE[sym]
            for st, fn in STRATS.items():
                key = (sym, st)
                if key in pos: continue
                sig = fn(r, cls)
                if not sig: continue
                d, stop = sig
                dist = abs(r.c - stop)
                if dist <= 0: continue
                m = learner.mult(key) if learn else 1.0
                risk_usd = mtm * risk * m * brake
                if heat + risk_usd / mtm > max_heat: continue
                size = risk_usd / dist
                # límite de apalancamiento nocional 10x por posición
                size = min(size, mtm * lev / r.c / max(1, len(data) / 4))
                risk_usd = size * dist
                entry = r.c
                pos[key] = dict(dir=d, entry=entry, stop=stop, size=size, risk_usd=risk_usd,
                                entry_date=t, bars=0, cost=cst, last=entry)
                heat += risk_usd / mtm
    s = pd.Series(dict(curve))
    return s, pd.DataFrame(trades)

def stats(curve, trades, start_eq=5000):
    yrs = (curve.index[-1] - curve.index[0]).days / 365.25
    cagr = (curve.iloc[-1] / start_eq) ** (1 / yrs) - 1 if curve.iloc[-1] > 0 else -1
    dd = (1 - curve / curve.cummax()).max()
    rets = curve.pct_change().dropna()
    sharpe = rets.mean() / rets.std() * math.sqrt(252) if rets.std() > 0 else 0
    out = dict(final=curve.iloc[-1], cagr=cagr, maxdd=dd, sharpe=sharpe, years=yrs, trades=len(trades))
    if len(trades):
        out.update(winrate=(trades.pnl > 0).mean(), avgR=trades.R.mean(),
                   pf=trades.pnl[trades.pnl > 0].sum() / max(1e-9, -trades.pnl[trades.pnl < 0].sum()))
    return out

def monte_carlo(R, trades_per_year, start=5000, goal=1_000_000, years=10, sims=4000, seed=7):
    """Remuestrea los trades históricos (en R) para estimar la probabilidad de llegar a la meta
    y de perder la mitad de la cuenta, según el % arriesgado por trade."""
    rng = np.random.default_rng(seed)
    n = int(trades_per_year * years)
    print(f"\nMonte Carlo ({sims} simulaciones, {years} años, ~{trades_per_year:.0f} trades/año):")
    for f in (0.005, 0.01, 0.02, 0.03, 0.05, 0.08):
        draws = rng.choice(R, size=(sims, n))
        eq = start * np.cumprod(np.maximum(1 + f * draws, 0), axis=1)
        hit = (eq >= goal).any(axis=1).mean()
        dd = 1 - eq / np.maximum.accumulate(eq, axis=1)
        half = (dd.max(axis=1) >= 0.5).mean()
        med = np.median(eq[:, -1])
        print(f"  riesgo {f*100:>4.1f}%/trade: mediana final ${med:>14,.0f} | P(llegar a $1M) {hit*100:5.1f}% | P(caída >=50%) {half*100:5.1f}%")

if __name__ == "__main__":
    folder = sys.argv[1]
    data = {}
    for f in os.listdir(folder):
        k = f[:-5]
        if k in UNIVERSE: data[k] = indicators(load(os.path.join(folder, f)))
    risks = [float(x) / 100 for x in sys.argv[2:]] or [0.005, 0.01, 0.02, 0.03]
    for rk in risks:
        for learn in (False, True):
            c, tr = run(data, risk=rk, learn=learn)
            s = stats(c, tr)
            print(f"riesgo {rk*100:.1f}% learn={learn!s:5} | final ${s['final']:>14,.0f} CAGR {s['cagr']*100:6.1f}% "
                  f"maxDD {s['maxdd']*100:5.1f}% Sharpe {s['sharpe']:.2f} trades {s['trades']} "
                  f"win {s.get('winrate',0)*100:.0f}% PF {s.get('pf',0):.2f} avgR {s.get('avgR',0):.2f}")
            if learn and rk == risks[0]:
                c.to_csv(os.path.join(os.path.dirname(__file__), "equity_curve.csv"))
                tr.to_csv(os.path.join(os.path.dirname(__file__), "trades.csv"), index=False)
                print(tr.groupby("strat").agg(n=("R", "size"), avgR=("R", "mean"), pnl=("pnl", "sum")).round(2))
                yearly = c.resample("YE").last()
                print("Rendimiento por año (%):")
                print((yearly.pct_change().fillna(yearly.iloc[0] / 5000 - 1) * 100).round(1).to_string())
                half = c.index[len(c) // 2]
                for nm, part in (("1a mitad", c[:half]), ("2a mitad", c[half:])):
                    y = (part.index[-1] - part.index[0]).days / 365.25
                    print(f"{nm}: CAGR {((part.iloc[-1]/part.iloc[0])**(1/y)-1)*100:.1f}% maxDD {(1-part/part.cummax()).max()*100:.1f}%")
                monte_carlo(tr.R.values, len(tr) / s["years"])
