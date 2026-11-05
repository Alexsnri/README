"""Risk agent and position-size calculation."""
import pytest

from bot.risk import DealingRules, RiskManager, RiskState, floor_step, position_size

PROFILE = {"riesgo_por_trade_pct": 1.0, "arranque": {"trades": 300, "riesgo_por_trade_pct": 0.5},
           "riesgo_abierto_max_pct": 3.0, "posiciones_max": 2, "stop_diario_R": -6, "stop_semanal_R": -15,
           "breaker_perdidas_pausa": 7, "breaker_perdidas_dia": 10}
US100 = DealingRules(min_size=0.001, step=0.001, min_stop_dist=1.0, margin_factor=0.01)


def test_size_never_risks_more_than_allowed():
    size, risk, why = position_size(100.0, 1.0, 60.0, US100)
    assert why == "ok"
    assert risk <= 1.0 + 1e-9                   # $1 = 1% of $100
    assert size == pytest.approx(0.016)         # 1/60 = 0.01666 -> rounded down to the 0.001 step


def test_size_includes_slippage():
    s1, _, _ = position_size(100.0, 1.0, 60.0, US100)
    s2, r2, _ = position_size(100.0, 1.0, 60.0, US100, slip=5.0)
    assert s2 < s1 and r2 <= 1.0 + 1e-9


def test_min_size_too_big_rejects():
    gold_mt5 = DealingRules(min_size=1.0, step=1.0)
    size, risk, why = position_size(100.0, 1.0, 3.0, gold_mt5)   # 1 oz with a $3 stop = 3% > 1%
    assert size == 0 and "mínimo" in why


def test_respects_min_stop_distance():
    size, risk, _ = position_size(100.0, 1.0, 0.1, US100)          # stop below the minimum -> uses 1.0
    assert risk <= 1.0 + 1e-9 and size == pytest.approx(1.0)


def test_invalid_inputs():
    assert position_size(0, 1, 10, US100)[0] == 0
    assert position_size(100, 1, 0, US100)[0] == 0
    assert position_size(100, 0, 10, US100)[0] == 0


def test_floor_step():
    assert floor_step(0.0169, 0.001) == pytest.approx(0.016)
    assert floor_step(250, 100) == 200


def test_startup_risk_then_normal():
    rm = RiskManager(PROFILE)
    assert rm.risk_pct() == 0.5          # first 300 live trades at 0.5%
    rm.s.live_trades = 300
    assert rm.risk_pct() == 1.0
    assert rm.risk_pct(slot_mult=0.5) == 0.5
    assert rm.risk_pct(learner_mult=3.0) == 1.0   # the learner can never raise risk


def test_no_averaging_down_and_max_positions():
    rm = RiskManager(PROFILE)
    ok, why = rm.check(1e9, 100, [{"instrumento": "US100", "risk_usd": 1}], 1, "US100")
    assert not ok and "promediar" in why
    two = [{"instrumento": "A", "risk_usd": 1}, {"instrumento": "B", "risk_usd": 1}]
    ok, why = rm.check(1e9, 100, two, 1, "US100")
    assert not ok and "máximo" in why


def test_max_open_risk():
    rm = RiskManager(PROFILE)
    ok, why = rm.check(1e9, 100, [{"instrumento": "A", "risk_usd": 2.5}], 1.0, "US100")
    assert not ok and "riesgo abierto" in why


def test_margin_check():
    rm = RiskManager(PROFILE)
    ok, why = rm.check(1e9, 100, [], 1.0, "US100", margin_needed=60, available=100)
    assert not ok and "margen" in why


def test_streak_breakers_and_no_martingale():
    rm = RiskManager(PROFILE, RiskState(live_trades=300))
    t = 1_700_000_000.0
    before = rm.risk_pct()
    for i in range(6):
        rm.on_close(t + i, -0.5)                  # small losses: the daily stop (-6R) does not fire
        assert rm.risk_pct() <= before            # never goes up after losses (no martingale)
    ev = rm.on_close(t + 7, -0.1)                 # 7th loss in a row -> pause and half size
    assert any("pausa" in e for e in ev)
    assert rm.risk_pct() == pytest.approx(0.5)
    ok, why = rm.check(t + 8, 100, [], 1, "US100")
    assert not ok and "breaker" in why
    ok, _ = rm.check(t + 3 * 3600, 100, [], 1, "US100")
    assert ok


def test_daily_stop():
    rm = RiskManager(PROFILE, RiskState(live_trades=300))
    t = 1_700_000_000.0
    ev = []
    for i in range(6):
        ev += rm.on_close(t + i, -1.1)            # 6 x -1.1R = -6.6R <= -6R
    assert any("STOP DIARIO" in e for e in ev)
    ok, why = rm.check(t + 10, 100, [], 1, "US100")
    assert not ok and "detenido" in why


def test_win_resets_streak():
    rm = RiskManager(PROFILE, RiskState(live_trades=300))
    t = 1_700_000_000.0
    for i in range(5):
        rm.on_close(t + i, -1.0)
    rm.on_close(t + 6, 2.0)
    assert rm.s.streak == 0


def test_shadow_trades_do_not_touch_breakers():
    rm = RiskManager(PROFILE)
    rm.on_close(1e9, -5, shadow=True)
    assert rm.s.day_r == 0 and rm.s.live_trades == 0
