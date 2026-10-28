"""Jarvis de Quincy: arma un resumen corto para escucharlo en voz alta (por ejemplo, al subirte a la camioneta).

Junta: visitas de Cloudflare (si existe CF_API_TOKEN), si el sitio está arriba, qué hicieron los agentes hoy,
lo que le toca al dueño, cuenta regresiva y quién trabaja después. Deja el texto en .github/jarvis/resumen.txt
(el iPhone lo lee desde raw.githubusercontent.com con un Atajo).

Uso:  python3 quincy/scripts/agentes/jarvis.py [--stdout]
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO = os.path.dirname(ROOT)
BITACORA = os.path.join(ROOT, "agentes", "bitacora.md")
OUT = os.path.join(REPO, ".github", "jarvis", "resumen.txt")
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

CHISTES = [
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
        return "Visitas no te puedo decir: sigue sin aparecer el token de Cloudflare. Ese es pendiente tuyo, jefe."
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
        txt = f"Llevas {v24} visitas en 24 horas y {v7} en la semana."
        if v24 == 0:
            txt += " Cero. Ni tu jefa entró. A compartir, huevón."
        pag = [g["dimensions"]["requestPath"] for g in hoy["pag"] if g["dimensions"]["requestPath"]]
        if pag:
            nombre = pag[0].strip("/").replace("-", " ") or "la portada"
            txt += f" La página más vista fue {nombre}."
        refs = [g["dimensions"]["refererHost"] for g in hoy["ref"] if g["dimensions"]["refererHost"] and "quincy" not in g["dimensions"]["refererHost"]]
        if refs:
            txt += " Llegan sobre todo de " + ", ".join(r.replace("www.", "").replace("l.instagram.com", "Instagram").replace(".com", "") for r in refs[:2]) + "."
        return txt
    except Exception as e:  # nunca tumbar el resumen por las visitas
        print(f"Cloudflare: {e}", file=sys.stderr)
        return "Las visitas no las pude leer esta vez; Cloudflare anda de payaso."


def sitio():
    malas = []
    for p in ["", "aguinaldo/", "app.html"]:
        try:
            st, _ = get(SITE + p, timeout=15)
            if st != 200:
                malas.append(p or "portada")
        except Exception:
            malas.append(p or "portada")
    if not malas:
        return ""
    return "Aguas: no abre " + ", ".join(m.strip("/").replace(".html", "") for m in malas) + ". Los agentes ya deberían estar corriendo."


def cuentas():
    hoy = NOW.date()
    out = []
    lanz = dt.date(2026, 11, 2)
    if hoy < lanz:
        d = (lanz - hoy).days
        out.append("Mañana es el lanzamiento, jefe. Ya ni modo de echarse para atrás." if d == 1 else f"Faltan {d} días para el lanzamiento.")
    elif hoy == lanz:
        out.append("Hoy es el lanzamiento. Publica el reel y manda los WhatsApp, que no se publican con la mente.")
    ag = dt.date(hoy.year, 12, 19)
    if dt.date(hoy.year, 11, 1) <= hoy <= ag:
        out.append(f"Y {(ag - hoy).days} para el aguinaldo: temporada alta.")
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


def pase_de_lista(ents):
    anda = en_que_anda()
    lineas = ["Ya los puse a chambear. Va el pase de lista."]
    for nombre, alias, apodo in EQUIPO:
        mias = [e for e in ents if e["agente"].startswith(nombre) and "Hice" in e]
        partes = [f"{alias[0].upper() + alias[1:]}, {apodo}."]
        if mias:
            ult = mias[0]
            cuando = "hoy" if ult["fecha"] == NOW.date().isoformat() else ("ayer" if ult["fecha"] == (NOW.date() - dt.timedelta(days=1)).isoformat() else "la última vez")
            partes.append(f"{cuando.capitalize()}: {frase(ult['Hice'], 75)}")
        else:
            partes.append("No ha reportado nada. Seguro anda en junta.")
        if anda.get(nombre):
            partes.append(f"Ahorita: {frase(anda[nombre], 65)}")
        prox = cuando_toca(alias if alias != "el de la lana" else "el de la lana")
        if prox:
            partes.append(f"Vuelve {prox}.")
        lineas.append(" ".join(partes))
    return lineas


def proximo():
    for minutos in range(1, 60 * 24 * 32):
        t = NOW + dt.timedelta(minutes=minutos)
        for nombre, cuando, hh, mm in AGENDA:
            ok = (t.weekday() in cuando.get("dow", [])) or (t.day in cuando.get("dom", []))
            if ok and t.hour == hh and t.minute == mm:
                dia = "hoy" if t.date() == NOW.date() else ("mañana" if t.date() == NOW.date() + dt.timedelta(days=1) else f"el {DIAS[t.weekday()]}")
                h12 = (hh - 1) % 12 + 1
                parte = "de la noche" if hh >= 19 else ("de la tarde" if hh >= 12 else "de la mañana")
                return f"Al rato le toca {nombre.replace('el ', 'al ', 1)}, {dia} a las {h12}:{mm:02d}. Andan jalando, jefe."
    return ""


def resumen():
    hora = NOW.hour
    saludo = "Buenos días" if hora < 12 else ("Buenas tardes" if hora < 19 else "Buenas noches")
    partes = [f"{saludo}, jefe.", cuentas(), visitas(), sitio()]

    ents = entradas()
    partes += pase_de_lista(ents)

    dueño = next((e["Para el dueño"] for e in ents if e.get("Para el dueño") and e["agente"].startswith("Director")), "")
    if dueño:
        partes.append("A ti te toca: " + frase(dueño, 110))
    partes.append(CHISTES[(NOW.timetuple().tm_yday * 12 + NOW.hour // 2) % len(CHISTES)])
    return "\n".join(p for p in partes if p)


def main():
    texto = resumen()
    if "--stdout" in sys.argv:
        print(texto)
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(texto + "\n")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
