"""Analyst agent: 0-100 score that combines the validated strategy, what the Learner has learned, market quality
and the information agents (each one with the weight it earned in the backtest; today they are all 0).
"""


def score(setup, arm_validated: bool, learner_p: float, info_readings: dict, cfg: dict):
    w = cfg["pesos"]
    parts = []
    s_strat = w["estrategia"] if arm_validated else 0.0
    parts.append(("estrategia validada (walk-forward)", s_strat, w["estrategia"]))
    s_learn = w["learner"] * max(0.0, min(1.0, learner_p))
    parts.append((f"learner P(E>0)={learner_p:.2f}", s_learn, w["learner"]))
    ratio = setup.spread / setup.atr if setup.atr > 0 else 1.0
    q = max(0.0, min(1.0, (0.25 - ratio) / 0.15))   # 1 if spread <= 0.10 ATR, 0 at 0.25 ATR
    parts.append((f"mercado: spread {ratio:.2f} ATR", w["mercado"] * q, w["mercado"]))
    # information: average of the agents with weight > 0 that agree with the direction (+1) or not (-1)
    num = den = 0.0
    for name, rd in info_readings.items():
        if rd.get("peso", 0) > 0 and rd.get("dir") is not None:
            num += rd["peso"] * (1 if rd["dir"] == setup.direction else 0)
            den += rd["peso"]
    s_info = w["informacion"] * (num / den if den else 0.5)
    parts.append(("agentes de información" + ("" if den else " (sin peso: neutral)"), s_info, w["informacion"]))
    total = sum(p[1] for p in parts)
    return round(total), [{"parte": p, "puntos": round(v, 1), "max": m} for p, v, m in parts]
