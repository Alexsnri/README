"""Report for the day and accumulated: trades, W/L, P&L with costs, best/worst, drawdown, what the Learner learned
and comparison against what the backtest predicted.
"""
import json
import os
import time
from datetime import datetime, timedelta, timezone

from .schedule import CDMX

HERE = os.path.dirname(os.path.abspath(__file__))


def backtest_expectation():
    p = os.path.join(HERE, "data", "backtest.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def stats(trades):
    if not trades:
        return {"trades": 0, "wins": 0, "losses": 0, "ceros": 0, "pnl": 0.0, "costos": 0.0, "r_total": 0.0,
                "r_medio": None, "mejor": None, "peor": None, "win_rate": None, "dd_usd": 0.0}
    pnl = [t["pnl"] or 0 for t in trades]
    eq, peak, dd = 0.0, 0.0, 0.0
    for x in pnl:
        eq += x
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
    rs = [t["r"] or 0 for t in trades]
    wins = sum(1 for x in pnl if x > 0)
    ceros = sum(1 for r in rs if abs(r) < 0.05)
    return {"trades": len(trades), "wins": wins, "losses": len(trades) - wins - ceros, "ceros": ceros,
            "pnl": sum(pnl), "costos": sum(t["costos"] or 0 for t in trades), "r_total": sum(rs),
            "r_medio": sum(rs) / len(rs), "mejor": max(pnl), "peor": min(pnl), "win_rate": wins / len(trades),
            "dd_usd": dd}


def day_start(now=None):
    now = datetime.fromtimestamp(now or time.time(), timezone.utc).astimezone(CDMX)
    return now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()


def build(store, learner, account, start_balance, now=None):
    now = now or time.time()
    t0 = day_start(now)
    live_all = store.trades(shadow=False)
    live_day = [t for t in live_all if t["closed"] >= t0]
    shadow_all = store.trades(shadow=True)
    bt = backtest_expectation()
    days = max(1.0, (now - (live_all[0]["opened"] if live_all else now)) / 86400)
    exp = bt.get("brazos", {})
    comp = []
    for arm in sorted({t["arm"] for t in live_all} | set(exp)):
        mine = [t for t in live_all if t["arm"] == arm]
        e = exp.get(arm, {})
        comp.append({"brazo": arm, "trades": len(mine), "r_medio_real": (sum(t["r"] for t in mine) / len(mine)) if mine else None,
                     "r_medio_backtest": e.get("E_oos"), "r_medio_backtest_reciente": e.get("E_reciente"),
                     "trades_dia_real": len(mine) / days, "trades_dia_backtest": e.get("trades_dia")})
    return {"generado": datetime.fromtimestamp(now, CDMX).strftime("%Y-%m-%d %H:%M CDMX"),
            "balance_capital": account.get("balance"), "no_realizado": account.get("upl"),
            "saldo_inicial": start_balance, "dia": stats(live_day), "acumulado": stats(live_all),
            "sombra": stats(shadow_all), "learner": learner.snapshot(),
            "cambios_learner": learner.changes(5), "vs_backtest": comp}


def to_text(rep):
    def fmt(s):
        if not s["trades"]:
            return "sin trades"
        return (f"{s['trades']} trades · {s['wins']}W/{s['losses']}L/{s['ceros']} en cero · PnL {s['pnl']:+.2f} USD "
                f"(costos {s['costos']:.2f}) · {s['r_total']:+.2f}R · mejor {s['mejor']:+.2f} · peor {s['peor']:+.2f} · "
                f"DD {s['dd_usd']:.2f}")
    lines = [f"📊 Reporte {rep['generado']} (DEMO)"]
    if rep["balance_capital"] is not None:
        lines.append(f"Balance Capital.com: ${rep['balance_capital']:,.2f} · no realizado {rep['no_realizado'] or 0:+.2f}"
                     + (f" · inicio ${rep['saldo_inicial']:,.2f}" if rep["saldo_inicial"] else ""))
    lines.append("Hoy: " + fmt(rep["dia"]))
    lines.append("Acumulado: " + fmt(rep["acumulado"]))
    lines.append("Sombra (papel): " + fmt(rep["sombra"]))
    for c in rep["vs_backtest"]:
        if c["r_medio_backtest"] is None:
            continue
        real = "—" if c["r_medio_real"] is None else f"{c['r_medio_real']:+.3f}R"
        lines.append(f"{c['brazo']}: real {real} en {c['trades']} trades vs backtest {c['r_medio_backtest']:+.3f}R "
                     f"(2025-26: {c['r_medio_backtest_reciente']:+.3f}R) · {c['trades_dia_real']:.2f} vs "
                     f"{c['trades_dia_backtest']:.2f} trades/día")
    for a in rep["learner"]:
        lines.append(f"Learner {a['arm']} [{a['modo']}]: n={a['n']} P(E>0)={a['p_pos']:.2f} riesgo×{a['mult']:.1f}")
    if rep["cambios_learner"]:
        lines.append("Último cambio del Learner: " + rep["cambios_learner"][0]["cambio"])
    return "\n".join(lines)


def write_daily(folder, rep):
    os.makedirs(folder, exist_ok=True)
    day = rep["generado"][:10]
    with open(os.path.join(folder, f"{day}.md"), "w", encoding="utf-8") as f:
        f.write(to_text(rep).replace("\n", "\n\n"))
    with open(os.path.join(folder, "acumulado.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1, default=str)
