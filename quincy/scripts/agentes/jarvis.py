"""Jarvis de Quincy: arma un resumen corto para escucharlo en voz alta (por ejemplo, al subirte a la camioneta).

Junta: visitas de Cloudflare (si existe CF_API_TOKEN), si el sitio está arriba, qué hicieron los agentes hoy,
lo que le toca al dueño, cuenta regresiva y quién trabaja después. Deja el texto en .github/jarvis/resumen.txt
(el iPhone lo lee desde raw.githubusercontent.com con un Atajo).

Uso:  python3 quincy/scripts/agentes/jarvis.py [--stdout]
"""
import datetime as dt
import json
import os
import random
import re
import sys
import urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jarvis_frases as F  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO = os.path.dirname(ROOT)
BITACORA = os.path.join(ROOT, "agentes", "bitacora.md")
OUT = os.path.join(REPO, ".github", "jarvis", "resumen.txt")
OUT_VARIANTES = os.path.join(REPO, ".github", "jarvis", "variantes.txt")
N_VARIANTES = 10
SEPARADOR = "~~~"
SITE = "https://quincy-mx.github.io/"
CF_SITE_TOKEN = "7867bd7b5a2449549624cefc62551f12"  # token público del beacon (js/core.js)
TZ = ZoneInfo("America/Mexico_City")
NOW = dt.datetime.fromisoformat(os.environ["NOW"]).replace(tzinfo=TZ) if os.environ.get("NOW") else dt.datetime.now(TZ)

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# Horario de los agentes (hora de la Ciudad de México): (nombre, días de la semana 0=lunes | días del mes, hora, minuto)
AGENDA = [
    ("el Director", {"dow": [6]}, 18, 37),
    ("el de Producto", {"dow": [0, 4]}, 21, 22),
    ("el de Ley y datos", {"dow": [1]}, 21, 13),
    ("el de SEO", {"dow": [2]}, 22, 41),
    ("el de SEO", {"dow": [5]}, 17, 48),
    ("el de Contenido", {"dow": [3]}, 20, 26),
    ("el de la lana", {"dom": [1, 15]}, 20, 44),
    ("el de Marca", {"dom": [3]}, 19, 52),
]

CHISTES_VIEJOS = [
    "Tú tranquilo, que aquí los únicos que chambean son ellos.",
    "Ellos no piden aguinaldo. Tú sí deberías calcular el tuyo.",
    "Si alguien pregunta, sí tienes empleados. Digitales, pero empleados.",
    "Maneja con cuidado, jefe, que tú eres el único sin respaldo.",
    "Qué pedo con esos pendientes, jefe. Los míos ya están hechos.",
    "Ya ni el Director te cree que lo vas a hacer hoy.",
]


def get(url, headers=None, data=None, timeout=20):
    req = urllib.request.Request(url, data=data, headers=headers or {"User-Agent": "quincy-jarvis/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def hablado(t):
    """Limpia texto de la bitácora para que se oiga bien en voz alta."""
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"`([^`]*)`", lambda m: re.sub(r"\.(html|py|js|json|md|yml|txt)\b", "", m.group(1)).strip("/").split("/")[-1].replace("_", " ").replace("-", " "), t)
    t = re.sub(r"\(\d+\)\s*", "", t)
    t = re.sub(r"\([^)]*\)", "", t)
    t = re.sub(r"\*\*|__|\*", "", t)
    t = t.replace("→", " a ").replace("·", ",").replace("≈", "unos ").replace("%", " por ciento")
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\s+([.,:;])", r"\1", t).strip(" ,;:.")
    return t


def frase(t, n=170):
    t = hablado(t)
    corte = re.split(r"(?<=[.;:])\s", t)[0].rstrip(".;:")
    if len(corte) > n:
        corte = corte[:n]
        for sep in (", ", " y ", " "):
            i = corte.rfind(sep)
            if i > n * 0.5:
                corte = corte[:i]
                break
    if len(corte) < len(t):
        sueltas = {"de", "del", "la", "el", "los", "las", "en", "y", "a", "al", "que", "con", "para", "por", "o", "un", "una", "se", "ya", "dice", "su", "sus", "desde", "hasta", "sobre"}
        pal = corte.rstrip(".;:, ").split()
        while len(pal) > 3 and pal[-1].lower() in sueltas:
            pal.pop()
        corte = " ".join(pal)
    return corte.rstrip(".;:, ") + "."


def entradas():
    txt = open(BITACORA, encoding="utf-8").read()
    out = []
    for bloque in re.split(r"^## ", txt, flags=re.M)[1:]:
        cab, _, cuerpo = bloque.partition("\n")
        m = re.match(r"(\d{4}-\d{2}-\d{2}) · (.+)", cab.strip())
        if not m:
            continue
        campos = {}
        for k in ("Hice", "Encontré", "Para el dueño"):
            mm = re.search(rf"^- {k}:(.*?)(?=^- |\Z)", cuerpo, flags=re.S | re.M)
            if mm:
                campos[k] = " ".join(mm.group(1).split())
        out.append({"fecha": m.group(1), "agente": re.sub(r"\s*\(.*?\)\s*$", "", m.group(2)).strip(), **campos})
    return out


def visitas():
    token = os.environ.get("CF_API_TOKEN", "").strip()
    if not token:
        return {"estado": "sin_token"}
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "quincy-jarvis/1.0"}
    try:
        _, body = get("https://api.cloudflare.com/client/v4/accounts", h)
        acc = json.loads(body)["result"][0]["id"]
        _, body = get(f"https://api.cloudflare.com/client/v4/accounts/{acc}/rum/site_info/list?per_page=50", h)
        sites = json.loads(body)["result"]
        tag = next((s["site_tag"] for s in sites if s.get("site_token") == CF_SITE_TOKEN), sites[0]["site_tag"])
        def rango(desde):
            q = """query($a:string!,$t:string!,$d:Time!,$h:Time!){viewer{accounts(filter:{accountTag:$a}){
              tot: rumPageloadEventsAdaptiveGroups(limit:1, filter:{siteTag:$t, datetime_geq:$d, datetime_leq:$h}){ count sum{ visits } }
              pag: rumPageloadEventsAdaptiveGroups(limit:2, orderBy:[count_DESC], filter:{siteTag:$t, datetime_geq:$d, datetime_leq:$h}){ count dimensions{ requestPath } }
              ref: rumPageloadEventsAdaptiveGroups(limit:3, orderBy:[count_DESC], filter:{siteTag:$t, datetime_geq:$d, datetime_leq:$h}){ count dimensions{ refererHost } }
            }}}"""
            fin = dt.datetime.now(dt.timezone.utc)
            var = {"a": acc, "t": tag, "d": (fin - desde).strftime("%Y-%m-%dT%H:%M:%SZ"), "h": fin.strftime("%Y-%m-%dT%H:%M:%SZ")}
            _, body = get("https://api.cloudflare.com/client/v4/graphql", h, json.dumps({"query": q, "variables": var}).encode())
            return json.loads(body)["data"]["viewer"]["accounts"][0]
        hoy, sem = rango(dt.timedelta(hours=24)), rango(dt.timedelta(days=7))
        v24 = sum(g["sum"]["visits"] for g in hoy["tot"]) if hoy["tot"] else 0
        v7 = sum(g["sum"]["visits"] for g in sem["tot"]) if sem["tot"] else 0
        pag = [g["dimensions"]["requestPath"] for g in hoy["pag"] if g["dimensions"]["requestPath"]]
        refs = [g["dimensions"]["refererHost"] for g in hoy["ref"] if g["dimensions"]["refererHost"] and "quincy" not in g["dimensions"]["refererHost"]]
        return {"estado": "ok", "v24": v24, "v7": v7,
                "pagina": (pag[0].strip("/").replace("-", " ").replace(".html", "") or "la portada") if pag else "",
                "fuentes": " y ".join(r.replace("www.", "").replace("l.instagram.com", "Instagram").replace(".com", "") for r in refs[:2])}
    except Exception as e:  # nunca tumbar el resumen por las visitas
        print(f"Cloudflare: {e}", file=sys.stderr)
        return {"estado": "error"}


def sitio():
    malas = []
    for p in ["", "aguinaldo/", "app.html"]:
        try:
            st, _ = get(SITE + p, timeout=15)
            if st != 200:
                malas.append(p or "portada")
        except Exception:
            malas.append(p or "portada")
    return [m.strip("/").replace(".html", "") for m in malas]


def cuentas(rng):
    hoy = NOW.date()
    out = []
    lanz = dt.date(2026, 11, 2)
    if hoy < lanz:
        d = (lanz - hoy).days
        out.append(rng.choice(F.LANZAMIENTO_MANANA) if d == 1 else rng.choice(F.LANZAMIENTO).format(dias=d))
    elif hoy == lanz:
        out.append(rng.choice(F.LANZAMIENTO_HOY))
    ag = dt.date(hoy.year, 12, 19)
    if dt.date(hoy.year, 11, 1) <= hoy <= ag:
        out.append(rng.choice(F.AGUINALDO).format(dias=(ag - hoy).days))
    return " ".join(out)

# Pase de lista: nombre en la bitácora -> (cómo se dice, apodo)
EQUIPO = [
    ("Director", "el Director", "el que manda después de ti, aunque a veces parece que antes"),
    ("Producto y diseño", "el de Producto", "el diseñador mamón"),
    ("SEO", "el de SEO", "el que le ruega a Google"),
    ("Contenido", "el de Contenido", "tu influencer de planta"),
    ("Ley y datos", "el de Ley y datos", "el licenciado"),
    ("Monetización", "el de la lana", "el que sueña con tu primer peso"),
    ("Marca", "el de Marca", "el vigilante del IMPI"),
]
PRIORIDADES = os.path.join(ROOT, "agentes", "estado", "prioridades.md")


def cuando_toca(alias):
    for minutos in range(1, 60 * 24 * 32):
        t = NOW + dt.timedelta(minutes=minutos)
        for nombre, cuando, hh, mm in AGENDA:
            if nombre != alias:
                continue
            ok = (t.weekday() in cuando.get("dow", [])) or (t.day in cuando.get("dom", []))
            if ok and t.hour == hh and t.minute == mm:
                dia = "hoy" if t.date() == NOW.date() else ("mañana" if t.date() == NOW.date() + dt.timedelta(days=1) else f"el {DIAS[t.weekday()]}")
                return f"{dia} a las {(hh - 1) % 12 + 1}:{mm:02d} de la {'noche' if hh >= 19 else 'tarde'}"
    return ""


def en_que_anda():
    try:
        txt = open(PRIORIDADES, encoding="utf-8").read()
    except OSError:
        return {}
    out = {}
    for m in re.finditer(r"\*\*([^*·]+?) · ([^*]+?)\.?\*\*", txt):
        out[m.group(1).strip()] = hablado(m.group(2))
    for m in re.finditer(r"\*\*(Ley y datos|Monetización|Marca|Director)\*\* ([^;\n]+)", txt):
        out.setdefault(m.group(1), hablado(m.group(2)))
    return out


def pase_de_lista(ents, rng):
    hoy, ayer = NOW.date().isoformat(), (NOW.date() - dt.timedelta(days=1)).isoformat()
    items = []
    for nombre, _, _ in EQUIPO:
        e = next((x for x in ents if x["agente"].startswith(nombre) and "Hice" in x and x["fecha"] in (hoy, ayer)), None)
        if e:
            apodo = rng.choice(F.APODOS[nombre])
            linea = rng.choice(F.PASE_LINEA).format(nombre=apodo, hecho=frase(e["Hice"], 60))
            items.append(linea[0].upper() + linea[1:])
    if not items:
        return [rng.choice(F.PASE_NADIE)]
    rng.shuffle(items)
    return [rng.choice(F.PASE_INTRO).format(n=len(items))] + items[:4]


def proximo():
    """(quién, cuándo) del próximo agente en el horario."""
    for minutos in range(1, 60 * 24 * 32):
        t = NOW + dt.timedelta(minutes=minutos)
        for nombre, cuando, hh, mm in AGENDA:
            ok = (t.weekday() in cuando.get("dow", [])) or (t.day in cuando.get("dom", []))
            if ok and t.hour == hh and t.minute == mm:
                dia = "hoy" if t.date() == NOW.date() else ("mañana" if t.date() == NOW.date() + dt.timedelta(days=1) else f"el {DIAS[t.weekday()]}")
                h12 = (hh - 1) % 12 + 1
                parte = "de la noche" if hh >= 19 else ("de la tarde" if hh >= 12 else "de la mañana")
                return (nombre.replace("el de ", "", 1), f"{dia} a las {h12}:{mm:02d}")
    return None


def resumen(rng, datos):
    hora = NOW.hour
    momento = "mañana" if hora < 12 else ("tarde" if hora < 19 else "noche")
    partes = [rng.choice(F.INTROS).format(saludo=rng.choice(F.SALUDOS[momento])), cuentas(rng)]

    v = datos["visitas"]
    if v["estado"] == "ok":
        txt = rng.choice(F.VISITAS_OK).format(v24=v["v24"], v7=v["v7"])
        if v["v24"] == 0:
            txt += " " + rng.choice(F.VISITAS_CERO)
        else:
            if v["pagina"]:
                txt += " " + rng.choice(F.PAGINA_TOP).format(pagina=v["pagina"])
            if v["fuentes"]:
                txt += " " + rng.choice(F.FUENTES).format(fuentes=v["fuentes"])
        partes.append(txt)
    else:
        partes.append(rng.choice(F.VISITAS_SIN_TOKEN if v["estado"] == "sin_token" else F.VISITAS_ERROR))
    if datos["malas"]:
        partes.append(rng.choice(F.SITIO_MAL).format(paginas=", ".join(datos["malas"])))

    pase = pase_de_lista(datos["ents"], rng)
    tarea = rng.choice(F.TAREA).format(tarea=frase(datos["dueño"], 90)) if datos["dueño"] else ""
    sigue = ""
    if datos["sigue"]:
        quien, cuando = datos["sigue"]
        sigue = rng.choice(F.SIGUE).format(quien=quien, cuando=cuando)
    cierre = rng.choice(F.CIERRES)

    def armar():
        return [p for p in partes + pase + [tarea, sigue, cierre] if p]

    # máximo ~45 segundos (unas 115 palabras): primero se recorta el pase de lista, luego el "sigue"
    while len(" ".join(armar()).split()) > 115:
        if len(pase) > 3:
            pase.pop()
        elif sigue:
            sigue = ""
        elif datos["dueño"] and len(tarea) > 80:
            tarea = rng.choice(F.TAREA).format(tarea=frase(datos["dueño"], 55))
        else:
            break
    texto = "\n".join(armar())
    texto = re.sub(r"\bde el\b", "del", texto)
    texto = re.sub(r"\ba el\b", "al", texto)
    return texto.replace('"', "")


def datos_del_momento():
    ents = entradas()
    return {"visitas": visitas(), "malas": sitio(), "ents": ents, "sigue": proximo(),
            "dueño": next((e["Para el dueño"] for e in ents if e.get("Para el dueño") and e["agente"].startswith("Director")), "")}


def main():
    datos = datos_del_momento()
    semilla = int(NOW.timestamp()) // 60
    versiones = [resumen(random.Random(semilla * 100 + i), datos) for i in range(N_VARIANTES)]
    if "--stdout" in sys.argv:
        print(f"\n{SEPARADOR}\n".join(versiones))
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(versiones[0] + "\n")
    with open(OUT_VARIANTES, "w", encoding="utf-8") as f:
        f.write(f"\n{SEPARADOR}\n".join(versiones) + "\n")
    print(versiones[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
