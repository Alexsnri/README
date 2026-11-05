"""Rotation calendar: what the bot trades in each time slot (research/02, section 8).

Everything is anchored to New York time because Capital.com's daily break and the US data releases follow NY
time. Mexico City has had a fixed UTC-6 offset since 2022, so the CDMX time of each slot moves by 1 hour when the
US changes to or from daylight saving time; this module uses the real time zones, so the bot needs no change.

Slots (NY time, Monday to Friday; in winter CDMX = NY - 1 h):
  asia      18:30-03:00  US100, GOLD at half risk
  londres   03:00-08:25  US100, GOLD, EURUSD, US500
  datos     08:25-08:40  no new entries (8:30 ET data)
  prime     08:40-12:00  the whole universe (crypto only here); 09:28-09:35 paused for the cash open
  ny_tarde  12:00-15:45  US100, US500, GOLD
  manejo    15:45-16:40  exits only; crypto is closed at 15:50
  rollover  16:40-18:30  no positions: daily break, overnight funding at 17:00 NY, widest spreads
  cerrado   Friday 16:40 until Sunday 18:30
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

NY = ZoneInfo("America/New_York")
CDMX = ZoneInfo("America/Mexico_City")

SLOTS = ["cerrado", "rollover", "asia", "londres", "datos", "prime", "ny_tarde", "manejo", "apertura"]
DEFAULT_ROTATION = {
    "asia": ["US100", "GOLD"],
    "londres": ["US100", "GOLD", "EURUSD", "US500"],
    "prime": ["US100", "US500", "GOLD", "EURUSD", "BTCUSD", "ETHUSD"],
    "ny_tarde": ["US100", "US500", "GOLD"],
}
SLOT_RISK = {"asia": 0.5}
FLAT_ALL_MIN = 16 * 60 + 40      # 16:40 NY: everything closed
FLAT_CRYPTO_MIN = 15 * 60 + 50   # 15:50 NY: crypto closed (its daily break is 16:00-16:05 NY)


def _slot_codes(minute, weekday):
    """minute = NY minute of day, weekday = NY weekday (Mon=0). Vectorized; returns indexes into SLOTS."""
    m = np.asarray(minute)
    wd = np.asarray(weekday)
    out = np.full(m.shape, SLOTS.index("asia"), dtype=np.int8)
    out[(m >= 3 * 60) & (m < 8 * 60 + 25)] = SLOTS.index("londres")
    out[(m >= 8 * 60 + 25) & (m < 8 * 60 + 40)] = SLOTS.index("datos")
    out[(m >= 8 * 60 + 40) & (m < 12 * 60)] = SLOTS.index("prime")
    out[(m >= 9 * 60 + 28) & (m < 9 * 60 + 35)] = SLOTS.index("apertura")
    out[(m >= 12 * 60) & (m < 15 * 60 + 45)] = SLOTS.index("ny_tarde")
    out[(m >= 15 * 60 + 45) & (m < FLAT_ALL_MIN)] = SLOTS.index("manejo")
    out[(m >= FLAT_ALL_MIN) & (m < 18 * 60 + 30)] = SLOTS.index("rollover")
    closed = (wd == 5) | ((wd == 6) & (m < 18 * 60 + 30)) | ((wd == 4) & (m >= FLAT_ALL_MIN))
    out[closed] = SLOTS.index("cerrado")
    return out


def ny_parts(index_utc: pd.DatetimeIndex):
    ny = index_utc.tz_convert(NY)
    return (ny.hour * 60 + ny.minute).to_numpy(), ny.weekday.to_numpy()


def slot_series(index_utc: pd.DatetimeIndex) -> np.ndarray:
    return _slot_codes(*ny_parts(index_utc))


def entry_mask(index_utc: pd.DatetimeIndex, instrument: str, rotation=None) -> np.ndarray:
    """True where a new entry is allowed in `instrument` (vectorized, used by the backtest)."""
    rotation = rotation or DEFAULT_ROTATION
    codes = slot_series(index_utc)
    ok = np.zeros(len(codes), dtype=bool)
    for slot, insts in rotation.items():
        if instrument in insts:
            ok |= codes == SLOTS.index(slot)
    return ok


def flatten_mask(index_utc: pd.DatetimeIndex, instrument: str, family: str) -> np.ndarray:
    """True where an open position in `instrument` must be closed."""
    m, wd = ny_parts(index_utc)
    codes = _slot_codes(m, wd)
    must = (codes == SLOTS.index("rollover")) | (codes == SLOTS.index("cerrado"))
    if family == "crypto":
        must |= (m >= FLAT_CRYPTO_MIN) | (m < 8 * 60 + 40)
    return must


# ---- scalar versions for the live bot ----
def now_utc():
    return datetime.now(timezone.utc)


def slot_at(ts: datetime) -> str:
    ny = ts.astimezone(NY)
    return SLOTS[int(_slot_codes(np.array([ny.hour * 60 + ny.minute]), np.array([ny.weekday()]))[0])]


def can_enter(ts: datetime, instrument: str, rotation=None) -> bool:
    rotation = rotation or DEFAULT_ROTATION
    return instrument in rotation.get(slot_at(ts), [])


def must_flatten(ts: datetime, instrument: str, family: str) -> bool:
    idx = pd.DatetimeIndex([ts]).tz_convert("UTC")
    return bool(flatten_mask(idx, instrument, family)[0])


def risk_multiplier(ts: datetime) -> float:
    return SLOT_RISK.get(slot_at(ts), 1.0)


def spread_multiplier(index_utc: pd.DatetimeIndex, family: str) -> np.ndarray:
    """Assumed spread widening by slot (research/02, section 3, NOT VERIFIED). Backtest only."""
    m, wd = ny_parts(index_utc)
    codes = _slot_codes(m, wd)
    mult = np.ones(len(codes))
    asia = codes == SLOTS.index("asia")
    if family in ("fx", "metal"):
        mult[asia] = 1.5
    elif family == "index":
        cash = (m >= 9 * 60 + 30) & (m < 16 * 60)
        mult[~cash] = 1.5
        mult[asia] = 2.0
    mult[(codes == SLOTS.index("rollover")) | (codes == SLOTS.index("manejo"))] *= 2.0
    return mult


def cdmx_str(ts: datetime) -> str:
    return ts.astimezone(CDMX).strftime("%H:%M")
