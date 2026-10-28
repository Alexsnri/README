"""Genera quincy/marketing/social/schedule.json: el calendario que publica el robot de Instagram.

Las imágenes y videos se sirven desde GitHub Pages (Instagram los descarga de una URL pública).
Uso: python3 quincy/scripts/build_social.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://alexsnri.github.io/README/quincy/"
MEDIA = SITE + "marketing/"
FEED_TIME, STORY_TIME, REEL_TIME = "13:30", "13:35", "20:00"  # hora de la Ciudad de México

TAGS = "#aguinaldo #quincena #finanzaspersonales #derechoslaborales #mexico"


def feed_captions():
    md = open(os.path.join(ROOT, "marketing", "posts.md"), encoding="utf-8").read()
    sec = md.split("## Feed")[1].split("## Historias")[0]
    out = {}
    for part in re.split(r"^### ", sec, flags=re.M)[1:]:
        head, body = part.split("\n", 1)
        f = re.search(r"`([^`]+)\.png`", head).group(1)
        lines = []
        for line in body.split("\n"):
            if line.startswith(">"):
                lines.append(line[1:].lstrip())
            elif lines:
                break
        out[f] = "\n".join(lines).strip()
    return out


CAP = feed_captions()

REELS = {
    "00-conoce-quincy": "Te presento Quincy 👋 La app que te dice lo que te toca, cuándo te toca y cuánto te queda.\nTu límite diario, tu aguinaldo, tus vacaciones y tu tanda. Gratis, sin registro y sin bancos.\nLink en bio.\n\n#quincy #finanzaspersonales #aguinaldo #quincena #mexico",
    "01-aguinaldo-ley": "Tu aguinaldo no es un regalo: es ley 💸 Mínimo 15 días de salario y te lo tienen que pagar antes del 20 de diciembre.\nMándaselo a quien todavía no sabe cuánto le toca 👇 Calcula el tuyo gratis: link en bio.\n\n#aguinaldo #aguinaldo2026 #finanzaspersonales #derechoslaborales #mexico",
    "02-renuncias": "¿Vas a renunciar? No pierdes tu aguinaldo. Tu finiquito incluye días no pagados, aguinaldo proporcional, vacaciones y prima vacacional.\nGuárdalo por si acaso y calcula el tuyo: link en bio.\n\n#finiquito #renuncia #derechoslaborales #trabajo #mexico",
    "03-aguinaldo-isr": "¿Por qué tu aguinaldo llega incompleto? Los primeros $3,519.30 no pagan ISR; solo lo que pasa de ahí.\nGuárdalo para diciembre 📌 Calcula el tuyo: link en bio.\n\n#aguinaldo #ISR #SAT #finanzaspersonales #mexico",
    "04-tanda-numero": "¿Pides el número 1 o el 10 de la tanda? 🤔 El 1 recibe un préstamo sin intereses; el 10 presta su dinero gratis.\nEtiqueta a quien organiza tu tanda 👇 Calcula la tuya: link en bio.\n\n#tanda #ahorro #CETES #finanzaspersonales #mexico",
    "05-te-despiden": "¿Te despidieron sin causa? No firmes nada todavía. Te tocan 3 meses de salario, 12 días por año y tu finiquito. Tienes 2 meses para reclamar y PROFEDET te asesora gratis.\nMándaselo a quien lo necesite. Link en bio.\n\n#liquidacion #despido #PROFEDET #derechoslaborales #mexico",
    "06-ruleta-tanda": "Se acabaron los pleitos por el número de la tanda 🎡 Gira la ruleta, sortea los turnos y manda el calendario al grupo.\nOrganiza la tuya gratis: link en bio.\n\n#tanda #ahorro #whatsapp #familia #mexico",
    "07-hoy-puedes-gastar": "La regla que me salvó la quincena: lo que te llega, menos pagos fijos y ahorro, entre los días que faltan. Ese es tu número de hoy.\n¿Cuál es el tuyo? Calcúlalo gratis: link en bio.\n\n#quincena #presupuesto #ahorro #finanzaspersonales #mexico",
    "08-faltan-18-dias": "Faltan 18 días para el límite del aguinaldo (19 de diciembre) ⏳ Antes de gastarlo: paga lo que te cobra intereses, aparta para enero y págate primero.\nCompártelo con tu equipo. Link en bio.\n\n#aguinaldo #aguinaldo2026 #ahorro #mexico",
}

HOOKS = {
    "00-conoce-quincy": "La app que te dice lo que te toca",
    "01-aguinaldo-ley": "Tu aguinaldo no es un regalo",
    "02-renuncias": "¿Renuncias? No pierdes tu aguinaldo",
    "03-aguinaldo-isr": "¿Por qué tu aguinaldo llega incompleto?",
    "04-tanda-numero": "¿Pides el número 1 o el 10?",
    "05-te-despiden": "¿Te despidieron? No firmes nada todavía",
    "06-ruleta-tanda": "Se acabaron los pleitos por el número",
    "07-hoy-puedes-gastar": "La regla que me salvó la quincena",
    "08-faltan-18-dias": "Faltan 18 días para tu aguinaldo",
}

CAROUSELS = {
    "c1-aguinaldo": ("5 cosas de tu aguinaldo", "5 cosas que tienes que saber de tu aguinaldo 💸 Desliza y guárdalo para diciembre.\n¿Ya sabes cuánto te toca? Calcúlalo gratis: link en bio.\n\n#aguinaldo #aguinaldo2026 #finanzaspersonales #derechoslaborales #mexico"),
    "c2-tanda": ("¿Qué número de la tanda te conviene?", "¿Qué número de la tanda te conviene? Hicimos la cuenta 👉 desliza.\nArma la tuya con ruleta y calendario, gratis: link en bio.\n\n#tanda #ahorro #CETES #finanzaspersonales #mexico"),
    "c3-finiquito-liquidacion": ("¿Finiquito o liquidación?", "¿Finiquito o liquidación? No es lo mismo. Desliza y guárdalo por si acaso 📌\nCalcula el tuyo gratis: link en bio.\n\n#finiquito #liquidacion #derechoslaborales #PROFEDET #mexico"),
}

REPEAT = {
    ("2026-11-23", "01-aguinaldo-tabla"): "Recordatorio: el aguinaldo se paga a más tardar el 19 de diciembre y son mínimo 15 días de salario.\nSi entraste este año, te toca la parte proporcional. Calcula el tuyo, link en bio 💸\n\n" + TAGS,
    ("2026-11-27", "05-aguinaldo-isr"): "Antes de gastar el aguinaldo en ofertas: los primeros $3,519.30 no pagan ISR, lo demás sí. Haz tus cuentas con lo que de verdad te va a llegar.\nLink en bio.\n\n#aguinaldo #ISR #blackfriday #finanzaspersonales #mexico",
    ("2026-12-15", "07-hoy-puedes-gastar"): "Cayó la quincena y ya casi el aguinaldo 🎄 Antes de que desaparezcan: Quincy te dice cuánto puedes gastar al día para llegar a la siguiente.\nLink en bio.\n\n#quincena #aguinaldo #presupuesto #mexico",
}

# fecha, tipo, pieza
PLAN = [
    ("2026-11-02", "feed", "01-aguinaldo-tabla"), ("2026-11-02", "story", "01-aguinaldo"), ("2026-11-02", "reel", "01-aguinaldo-ley"),
    ("2026-11-03", "story", "05-mi-futuro"),
    ("2026-11-04", "feed", "02-vacaciones-dignas"),
    ("2026-11-05", "story", "02-tanda"),
    ("2026-11-06", "feed", "03-si-renuncias"), ("2026-11-06", "reel", "02-renuncias"),
    ("2026-11-07", "story", "04-dias-en-verde"),
    ("2026-11-09", "carousel", "c3-finiquito-liquidacion"), ("2026-11-09", "story", "01-aguinaldo"),
    ("2026-11-11", "feed", "05-aguinaldo-isr"), ("2026-11-11", "story", "05-mi-futuro"), ("2026-11-11", "reel", "03-aguinaldo-isr"),
    ("2026-11-12", "story", "02-tanda"),
    ("2026-11-13", "carousel", "c2-tanda"), ("2026-11-13", "reel", "04-tanda-numero"),
    ("2026-11-14", "story", "04-dias-en-verde"),
    ("2026-11-15", "feed", "07-hoy-puedes-gastar"), ("2026-11-15", "story", "03-ticket"),
    ("2026-11-16", "story", "01-aguinaldo"),
    ("2026-11-17", "feed", "08-ptu-tope"),
    ("2026-11-18", "story", "05-mi-futuro"),
    ("2026-11-19", "feed", "09-salario-minimo"), ("2026-11-19", "reel", "05-te-despiden"),
    ("2026-11-20", "story", "02-tanda"),
    ("2026-11-21", "feed", "10-tanda-ruleta"), ("2026-11-21", "reel", "06-ruleta-tanda"),
    ("2026-11-22", "story", "04-dias-en-verde"),
    ("2026-11-23", "carousel", "c1-aguinaldo"), ("2026-11-23", "story", "01-aguinaldo"),
    ("2026-11-25", "story", "05-mi-futuro"), ("2026-11-25", "reel", "07-hoy-puedes-gastar"),
    ("2026-11-26", "story", "02-tanda"),
    ("2026-11-27", "feed", "05-aguinaldo-isr"),
    ("2026-11-28", "story", "04-dias-en-verde"),
    ("2026-11-30", "feed", "11-ticket"), ("2026-11-30", "story", "03-ticket"),
    ("2026-12-01", "story", "01-aguinaldo"), ("2026-12-01", "reel", "08-faltan-18-dias"),
    ("2026-12-07", "story", "01-aguinaldo"),
    ("2026-12-15", "feed", "07-hoy-puedes-gastar"), ("2026-12-15", "story", "03-ticket"),
    ("2026-12-18", "story", "01-aguinaldo"),
]

# Se publica a mano desde GitHub Actions al terminar la configuración (y sirve de prueba).
MANUAL = [("fijado", "reel", "00-conoce-quincy")]


def item(date, kind, piece):
    if kind == "feed":
        url, caption, time = MEDIA + f"ig/{piece}.jpg", REPEAT.get((date, piece), CAP[piece]), FEED_TIME
    elif kind == "story":
        url, caption, time = MEDIA + f"ig/story-{piece}.jpg", "", STORY_TIME
    elif kind == "carousel":
        folder = os.path.join(ROOT, "marketing", "carruseles", piece)
        urls = [MEDIA + f"carruseles/{piece}/{f}" for f in sorted(os.listdir(folder)) if f.endswith(".jpg")]
        for u in urls:
            assert os.path.exists(u.replace(MEDIA, os.path.join(ROOT, "marketing") + "/")), u
        return {"id": f"{date}-{kind}-{piece}", "date": date, "time": FEED_TIME, "type": kind, "media": urls[0], "children": urls,
                "title": CAROUSELS[piece][0], "caption": CAROUSELS[piece][1]}
    else:
        url, caption, time = MEDIA + f"video/animados/reel-{piece}.mp4", REELS[piece], REEL_TIME
    for p in (url.replace(MEDIA, os.path.join(ROOT, "marketing") + "/"),):
        assert os.path.exists(p), p
    return {"id": f"{date}-{kind}-{piece}", "date": date, "time": time, "type": kind, "media": url, "caption": caption}


DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def fecha(iso):
    import datetime as dt
    d = dt.date.fromisoformat(iso)
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month]}"


def write_reels_doc(items):
    """Escribe marketing/social/reels.json y la sección de reels de posts.md."""
    reels = []
    for it in items:
        if it["type"] != "reel":
            continue
        rid = it["id"].split("-reel-")[1]
        reels.append({"id": rid, "file": f"video/animados/reel-{rid}.mp4", "date": it["date"], "when": "Publícalo hoy y fíjalo" if it["date"] == "fijado" else fecha(it["date"]),
                      "hook": HOOKS[rid], "caption": it["caption"]})
    with open(os.path.join(ROOT, "marketing", "social", "reels.json"), "w", encoding="utf-8") as f:
        json.dump(reels, f, ensure_ascii=False, indent=1)
    md_path = os.path.join(ROOT, "marketing", "posts.md")
    md = open(md_path, encoding="utf-8").read()
    body = ["<!-- reels:start (generado por scripts/build_social.py) -->", ""]
    for i, r in enumerate(reels, 1):
        body += [f"### R{i} · {r['hook']} · `{r['file']}` · {r['when']}", ""]
        body += ["> " + l if l else ">" for l in r["caption"].split("\n")]
        body += [""]
    body += ["<!-- reels:end -->"]
    md = re.sub(r"<!-- reels:start.*?<!-- reels:end -->", "\n".join(body), md, flags=re.S)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)


def main():
    items = [item(*x) for x in PLAN] + [item(*x) for x in MANUAL]
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids)), "ids repetidos"
    assert all(len(i["caption"]) <= 2200 for i in items)
    out = os.path.join(ROOT, "marketing", "social")
    os.makedirs(out, exist_ok=True)
    data = {"timezone": "America/Mexico_City", "items": items}
    with open(os.path.join(out, "schedule.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    write_reels_doc(items)
    counts = {k: sum(1 for i in items if i["type"] == k) for k in ("feed", "carousel", "story", "reel")}
    print("schedule.json:", len(items), "piezas", counts)


if __name__ == "__main__":
    main()
