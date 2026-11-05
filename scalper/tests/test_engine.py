"""Engine: a close is recorded only once even if reconciliation and the close happen at the same time."""
import asyncio

import numpy as np
import pandas as pd
import pytest

from bot import config
from bot.engine import Engine
from bot.fakebroker import FakeBroker
from bot.learner import Learner
from bot.logger import Hub, Logger
from bot.risk import DealingRules, position_size
from bot.store import Store


class NoInfo:
    def news_block(self, inst, now):
        return ""

    def readings(self, inst):
        return {}


def make(tmp_path, monkeypatch):
    monkeypatch.delenv("CAPITAL_API_URL", raising=False)
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    cfg = config.load()
    idx = pd.date_range("2026-10-01", periods=600, freq="1min", tz="UTC")
    df = pd.DataFrame({"o": 100.0, "h": 100.5, "l": 99.5, "c": 100.0}, index=idx)
    br = FakeBroker({"US100": df, "US500": df}, start="2026-10-01T05:00:00", speed=0)
    br.last = {"US100": (99.9, 100.1), "US500": (99.9, 100.1)}
    store = Store(str(tmp_path / "b.db"))
    log = Logger(store, Hub(), str(tmp_path / "logs"))
    ln = Learner(cfg["learner"], cfg["brazos"], {}, store, log)
    return Engine(cfg, store, log, Hub(), br, NoInfo(), ln), br


def test_close_recorded_once_under_race(tmp_path, monkeypatch):
    eng, br = make(tmp_path, monkeypatch)

    async def run():
        r = await br.open_position("US100", 1, 0.01, 95.0)
        deal = br.confirms[r["dealReference"]]["dealId"]
        p = {"deal_id": deal, "arm": "S1-US100", "instrumento": "US100", "dir": 1, "size": 0.01, "entry": 100.1,
             "stop": 95.0, "stop0": 95.0, "tp": None, "atr": 2.0, "opened": 0, "best": 100.0, "shadow": 0}
        eng.positions[deal] = p
        eng.quotes["US100"] = (99.9, 100.1, br.now())
        slow_close = br.close_position

        async def delayed(d):
            res = await slow_close(d)
            await asyncio.sleep(0.05)      # the server already closed it, the confirmation is late
            return res
        br.close_position = delayed
        await asyncio.gather(eng.close(p, "salida"), eng.reconcile(), eng.close(p, "cierre por horario"))
    asyncio.run(run())
    trades = eng.store.trades()
    assert len(trades) == 1
    assert eng.learner.arms["S1-US100"].n_raw == 1
    assert eng.risk.s.live_trades == 1


def test_min_size_cap():
    r = DealingRules(min_size=0.01, step=0.01)
    # $100, 0.5% = $0.50; the minimum 0.01 with a 90-point stop risks $0.90 (0.9%)
    assert position_size(100, 0.5, 90, r)[0] == 0
    size, risk, why = position_size(100, 0.5, 90, r, min_cap_pct=2.0)
    assert size == 0.01 and why == "tamaño mínimo" and risk == pytest.approx(0.9)
    assert position_size(100, 0.5, 300, r, min_cap_pct=2.0)[0] == 0     # $3 > 2% cap: rejected
