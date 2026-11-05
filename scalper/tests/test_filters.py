"""Filter agent: a single failure = discarded."""
from dataclasses import replace

from bot.filters import Setup, evaluate

CFG = {"spread_max_atr": 0.25, "spread_max_vs_tipico": 2.0, "atr_percentil_min": 5, "atr_percentil_max": 99,
       "datos_max_seg": 15}
GOOD = Setup("US100", "S1-US100", 1, 0.0, spread=1.8, atr=30.0, atr_pctile=50, typical_spread=1.8,
             has_position=False, session_ok=True, news_block="", market_open=True, quote_age=1.0)


def test_good_setup_passes():
    ok, rules = evaluate(GOOD, CFG)
    assert ok and all(r[1] for r in rules) and len(rules) == 9


def check_kills(**change):
    ok, rules = evaluate(replace(GOOD, **change), CFG)
    assert not ok
    assert sum(1 for r in rules if not r[1]) >= 1
    return [r[0] for r in rules if not r[1]]


def test_each_rule_kills():
    assert "sesión permitida" in check_kills(session_ok=False)
    assert "mercado abierto" in check_kills(market_open=False)
    assert "datos frescos" in check_kills(quote_age=60)
    assert any("ATR" in r for r in check_kills(spread=10.0))            # 10/30 = 0.33 ATR
    assert any("típico" in r for r in check_kills(spread=4.0, atr=100))  # 4/1.8 = 2.2x typical
    assert "sin noticia de alto impacto" in check_kills(news_block="USD CPI 08:30 NY")
    assert any("≥ p5" in r for r in check_kills(atr_pctile=2))
    assert any("≤ p99" in r for r in check_kills(atr_pctile=99.5))
    assert "sin posición en el instrumento" in check_kills(has_position=True)


def test_zero_atr_kills():
    assert any("ATR" in r for r in check_kills(atr=0.0))
