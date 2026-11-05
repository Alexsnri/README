"""Instruments the bot knows about.

The spreads are the ones Capital.com published on 2026-11-05 (research/02, section 3). They are only used by the
backtest and as a fallback: live, the bot always uses the real bid/ask from the stream, and minimum sizes and stop
distances come from `dealingRules` on GET /markets/{epic}.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Instrument:
    name: str          # internal name (= epic in Capital.com, verified at startup)
    epic: str
    family: str        # index | metal | fx | crypto
    spread_bps: float  # typical published spread, in basis points of price
    data: tuple        # historical source for the backtest (source, symbol)


INSTRUMENTS = {
    "US100": Instrument("US100", "US100", "index", 0.64, ("histdata", "NSXUSD")),
    "US500": Instrument("US500", "US500", "index", 0.78, ("histdata", "SPXUSD")),
    "GOLD": Instrument("GOLD", "GOLD", "metal", 1.21, ("histdata", "XAUUSD")),
    "EURUSD": Instrument("EURUSD", "EURUSD", "fx", 0.62, ("histdata", "EURUSD")),
    "GBPUSD": Instrument("GBPUSD", "GBPUSD", "fx", 0.96, ("histdata", "GBPUSD")),
    "BTCUSD": Instrument("BTCUSD", "BTCUSD", "crypto", 6.23, ("binance", "BTCUSDT")),
    "ETHUSD": Instrument("ETHUSD", "ETHUSD", "crypto", 7.24, ("binance", "ETHUSDT")),
}
