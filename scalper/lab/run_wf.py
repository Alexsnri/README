"""Backtest lab: every strategy x instrument x parameters x exit policy, with costs, anchored walk-forward,
Deflated Sharpe and evaluation with backtest-expert.

Usage: python -I lab/run_wf.py            -> writes lab/results/*.csv and lab/results/resumen.json
"""
import json
import math
import os
import subprocess
import sys
from statistics import NormalDist

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
from data import load_1m  # noqa: E402
from sim import Market, simulate  # noqa: E402
from bot import strategies as S  # noqa: E402
from bot.stops import POLICIES  # noqa: E402

OUT = os.path.join(HERE, "results")
EVAL = os.path.join(ROOT, "..", ".claude", "skills", "backtest-expert", "scripts", "evaluate_backtest.py")
N = NormalDist()
STEP_MONTHS = 6
MIN_TRAIN_MONTHS = 12
MIN_TRAIN_TRADES = 30


def windows(start, end):
    a = (start + pd.DateOffset(months=MIN_TRAIN_MONTHS)).normalize().replace(day=1)
    while a < end:
        b = a + pd.DateOffset(months=STEP_MONTHS)
        yield a, min(b, end)
        a = b


def stats(R: pd.Series, t_out: pd.Series, risk=0.01):
    n = len(R)
    if n == 0:
        return dict(n=0)
    wins, losses = R[R > 0], R[R <= 0]
    eq = np.cumprod(1 + risk * R.to_numpy())
    peak = np.maximum.accumulate(np.concatenate([[1.0], eq]))[1:]
    dd = float((1 - eq / peak).max())
    daily = R.groupby(pd.DatetimeIndex(t_out).tz_convert("America/New_York").date).sum()
    years = max((t_out.max() - t_out.min()).days / 365.25, 1e-9)
    sh = float(daily.mean() / daily.std() * math.sqrt(252)) if len(daily) > 2 and daily.std() > 0 else 0.0
    se = R.std(ddof=1) / math.sqrt(n) if n > 1 else float("nan")
    return dict(n=n, win=float((R > 0).mean()), E=float(R.mean()), t=float(R.mean() / se) if se else 0.0,
                pf=float(wins.sum() / -losses.sum()) if losses.sum() < 0 else float("inf"),
                avg_win=float(wins.mean()) if len(wins) else 0.0, avg_loss=float(-losses.mean()) if len(losses) else 0.0,
                ge0=float((R >= -1e-9).mean()), dd1=dd, sharpe=sh, years=years, per_year=n / years,
                cagr1=float(eq[-1] ** (1 / years) - 1))


def deflated_sharpe(R: pd.Series, trial_srs):
    """Bailey & Lopez de Prado (2014), per-trade SR. Returns P(true SR > 0) correcting for the number of trials."""
    n = len(R)
    if n < 10 or R.std() == 0:
        return float("nan")
    sr = R.mean() / R.std()
    k = len(trial_srs)
    var = np.var(trial_srs) if k > 1 else 0.0
    g = 0.5772156649
    if k > 1:
        sr0 = math.sqrt(var) * ((1 - g) * N.inv_cdf(1 - 1 / k) + g * N.inv_cdf(1 - 1 / (k * math.e)))
    else:
        sr0 = 0.0
    skew = float(((R - R.mean()) ** 3).mean() / R.std() ** 3)
    kurt = float(((R - R.mean()) ** 4).mean() / R.std() ** 4)
    den = math.sqrt(max(1e-12, 1 - skew * sr + (kurt - 1) / 4 * sr ** 2))
    return float(N.cdf((sr - sr0) * math.sqrt(n - 1) / den))


def evaluate(st, n_params, years):
    """Calls the backtest-expert skill script and returns its decision."""
    if st.get("n", 0) == 0:
        return {"decision": "NOT_EVALUABLE", "blocking_reasons": ["no_trades"]}
    args = [sys.executable, "-I", EVAL, "--total-trades", str(st["n"]), "--win-rate", f"{100 * st['win']:.2f}",
            "--avg-win-pct", f"{max(st['avg_win'], 1e-6):.4f}", "--avg-loss-pct", f"{max(st['avg_loss'], 1e-6):.4f}",
            "--max-drawdown-pct", f"{100 * st['dd1']:.2f}", "--years-tested", str(int(years + 0.05)),
            "--num-parameters", str(n_params), "--slippage-tested", "--output-dir", os.path.join(OUT, "eval")]
    # avg win/loss in % of account at 1% risk per trade = R x 1%
    r = subprocess.run(args, capture_output=True, text=True)
    files = sorted(f for f in os.listdir(os.path.join(OUT, "eval")) if f.endswith(".json"))
    if r.returncode != 0 or not files:
        return {"decision": "ERROR", "blocking_reasons": [r.stderr[-300:]]}
    rep = json.load(open(os.path.join(OUT, "eval", files[-1])))
    return {"decision": rep.get("decision"), "verdict": rep.get("verdict"), "score": rep.get("quality_score"),
            "blocking_reasons": rep.get("blocking_reasons", [])}


def main(only=None):
    os.makedirs(os.path.join(OUT, "eval"), exist_ok=True)
    rows, oos_all, policy_rows = [], [], []
    markets = {}
    for cls in S.ALL:
        if only and cls.code not in only:
            continue
        for inst in cls.instruments:
            if inst not in markets:
                markets[inst] = Market(inst, load_1m(inst))
            mk = markets[inst]
            mk.set_cost(1.25)
            ign = getattr(cls, "ignore_schedule", False)
            trades = {}
            sigs = {}
            for st in cls.configs():
                sig = st.signals(mk.df5, mk.inst.family)
                sigs[st.key] = sig
                for pol, p in POLICIES.items():
                    tr = simulate(mk, sig, p, ignore_schedule=ign)
                    trades[(st.key, pol)] = tr
            # full-sample per-trial SRs (for the DSR) and plateau
            trial = {k: v for k, v in trades.items() if len(v) >= MIN_TRAIN_TRADES}
            trial_sr = [v["R"].mean() / v["R"].std() for v in trial.values() if v["R"].std() > 0]
            plateau = float(np.mean([v["R"].mean() > 0 for v in trial.values()])) if trial else 0.0
            # move early vs let it breathe
            for (key, pol), tr in trades.items():
                if len(tr):
                    policy_rows.append(dict(strat=cls.code, inst=inst, config=key, policy=pol, n=len(tr),
                                            E=tr["R"].mean(), ge0=(tr["R"] >= -1e-9).mean(), win=(tr["R"] > 0).mean(),
                                            moved_be=(tr["reason"] == 4).mean()))
            # anchored walk-forward
            t0 = mk.t1[0]
            t1 = mk.t1[-1]
            oos = []
            chosen = []
            for a, b in windows(t0, t1):
                best, best_e = None, 0.0
                for k, tr in trades.items():
                    tr_train = tr[tr["t_in"] < a]
                    if len(tr_train) >= MIN_TRAIN_TRADES and tr_train["R"].mean() > best_e:
                        best, best_e = k, tr_train["R"].mean()
                chosen.append(dict(window=str(a.date()), choice=best and f"{best[0]}|{best[1]}", train_E=best_e))
                if best is None:
                    continue
                tr = trades[best]
                sel = tr[(tr["t_in"] >= a) & (tr["t_in"] < b)].copy()
                sel["config"], sel["policy"] = best
                oos.append(sel)
            oos = pd.concat(oos) if oos else pd.DataFrame(columns=["R", "t_out"])
            # stress: the same choices with 2x spread
            mk.set_cost(2.0)
            stress = []
            for c in chosen:
                if not c["choice"]:
                    continue
                key, pol = c["choice"].split("|")
                a = pd.Timestamp(c["window"], tz="UTC")
                b = a + pd.DateOffset(months=STEP_MONTHS)
                tr = simulate(mk, sigs[key], POLICIES[pol], ignore_schedule=ign)
                stress.append(tr[(tr["t_in"] >= a) & (tr["t_in"] < b)])
            mk.set_cost(1.25)
            stress = pd.concat(stress) if stress else pd.DataFrame(columns=["R"])
            st_oos = stats(oos["R"], oos["t_out"]) if len(oos) else dict(n=0)
            years_total = (t1 - t0).days / 365.25
            n_params = len(cls.grid) + 1
            ev = evaluate(st_oos, n_params, years_total)
            dsr = deflated_sharpe(oos["R"], trial_sr) if len(oos) else float("nan")
            stress_E = float(stress["R"].mean()) if len(stress) else float("nan")
            verdict = ev["decision"]
            if verdict in ("DEPLOY", "REFINE") and not (stress_E > 0):
                verdict = "ABANDON (no aguanta 2x spread)"
            best_is = max(trades.items(), key=lambda kv: kv[1]["R"].mean() if len(kv[1]) >= MIN_TRAIN_TRADES else -9)
            row = dict(strat=cls.code, name=cls.name, inst=inst, trials=len(trades), plateau=plateau,
                       is_best=f"{best_is[0][0]}|{best_is[0][1]}", is_n=len(best_is[1]),
                       is_E=float(best_is[1]["R"].mean()) if len(best_is[1]) else float("nan"),
                       is_cost=float(best_is[1]["cost_R"].mean()) if len(best_is[1]) else float("nan"),
                       stress_E=stress_E, dsr=dsr, decision=ev["decision"], verdict=verdict,
                       blocking=",".join(ev.get("blocking_reasons", [])), score=ev.get("score"),
                       chosen=json.dumps(chosen), **{f"oos_{k}": v for k, v in st_oos.items()})
            rows.append(row)
            if len(oos):
                oos["strat"] = cls.code
                oos_all.append(oos)
            print(f"{cls.code} {inst:7s} IS-best E={row['is_E']:+.3f} cost={row['is_cost']:.3f} | OOS n={st_oos.get('n', 0):5d} E={st_oos.get('E', float('nan')):+.3f}R "
                  f"t={st_oos.get('t', 0):+.2f} stress={stress_E:+.3f} DSR={dsr:.2f} plateau={plateau:.2f} -> {verdict}",
                  flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(OUT, "ranking.csv"), index=False)
    pd.DataFrame(policy_rows).to_csv(os.path.join(OUT, "politicas_stop.csv"), index=False)
    if oos_all:
        pd.concat(oos_all).to_parquet(os.path.join(OUT, "oos_trades.parquet"))
    return res


if __name__ == "__main__":
    main(sys.argv[1:] or None)
