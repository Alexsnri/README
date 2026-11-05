from bot.learner import Learner
from bot.store import Store

CFG = {"descuento": 0.995, "prior_trades": 50, "promover_min_trades": 271, "pausar_si_prob_menor": 0.2,
       "auto_promover": False}
ARMS = [{"estrategia": "S1", "instrumento": "US100", "modo": "vivo"},
        {"estrategia": "S1", "instrumento": "US500", "modo": "sombra"}]


def mk(tmp_path):
    logs = []
    st = Store(str(tmp_path / "t.db"))
    return Learner(CFG, ARMS, {"S1-US100": 0.10}, st, lambda *a: logs.append(a)), logs


def test_does_not_learn_from_a_streak(tmp_path):
    ln, logs = mk(tmp_path)
    for _ in range(30):                 # 30 losses in a row: < 50 trades, does not touch risk
        ln.on_trade("S1-US100", -1.0)
    assert ln.mult["S1-US100"] == 1.0


def test_cuts_risk_with_enough_bad_sample(tmp_path):
    ln, logs = mk(tmp_path)
    for i in range(120):
        ln.on_trade("S1-US100", -0.4 if i % 3 else 0.3)
    assert ln.mult["S1-US100"] < 1.0
    assert ln.changes(5)                # left a record with the reason


def test_shadow_promotion_needs_sample(tmp_path):
    ln, logs = mk(tmp_path)
    for i in range(100):
        ln.on_trade("S1-US500", 0.5)
    assert ln.modes["S1-US500"] == "sombra"
    for i in range(200):
        ln.on_trade("S1-US500", 0.5 if i % 2 else 0.2)
    assert ln.modes["S1-US500"] == "sombra"          # auto_promover false: only proposes
    assert any("candidato" in c["cambio"] for c in ln.changes(5))


def test_state_survives_restart(tmp_path):
    ln, _ = mk(tmp_path)
    for _ in range(10):
        ln.on_trade("S1-US100", 1.0)
    ln2 = Learner(CFG, ARMS, {"S1-US100": 0.10}, ln.store, lambda *a: None)
    assert ln2.arms["S1-US100"].n_raw == 10
