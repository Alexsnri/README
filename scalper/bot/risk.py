"""Risk agent: fixed risk per trade, stop set before entry, position limits, daily/weekly stop and losing-streak
breaker. No martingale and no averaging down: size never goes up after a loss and nothing is added to an open
position.
"""
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from .schedule import NY


@dataclass
class DealingRules:
    min_size: float = 0.01
    step: float = 0.01
    max_size: float = 1e9
    min_stop_dist: float = 0.0      # price
    margin_factor: float = 0.05     # fraction of the notional
    value_per_point: float = 1.0    # USD per point per 1 unit of size


def floor_step(x, step):
    if step <= 0:
        return x
    n = math.floor(x / step + 1e-9)
    return round(n * step, 10)


def position_size(equity, risk_pct, stop_dist, rules: DealingRules, slip=0.0):
    """Size such that hitting the stop loses at most `risk_pct`% of `equity`. Returns (size, real_risk_usd, reason)."""
    if equity <= 0 or risk_pct <= 0:
        return 0.0, 0.0, "sin capital o riesgo 0"
    if stop_dist <= 0:
        return 0.0, 0.0, "stop inválido"
    stop_dist = max(stop_dist, rules.min_stop_dist)
    risk_usd = equity * risk_pct / 100.0
    per_unit = (stop_dist + slip) * rules.value_per_point
    size = floor_step(risk_usd / per_unit, rules.step)
    if size < rules.min_size:
        return 0.0, rules.min_size * per_unit, (f"el tamaño mínimo ({rules.min_size}) arriesgaría "
                                                f"${rules.min_size * per_unit:.2f} > ${risk_usd:.2f}")
    size = min(size, rules.max_size)
    return size, size * per_unit, "ok"


@dataclass
class RiskState:
    day: str = ""
    week: str = ""
    day_r: float = 0.0
    week_r: float = 0.0
    streak: int = 0
    pause_until: float = 0.0
    half_size: bool = False
    halted_day: bool = False
    halted_week: bool = False
    live_trades: int = 0
    history: list = field(default_factory=list)


def trading_day(ts: float):
    """The trading day starts at 18:00 NY (after the daily break)."""
    ny = datetime.fromtimestamp(ts, timezone.utc).astimezone(NY)
    d = (ny.replace(tzinfo=None) + timedelta(hours=6)).date()
    iso = d.isocalendar()
    return d.isoformat(), f"{iso[0]}-W{iso[1]:02d}"


class RiskManager:
    def __init__(self, profile: dict, state: RiskState | None = None):
        self.p = profile
        self.s = state or RiskState()

    def _roll(self, now):
        day, week = trading_day(now)
        if day != self.s.day:
            self.s.day, self.s.day_r, self.s.halted_day = day, 0.0, False
        if week != self.s.week:
            self.s.week, self.s.week_r, self.s.halted_week = week, 0.0, False

    def risk_pct(self, slot_mult=1.0, learner_mult=1.0):
        arr = self.p.get("arranque") or {}
        base = self.p["riesgo_por_trade_pct"]
        if self.s.live_trades < arr.get("trades", 0):
            base = arr["riesgo_por_trade_pct"]
        pct = base * slot_mult * min(1.0, learner_mult)   # the learner can only lower risk, never raise it
        if self.s.half_size:
            pct *= 0.5
        return pct

    def check(self, now, equity, open_positions, new_risk_usd, instrument, margin_needed=0.0, available=None):
        """Returns (ok, reason). `open_positions` = list of dicts with 'instrumento' and 'risk_usd'."""
        self._roll(now)
        if self.s.halted_week:
            return False, f"stop semanal alcanzado ({self.s.week_r:+.1f}R)"
        if self.s.halted_day:
            return False, f"día detenido ({self.s.day_r:+.1f}R / racha {self.s.streak})"
        if now < self.s.pause_until:
            return False, f"breaker: pausa hasta {datetime.fromtimestamp(self.s.pause_until, NY):%H:%M} NY"
        if any(p["instrumento"] == instrument for p in open_positions):
            return False, "ya hay posición en este instrumento (sin promediar)"
        if len(open_positions) >= self.p["posiciones_max"]:
            return False, f"máximo de posiciones ({self.p['posiciones_max']})"
        open_risk = sum(p.get("risk_usd", 0) for p in open_positions) + new_risk_usd
        if equity > 0 and open_risk / equity * 100 > self.p["riesgo_abierto_max_pct"] + 1e-9:
            return False, f"riesgo abierto {open_risk / equity * 100:.1f}% > {self.p['riesgo_abierto_max_pct']}%"
        if available is not None and margin_needed > 0.5 * available:
            return False, f"margen ${margin_needed:.2f} > 50% del disponible"
        return True, "ok"

    def on_close(self, now, r, shadow=False):
        """Updates the breakers with the result in R of a closed (live) trade. Returns a list of events."""
        if shadow:
            return []
        self._roll(now)
        ev = []
        self.s.live_trades += 1
        self.s.day_r += r
        self.s.week_r += r
        if r < 0:
            self.s.streak += 1
        else:
            self.s.streak = 0
            self.s.half_size = False
        if self.s.streak >= self.p["breaker_perdidas_dia"]:
            self.s.halted_day = True
            ev.append(f"BREAKER {self.s.streak} pérdidas seguidas: alto del día")
        elif self.s.streak >= self.p["breaker_perdidas_pausa"] and not self.s.half_size:
            self.s.pause_until = now + 2 * 3600
            self.s.half_size = True
            ev.append(f"BREAKER {self.s.streak} pérdidas seguidas: pausa 2 h y medio tamaño")
        if self.s.day_r <= self.p["stop_diario_R"]:
            self.s.halted_day = True
            ev.append(f"STOP DIARIO {self.s.day_r:+.1f}R: no más entradas hoy")
        if self.s.week_r <= self.p["stop_semanal_R"]:
            self.s.halted_week = True
            ev.append(f"STOP SEMANAL {self.s.week_r:+.1f}R: no más entradas esta semana")
        return ev
