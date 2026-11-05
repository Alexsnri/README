"""Stop Manager logic (research/05). A pure function that the backtest (compiled with numba) and the live bot both use.

Rules:
 1. When the favorable move (measured on the close of the 1-minute bar, on the side we would close at) reaches
    `be_trig` ATR, the stop moves to break-even plus a buffer (`be_buf`, in price) that covers slippage. From
    then on the trade can no longer lose, unless there is a gap.
 2. When the move reaches `trail_start` ATR, the stop follows the best price at `trail_mult` ATR.
 3. The stop only moves in favor, never against.
"""


def update_stop(direction, entry, stop, best, atr, be_trig, be_buf, trail_mult, trail_start):
    """direction +1/-1; best = best close in our favor since entry. Returns the new stop."""
    if atr <= 0.0:
        return stop
    fav = direction * (best - entry) / atr
    new = stop
    if be_trig > 0.0 and fav >= be_trig:
        cand = entry + direction * be_buf
        if direction * (cand - new) > 0.0:
            new = cand
    if trail_mult > 0.0 and fav >= trail_start:
        cand = best - direction * trail_mult * atr
        if direction * (cand - new) > 0.0:
            new = cand
    return new


def stop_reason(direction, entry, old, new, be_buf):
    """Text for the log: why the stop moved."""
    if abs(new - (entry + direction * be_buf)) < 1e-12:
        return "break-even + costos"
    return "trailing"


# Exit policies the backtest compares ("move early" vs "let it breathe")
POLICIES = {
    "fijo": dict(be_trig=0.0, trail_mult=0.0, trail_start=0.0),
    "be1.0": dict(be_trig=1.0, trail_mult=0.0, trail_start=0.0),
    "be1.5": dict(be_trig=1.5, trail_mult=0.0, trail_start=0.0),
    "be1.0+tr2.0": dict(be_trig=1.0, trail_mult=2.0, trail_start=1.0),
}
