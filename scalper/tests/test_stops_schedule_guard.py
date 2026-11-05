"""Stop Manager (only in favor), rotation calendar and the DEMO-only guard."""
import os
from datetime import datetime, timezone

import pandas as pd
import pytest

from bot import config, schedule
from bot.stops import update_stop


def test_stop_only_moves_in_favor_long():
    s = update_stop(1, 100.0, 98.0, 103.0, 1.0, be_trig=1.0, be_buf=0.1, trail_mult=2.0, trail_start=1.0)
    assert s == pytest.approx(101.0)            # trailing 2 ATR below the best 103
    s2 = update_stop(1, 100.0, s, 102.0, 1.0, 1.0, 0.1, 2.0, 1.0)   # price falls: the stop does NOT go down
    assert s2 == s


def test_break_even_plus_costs_short():
    s = update_stop(-1, 100.0, 102.0, 98.9, 1.0, be_trig=1.0, be_buf=0.1, trail_mult=0.0, trail_start=0.0)
    assert s == pytest.approx(99.9)             # BE + costs for a short = entry - buffer


def test_no_move_before_trigger():
    assert update_stop(1, 100.0, 98.0, 100.5, 1.0, 1.0, 0.1, 2.0, 1.0) == 98.0


def test_fixed_policy_never_moves():
    assert update_stop(1, 100.0, 98.0, 150.0, 1.0, 0.0, 0.1, 0.0, 0.0) == 98.0


def ts(s):
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


def test_slots_winter_cdmx():
    # 2026-11-05 is a Thursday; NY in EST (UTC-5), CDMX UTC-6
    assert schedule.slot_at(ts("2026-11-05T15:00:00")) == "prime"      # 10:00 NY / 09:00 CDMX
    assert schedule.slot_at(ts("2026-11-05T13:30:00")) == "datos"      # 08:30 NY
    assert schedule.slot_at(ts("2026-11-05T22:00:00")) == "rollover"   # 17:00 NY / 16:00 CDMX
    assert schedule.slot_at(ts("2026-11-07T15:00:00")) == "cerrado"    # Saturday
    assert schedule.can_enter(ts("2026-11-05T17:30:00"), "US100")      # 12:30 NY afternoon
    assert not schedule.can_enter(ts("2026-11-05T17:30:00"), "BTCUSD")
    assert schedule.must_flatten(ts("2026-11-05T21:45:00"), "US100", "index")   # 16:45 NY


def test_slots_follow_us_dst():
    # in July NY is UTC-4: 10:00 NY = 14:00 UTC
    assert schedule.slot_at(ts("2026-07-09T14:00:00")) == "prime"
    assert schedule.slot_at(ts("2026-07-09T12:00:00")) == "londres"   # 08:00 NY


def test_demo_guard_refuses_live(monkeypatch):
    monkeypatch.setenv("CAPITAL_API_URL", "https://api-capital.backend-capital.com")
    with pytest.raises(config.NotDemoError):
        config.api_url()
    monkeypatch.setenv("CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1")
    assert config.api_url() == config.DEMO_API
    monkeypatch.setenv("CAPITAL_ENV", "live")
    with pytest.raises(config.NotDemoError):
        config.api_url()


def test_redact(monkeypatch):
    monkeypatch.setenv("CAPITAL_API_KEY", "supersecret123")
    assert "supersecret123" not in config.redact("error with key supersecret123")
