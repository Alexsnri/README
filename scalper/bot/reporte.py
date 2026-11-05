"""Report for the day and accumulated from the command line: `python -m bot.reporte` (on a VPS:
`docker exec scalper python -m bot.reporte`). The same report comes in Telegram with /reporte and on the dashboard."""
import os

from . import config, report
from .learner import Learner
from .store import Store


def main():
    cfg = config.load()
    store = Store(os.path.join(cfg["data_dir"], "bot.db"))
    learner = Learner(cfg["learner"], cfg["brazos"], {}, store, lambda *a, **k: None)
    eq = store.q("SELECT balance, upl FROM equity ORDER BY ts DESC LIMIT 1")
    acct = {"balance": eq[0]["balance"], "upl": eq[0]["upl"]} if eq else {}
    print(report.to_text(report.build(store, learner, acct, store.kv_get("start_balance"))))


if __name__ == "__main__":
    main()
