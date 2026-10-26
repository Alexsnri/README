"""
Genera seed_learning.json: los últimos 30 resultados (en R) de cada estrategia x mercado según el
backtest de 20 años en modo Turbo. Con esto el bot arranca sabiendo lo que aprendió en la historia, y
cada trade real va reemplazando poco a poco a los históricos.

Uso: python make_seed.py <carpeta_con_json_de_yahoo>
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "backtest"))
from backtest import UNIVERSE, indicators, load, run  # noqa: E402

CODES = {"donchian": "D", "tsmom": "T", "meanrev": "M"}

folder = sys.argv[1]
data = {f[:-5]: indicators(load(os.path.join(folder, f))) for f in os.listdir(folder) if f[:-5] in UNIVERSE}
_, trades = run(data, risk=0.04, max_heat=0.25, lev=40)
trades = trades.sort_values("exit_date")
seed = {}
for (sym, strat), g in trades.groupby(["sym", "strat"]):
    seed[f"{UNIVERSE[sym][0]}_{CODES[strat]}"] = [round(r, 3) for r in g.R.tail(30)]
json.dump(dict(sorted(seed.items())), open(os.path.join(HERE, "seed_learning.json"), "w"), indent=1)
print(f"{len(seed)} brazos, {sum(map(len, seed.values()))} trades históricos")
