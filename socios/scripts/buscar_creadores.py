#!/usr/bin/env python3
"""Cazador: busca creadores de YouTube del nicho y arma la lista de prospectos.

Usa la API oficial y gratuita de YouTube (YouTube Data API v3, 10,000 unidades al día).
Cada corrida completa gasta unas 100 unidades por palabra clave, así que alcanza para
unas 80 palabras clave al día.

Uso:
    YOUTUBE_API_KEY=tu_llave python3 socios/scripts/buscar_creadores.py
    python3 socios/scripts/buscar_creadores.py --palabras "salir de deudas" "ahorro"
    python3 socios/scripts/buscar_creadores.py --max 5     # prueba corta

Resultado: socios/data/prospectos.csv (no se sube al repo: tiene correos de personas).
Si el archivo ya existe, conserva el estado y las notas de cada creador y solo agrega o
actualiza números.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import statistics
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "config.json"
SALIDA = RAIZ / "data" / "prospectos.csv"
API = "https://www.googleapis.com/youtube/v3/"

CORREO = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
INSTAGRAM = re.compile(r"instagram\.com/([A-Za-z0-9._]{2,30})", re.I)
TIKTOK = re.compile(r"tiktok\.com/@([A-Za-z0-9._]{2,30})", re.I)
# Señales de que ya vende algo propio. No los descarta: baja su prioridad y el escritor
# cambia el ángulo ("mejoramos lo que ya tienes" en vez de "tu primer producto").
YA_VENDE = re.compile(
    r"hotmart|stan\.store|whop\.com|gumroad|payhip|kajabi|teachable|skool\.com|"
    r"mi curso|mi ebook|mi libro|mentor[ií]a|membres[ií]a|plantilla de pago",
    re.I,
)
CORREOS_IGNORADOS = ("example.com", "sentry", "wixpress", "noreply", "no-reply", "pixabay", "epidemicsound",
                     "artlist", "envato", "canva.com", "donacion", "donation")

COLUMNAS = [
    "canal_id", "canal", "url", "pais", "suscriptores", "videos",
    "vistas_medianas", "vistas_entre_subs", "likes_por_vista", "comentarios_por_vista",
    "dias_ultimo_video", "videos_por_mes", "correo", "instagram", "tiktok",
    "ya_vende", "relevancia", "puntaje", "videos_recientes", "estado", "notas", "actualizado",
]


def llamar(recurso: str, **params) -> dict:
    """GET a la API. La llave va en el encabezado X-Goog-Api-Key si existe la variable."""
    url = API + recurso + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    llave = os.environ.get("YOUTUBE_API_KEY")
    if llave:
        req.add_header("X-Goog-Api-Key", llave)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode("utf-8", "replace")[:400]
        sys.exit(f"YouTube respondió {e.code} en {recurso}: {cuerpo}\n"
                 "¿Pusiste YOUTUBE_API_KEY y activaste 'YouTube Data API v3' en Google Cloud?")


def en_lotes(items: list, n: int = 50):
    for i in range(0, len(items), n):
        yield items[i:i + n]


def buscar_canales(palabras: list[str], cfg: dict) -> list[str]:
    """Busca videos recientes por palabra clave y junta los canales que los subieron.

    Buscar videos (y no canales) filtra solo a creadores activos en el tema.
    """
    desde = (dt.datetime.now(dt.timezone.utc)
             - dt.timedelta(days=cfg["busqueda"]["dias_hacia_atras"]))
    vistos: dict[str, None] = {}
    for palabra in palabras:
        datos = llamar(
            "search", part="snippet", type="video", q=palabra,
            maxResults=cfg["busqueda"]["resultados_por_palabra"],
            regionCode=cfg["region"], relevanceLanguage=cfg["idioma"],
            publishedAfter=desde.strftime("%Y-%m-%dT%H:%M:%SZ"), order="relevance",
        )
        for item in datos.get("items", []):
            vistos.setdefault(item["snippet"]["channelId"], None)
        print(f"  «{palabra}»: {len(vistos)} canales acumulados", file=sys.stderr)
    return list(vistos)


def detalles_canales(ids: list[str]) -> list[dict]:
    canales = []
    for lote in en_lotes(ids):
        datos = llamar("channels", part="snippet,statistics,contentDetails", id=",".join(lote))
        canales.extend(datos.get("items", []))
    return canales


def videos_recientes(uploads: str, cuantos: int) -> list[dict]:
    lista = llamar("playlistItems", part="contentDetails", playlistId=uploads, maxResults=cuantos)
    ids = [i["contentDetails"]["videoId"] for i in lista.get("items", [])]
    if not ids:
        return []
    datos = llamar("videos", part="snippet,statistics,contentDetails", id=",".join(ids))
    return datos.get("items", [])


def extraer(textos: list[str], patron: re.Pattern) -> str:
    for t in textos:
        for m in patron.finditer(t or ""):
            valor = m.group(1) if patron.groups else m.group(0)
            if not any(x in valor.lower() for x in CORREOS_IGNORADOS):
                return valor.strip(".")
    return ""


def relevancia(videos: list[dict], terminos: list[str]) -> float:
    """Fracción de videos recientes cuyo título o etiquetas hablan del tema."""
    if not videos:
        return 0.0
    def habla(v: dict) -> bool:
        texto = (v["snippet"].get("title", "") + " " + " ".join(v["snippet"].get("tags", []))).lower()
        return any(t in texto for t in terminos)
    return round(sum(habla(v) for v in videos) / len(videos), 2)


def analizar(canal: dict, videos: list[dict], ahora: dt.datetime, terminos: list[str] = ()) -> dict:
    sn, st = canal["snippet"], canal.get("statistics", {})
    subs = int(st.get("subscriberCount", 0) or 0)
    vistas = [int(v["statistics"].get("viewCount", 0)) for v in videos]
    likes = [int(v["statistics"].get("likeCount", 0)) for v in videos]
    coments = [int(v["statistics"].get("commentCount", 0)) for v in videos]
    fechas = sorted(
        (dt.datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00")) for v in videos),
        reverse=True,
    )
    mediana = statistics.median(vistas) if vistas else 0
    total_vistas = sum(vistas) or 1
    dias_ultimo = (ahora - fechas[0]).days if fechas else 9999
    if len(fechas) >= 2:
        rango = max((fechas[0] - fechas[-1]).days, 1)
        por_mes = round((len(fechas) - 1) * 30 / rango, 1)
    else:
        por_mes = 0.0
    textos = [sn.get("description", "")] + [v["snippet"].get("description", "") for v in videos]
    return {
        "canal_id": canal["id"],
        "canal": sn.get("title", ""),
        "url": f"https://www.youtube.com/channel/{canal['id']}",
        "pais": sn.get("country", ""),
        "suscriptores": subs,
        "videos": int(st.get("videoCount", 0) or 0),
        "vistas_medianas": int(mediana),
        "vistas_entre_subs": round(mediana / subs, 3) if subs else 0,
        "likes_por_vista": round(sum(likes) / total_vistas, 4),
        "comentarios_por_vista": round(sum(coments) / total_vistas, 4),
        "dias_ultimo_video": dias_ultimo,
        "videos_por_mes": por_mes,
        # El correo del canal manda; el de las descripciones de videos es respaldo (suele ser de créditos).
        "correo": extraer(textos[:1], CORREO) or extraer(textos[1:], CORREO),
        "instagram": extraer(textos, INSTAGRAM),
        "tiktok": extraer(textos, TIKTOK),
        "ya_vende": "sí" if any(YA_VENDE.search(t or "") for t in textos) else "no",
        "relevancia": relevancia(videos, list(terminos)),
        "videos_recientes": " | ".join(v["snippet"]["title"] for v in videos[:3]),
    }


def puntaje(p: dict) -> float:
    """0 a 100. Premia audiencia que de verdad ve y comenta (confianza), constancia y correo.

    Los comentarios pesan más que los likes: comentar es la señal más cercana a comprar.
    """
    s = 0.0
    s += min(p["vistas_entre_subs"] / 0.30, 1) * 30          # 30% de sus subs ve cada video = máximo
    s += min(p["comentarios_por_vista"] / 0.005, 1) * 25     # 0.5% comenta = máximo
    s += min(p["likes_por_vista"] / 0.05, 1) * 10
    s += min(p["videos_por_mes"] / 8, 1) * 15                 # 2 por semana = máximo
    s += 10 if p["correo"] else 0
    s += 10 if p["ya_vende"] == "no" else 0
    return round(s, 1)


def pasa_filtros(p: dict, f: dict) -> bool:
    return (f["suscriptores_min"] <= p["suscriptores"] <= f["suscriptores_max"]
            and p["dias_ultimo_video"] <= f["dias_desde_ultimo_video_max"]
            and p["vistas_entre_subs"] >= f["vistas_entre_suscriptores_min"]
            and p["relevancia"] >= f.get("relevancia_min", 0))


def leer_existentes() -> dict[str, dict]:
    if not SALIDA.exists():
        return {}
    with SALIDA.open(newline="", encoding="utf-8") as fh:
        return {r["canal_id"]: r for r in csv.DictReader(fh)}


def guardar(filas: list[dict]) -> None:
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    filas.sort(key=lambda r: float(r.get("puntaje") or 0), reverse=True)
    with SALIDA.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--palabras", nargs="+", help="palabras clave (por defecto, las de config.json)")
    ap.add_argument("--max", type=int, default=0, help="revisar como máximo N canales (para probar)")
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    palabras = args.palabras or cfg["palabras_clave"]
    f = cfg["filtros"]
    ahora = dt.datetime.now(dt.timezone.utc)

    print(f"Buscando en {len(palabras)} palabras clave…", file=sys.stderr)
    ids = buscar_canales(palabras, cfg)
    canales = detalles_canales(ids)
    # Primero el filtro barato (suscriptores) para no gastar cuota en canales que no sirven.
    canales = [c for c in canales
               if f["suscriptores_min"] <= int(c.get("statistics", {}).get("subscriberCount", 0) or 0)
               <= f["suscriptores_max"]]
    if args.max:
        canales = canales[: args.max]
    print(f"Analizando {len(canales)} canales en rango de suscriptores…", file=sys.stderr)

    existentes = leer_existentes()
    nuevos = 0
    for c in canales:
        uploads = c.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
        if not uploads:
            continue
        p = analizar(c, videos_recientes(uploads, f["videos_a_revisar"]), ahora, cfg.get("terminos_tema", []))
        if not pasa_filtros(p, f):
            existentes.pop(p["canal_id"], None)  # dejó de calificar (p. ej. por el filtro de tema)
            continue
        p["puntaje"] = puntaje(p)
        p["actualizado"] = ahora.date().isoformat()
        previo = existentes.get(p["canal_id"])
        if previo:
            p["estado"], p["notas"] = previo.get("estado", ""), previo.get("notas", "")
            p["correo"] = p["correo"] or previo.get("correo", "")  # no borrar un correo ya encontrado a mano
        else:
            p["estado"], p["notas"] = "nuevo", ""
            nuevos += 1
        existentes[p["canal_id"]] = p

    guardar(list(existentes.values()))
    con_correo = sum(1 for r in existentes.values() if r.get("correo"))
    print(f"Listo: {nuevos} nuevos, {len(existentes)} en total, {con_correo} con correo → {SALIDA}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
