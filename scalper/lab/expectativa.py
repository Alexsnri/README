"""Realistic expectation table from the walk-forward OOS trades (day bootstrap)."""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")


def main():
    oos = pd.read_parquet(os.path.join(OUT, "oos_trades.parquet"))
    rank = pd.read_csv(os.path.join(OUT, "ranking.csv"))
    ok = rank[rank["verdict"].isin(["DEPLOY", "REFINE"])][["strat", "inst"]]
    tr = oos.merge(ok, on=["strat", "inst"])
    days = pd.bdate_range(tr["t_in"].min().normalize(), tr["t_in"].max().normalize(), tz="UTC")
    rng = np.random.default_rng(7)
    res = {}
    for label, sub in [("todo_OOS_2022_2026", tr), ("reciente_2025_2026", tr[tr["t_in"] >= "2025-01-01"])]:
        d = sub.groupby(sub["t_in"].dt.tz_convert("America/New_York").dt.date)["R"].apply(list)
        alld = pd.bdate_range(sub["t_in"].min().normalize(), sub["t_in"].max().normalize())
        pool = [d.get(x.date(), []) for x in alld]   # includes days with no trades
        out = {"trades_por_dia": len(sub) / len(alld), "E_R": float(sub["R"].mean())}
        for risk in (0.005, 0.01, 0.02, 0.05):
            for horizon, n in (("dia", 1), ("semana", 5), ("mes", 21), ("anio", 252)):
                eq = np.full(20000, 100.0)
                for _ in range(n):
                    pick = rng.integers(0, len(pool), size=20000)
                    for i, p in enumerate(pick):
                        for r in pool[p]:
                            eq[i] *= 1 + risk * r
                q = np.percentile(eq, [10, 50, 90])
                out[f"{risk:.3f}_{horizon}"] = dict(p10=q[0], p50=q[1], p90=q[2], p_menos50=float((eq <= 50).mean()),
                                                    p_10k=float((eq >= 10000).mean()))
        res[label] = out
    json.dump(res, open(os.path.join(OUT, "expectativa.json"), "w"), indent=1)
    for label, out in res.items():
        print(label, "trades/dia %.2f E %.3f" % (out["trades_por_dia"], out["E_R"]))
        for k, v in out.items():
            if isinstance(v, dict):
                print(" ", k, {a: round(b, 3) for a, b in v.items()})


if __name__ == "__main__":
    main()
