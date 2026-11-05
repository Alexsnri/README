"""Exports the lab summary for the bot (bot/data/backtest.json): Learner prior and comparison in REPORTE."""
import json, os
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "results")
rank = pd.read_csv(os.path.join(R, "ranking.csv"))
oos = pd.read_parquet(os.path.join(R, "oos_trades.parquet"))
exp = json.load(open(os.path.join(R, "expectativa.json")))
out = {"fuente": "lab/run_wf.py (walk-forward anclado, costos 1.25x spread, deslizamiento 0.5x en stops)", "brazos": {}}
for _, r in rank.iterrows():
    key = f"{r.strat}-{r.inst}"
    t = oos[(oos.strat == r.strat) & (oos.inst == r.inst)]
    if not len(t):
        continue
    days = len(pd.bdate_range(t.t_in.min().normalize(), t.t_in.max().normalize()))
    rec = t[t.t_in >= "2025-01-01"]
    out["brazos"][key] = {"veredicto": r.verdict, "E_oos": float(t.R.mean()), "E_reciente": float(rec.R.mean()) if len(rec) else None,
                          "trades": int(len(t)), "trades_dia": len(t) / days, "win": float((t.R > 0).mean()),
                          "E_estres_2x": float(r.stress_E)}
out["expectativa"] = exp
json.dump(out, open(os.path.join(HERE, "..", "bot", "data", "backtest.json"), "w"), indent=1)
print(json.dumps(out["brazos"], indent=1))
