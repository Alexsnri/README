"""Actualiza futuro/data/rates.json con la tasa de CETES a 28 días y la inflación anual
desde la API oficial del Banco de México (SIE). Corre cada semana en GitHub Actions.

Necesita el secreto BANXICO_TOKEN (gratis en https://www.banxico.org.mx/SieAPIRest/service/v1/token).
Si no hay token, o si la respuesta no es la serie esperada, no toca nada.
"""
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]

RATES = Path(__file__).resolve().parent.parent / "data" / "rates.json"
SERIES = {
    # id: (campo en rates.json, grupos de palabras: de cada grupo, al menos una debe aparecer en el título)
    "SF43936": ("cetes28", [("cetes",), ("28",)]),
    "SP30578": ("inflacion", [("inflaci", "precios"), ("anual",)]),
}


def main() -> int:
    token = os.environ.get("BANXICO_TOKEN", "").strip()
    if not token:
        print("Sin BANXICO_TOKEN: se conservan las tasas actuales.")
        return 0

    url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/" + ",".join(SERIES) + "/datos/oportuno"
    req = urllib.request.Request(url, headers={"Bmx-Token": token, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)

    rates = json.loads(RATES.read_text(encoding="utf-8"))
    changed = False
    for serie in payload["bmx"]["series"]:
        field, words = SERIES[serie["idSerie"]]
        title = serie.get("titulo", "")
        if not all(any(w in title.lower() for w in group) for group in words):
            print(f"La serie {serie['idSerie']} no parece ser '{field}' (título: {title!r}). No se actualiza.")
            continue
        dato = serie["datos"][-1]
        value = round(float(dato["dato"].replace(",", "")), 2)
        if not 0 < value < 30:
            print(f"Valor fuera de rango para {field}: {value}. No se actualiza.")
            continue
        if rates.get(field) != value:
            rates[field] = value
            changed = True
        # Banxico fecha la inflación con el día 1 del mes (01/09/2026 = septiembre) y CETES con el día de colocación.
        _, mes, anio = dato["fecha"].split("/")
        if field == "inflacion":
            fuente = f"INPC, variación anual de {MESES[int(mes) - 1]} de {anio} (INEGI, vía Banco de México SIE)"
        else:
            fuente = f"Subasta semanal de CETES a 28 días, colocación del {dato['fecha']} (Banco de México, SIE)"
        rates[f"{field}_fuente"] = fuente
        print(f"{field} = {value} ({dato['fecha']})")

    if changed:
        rates["actualizado"] = date.today().isoformat()
    RATES.write_text(json.dumps(rates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
