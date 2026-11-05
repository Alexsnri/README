"""Tabla spread / rango 5m por bloque (CDMX invierno). Valores copiados de hourly_vol_output.txt,
daily_calib_output.txt y de las páginas de capital.com descargadas el 2026-11-05 ~04:45 UTC.
Uso: python3 -I ratio_table.py"""
spread_pts = {"BTC/USD": (50, 80312.6), "ETH/USD": (1.75, 2416.76), "GOLD": (0.5, 4134.21),
              "US100": (1.8, 28222.5), "US500": (0.6, 7678.8), "EUR/USD": (0.00007, 1.12593),
              "GBP/USD": (0.00013, 1.34911)}
sp = {k: v[0] / v[1] * 1e4 for k, v in spread_pts.items()}
blocks = ["Asia", "Londres", "Solape", "NYtarde", "Cierre"]
r5 = {  # bps, L-V
    "BTC/USD": [11.44, 12.69, 22.69, 15.02, 10.95],
    "ETH/USD": [15.57, 17.07, 29.25, 20.95, 17.55],
    "GOLD": [10.04, 9.47, 16.08, 9.79, 3.01],
    "US100": [7.18, 7.74, 13.83, 10.02, 5.03],
    "US500": [3.65, 4.67, 8.55, 7.15, 3.67],
    "EUR/USD": [1.83, 2.89, 2.98, 1.92, 1.64],
    "GBP/USD": [1.77, 2.80, 2.89, 1.86, 1.59],
}
weekend = {"BTC/USD": (6.10, 7.59), "ETH/USD": (10.02, 13.03)}
# multiplicadores de spread SUPUESTOS (NO VERIFICADOS) por bloque
mult = {"BTC/USD": [1, 1, 1, 1, 1], "ETH/USD": [1, 1, 1, 1, 1],
        "GOLD": [1.5, 1.2, 1, 1.2, 3], "US100": [2, 1.5, 1, 1, 3], "US500": [2, 1.5, 1, 1, 3],
        "EUR/USD": [1.5, 1, 1, 1.2, 3], "GBP/USD": [1.5, 1, 1, 1.2, 3]}
print("spread bps:", {k: round(v, 2) for k, v in sp.items()})
print("instr | " + " | ".join(blocks) + " | Sab | Dom")
for k in r5:
    cells = []
    for i, b in enumerate(blocks):
        nom = sp[k] / r5[k][i]
        adj = sp[k] * mult[k][i] / r5[k][i]
        cells.append(f"{nom:.2f} ({adj:.2f})")
    we = [f"{sp[k]/w:.2f}" for w in weekend.get(k, ())] or ["cerrado", "cerrado"]
    print(k, "|", " | ".join(cells), "|", " | ".join(we))
