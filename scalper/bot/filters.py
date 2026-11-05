"""Filter agent: hard rules. A single failure = the setup is discarded (and the Logger records which rule killed it)."""
from dataclasses import dataclass


@dataclass
class Setup:
    instrument: str
    arm: str
    direction: int
    ts: float
    spread: float          # live ask - bid
    atr: float             # ATR(5m)
    atr_pctile: float      # percentile of the current ATR versus the last 20 days (0-100)
    typical_spread: float  # median recorded spread (or the published one if there is no history)
    has_position: bool
    session_ok: bool
    news_block: str        # "" if there is no event, or the text of the event
    market_open: bool
    quote_age: float       # seconds since the last quote


def evaluate(s: Setup, cfg: dict):
    """Returns (passes, [(rule, ok, value)]). All rules are evaluated (for the dashboard checklist)."""
    f = cfg
    ratio = s.spread / s.atr if s.atr > 0 else float("inf")
    vs_typ = s.spread / s.typical_spread if s.typical_spread > 0 else 1.0
    rules = [
        ("sesión permitida", s.session_ok, "sí" if s.session_ok else "fuera de horario"),
        ("mercado abierto", s.market_open, "abierto" if s.market_open else "cerrado"),
        ("datos frescos", s.quote_age <= f["datos_max_seg"], f"{s.quote_age:.0f}s"),
        (f"spread ≤ {f['spread_max_atr']:.2f} ATR", ratio <= f["spread_max_atr"], f"{ratio:.3f} ATR"),
        (f"spread ≤ {f['spread_max_vs_tipico']:.1f}× típico", vs_typ <= f["spread_max_vs_tipico"], f"{vs_typ:.2f}×"),
        ("sin noticia de alto impacto", not s.news_block, s.news_block or "libre"),
        (f"volatilidad ≥ p{f['atr_percentil_min']}", s.atr_pctile >= f["atr_percentil_min"], f"p{s.atr_pctile:.0f}"),
        (f"volatilidad ≤ p{f['atr_percentil_max']}", s.atr_pctile <= f["atr_percentil_max"], f"p{s.atr_pctile:.0f}"),
        ("sin posición en el instrumento", not s.has_position, "libre" if not s.has_position else "ocupado"),
    ]
    return all(ok for _, ok, _ in rules), rules
