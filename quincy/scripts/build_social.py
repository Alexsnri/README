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
    "01-app-aguinaldo": "POV: encontraste la app que te dice cuánto te toca de aguinaldo, cuánto puedes gastar hoy y qué número de la tanda te conviene 👀\nGratis y sin registro. Link en bio.\n\n" + TAGS,
    "02-si-renuncias": "¿Vas a renunciar? Antes de firmar, calcula tu finiquito: días trabajados, aguinaldo proporcional, vacaciones y prima vacacional.\nGratis en Quincy, link en bio.\n\n#finiquito #renuncia #derechoslaborales #trabajo #mexico",
    "03-calcula-aguinaldo": "¿Cuánto te toca de aguinaldo? Pones tu sueldo y tu fecha de ingreso y listo. Te lo tienen que pagar antes del 20 de diciembre.\nCalcúlalo gratis, link en bio.\n\n#aguinaldo #aguinaldo2026 #finanzaspersonales #mexico",
    "04-numero-tanda": "¿Pides el número 1 o el último de la tanda? 🤔\nEl 1 recibe un préstamo sin intereses; el último ahorra sin rendimiento. Quincy te dice cuánto gana o pierde cada número frente a CETES.\nLink en bio.\n\n#tanda #ahorro #CETES #finanzaspersonales #mexico",
    "05-si-te-despiden": "Si te despiden sin causa: 3 meses de salario integrado + 12 días por año de prima de antigüedad + tu finiquito. Tienes 2 meses para reclamar y PROFEDET te asesora gratis.\nCalcula la tuya, link en bio.\n\n#liquidacion #despido #PROFEDET #derechoslaborales #mexico",
    "06-ruleta-tanda": "Se acabaron los pleitos por el número de la tanda 🎡 Gira la ruleta, sortea los turnos y manda el calendario al grupo de WhatsApp.\nGratis, link en bio.\n\n#tanda #ahorro #whatsapp #familia #mexico",
    "07-hoy-puedes-gastar": "La app que me dice cuánto puedo gastar hoy para llegar a la quincena. Si hoy gasto menos, mañana tengo más.\nSin conectar tu banco. Link en bio.\n\n#quincena #presupuesto #ahorro #finanzaspersonales #mexico",
    "08-faltan-dias-aguinaldo": "Faltan 18 días para el límite del aguinaldo (19 de diciembre). ¿Ya sabes cuánto te toca? Calcúlalo en 10 segundos, link en bio.\n\n#aguinaldo #aguinaldo2026 #quincena #mexico",
}

HOOKS = {
    "01-app-aguinaldo": "POV: encontraste la app que te dice cuánto te toca de aguinaldo",
    "02-si-renuncias": "¿Vas a renunciar? Esto te tienen que pagar",
    "03-calcula-aguinaldo": "¿Cuánto te toca de aguinaldo? Te lo digo en 10 segundos",
    "04-numero-tanda": "El número 1 de la tanda gana dinero. El último pierde.",
    "05-si-te-despiden": "Si te despiden, esto es lo mínimo que te tienen que dar",
    "06-ruleta-tanda": "Se acabaron los pleitos por el número de la tanda",
    "07-hoy-puedes-gastar": "La app que me dice cuánto puedo gastar hoy",
    "08-faltan-dias-aguinaldo": "Faltan 18 días para el aguinaldo. ¿Ya sabes cuánto te toca?",
}

REPEAT = {
    ("2026-11-23", "01-aguinaldo-tabla"): "Recordatorio: el aguinaldo se paga a más tardar el 19 de diciembre y son mínimo 15 días de salario.\nSi entraste este año, te toca la parte proporcional. Calcula el tuyo, link en bio 💸\n\n" + TAGS,
    ("2026-11-27", "05-aguinaldo-isr"): "Antes de gastar el aguinaldo en ofertas: los primeros $3,519.30 no pagan ISR, lo demás sí. Haz tus cuentas con lo que de verdad te va a llegar.\nLink en bio.\n\n#aguinaldo #ISR #blackfriday #finanzaspersonales #mexico",
    ("2026-12-15", "07-hoy-puedes-gastar"): "Cayó la quincena y ya casi el aguinaldo 🎄 Antes de que desaparezcan: Quincy te dice cuánto puedes gastar al día para llegar a la siguiente.\nLink en bio.\n\n#quincena #aguinaldo #presupuesto #mexico",
}

# fecha, tipo, pieza
PLAN = [
    ("2026-11-02", "feed", "01-aguinaldo-tabla"), ("2026-11-02", "story", "01-aguinaldo"), ("2026-11-02", "reel", "01-app-aguinaldo"),
    ("2026-11-03", "story", "05-mi-futuro"),
    ("2026-11-04", "feed", "02-vacaciones-dignas"),
    ("2026-11-05", "story", "02-tanda"),
    ("2026-11-06", "feed", "03-si-renuncias"), ("2026-11-06", "reel", "02-si-renuncias"),
    ("2026-11-07", "story", "04-dias-en-verde"),
    ("2026-11-09", "feed", "04-si-te-despiden"), ("2026-11-09", "story", "01-aguinaldo"),
    ("2026-11-11", "feed", "05-aguinaldo-isr"), ("2026-11-11", "story", "05-mi-futuro"), ("2026-11-11", "reel", "03-calcula-aguinaldo"),
    ("2026-11-12", "story", "02-tanda"),
    ("2026-11-13", "feed", "06-tanda-numero"), ("2026-11-13", "reel", "04-numero-tanda"),
    ("2026-11-14", "story", "04-dias-en-verde"),
    ("2026-11-15", "feed", "07-hoy-puedes-gastar"), ("2026-11-15", "story", "03-ticket"),
    ("2026-11-16", "story", "01-aguinaldo"),
    ("2026-11-17", "feed", "08-ptu-tope"),
    ("2026-11-18", "story", "05-mi-futuro"),
    ("2026-11-19", "feed", "09-salario-minimo"), ("2026-11-19", "reel", "05-si-te-despiden"),
    ("2026-11-20", "story", "02-tanda"),
    ("2026-11-21", "feed", "10-tanda-ruleta"), ("2026-11-21", "reel", "06-ruleta-tanda"),
    ("2026-11-22", "story", "04-dias-en-verde"),
    ("2026-11-23", "feed", "01-aguinaldo-tabla"), ("2026-11-23", "story", "01-aguinaldo"),
    ("2026-11-25", "story", "05-mi-futuro"), ("2026-11-25", "reel", "07-hoy-puedes-gastar"),
    ("2026-11-26", "story", "02-tanda"),
    ("2026-11-27", "feed", "05-aguinaldo-isr"),
    ("2026-11-28", "story", "04-dias-en-verde"),
    ("2026-11-30", "feed", "11-ticket"), ("2026-11-30", "story", "03-ticket"),
    ("2026-12-01", "story", "01-aguinaldo"), ("2026-12-01", "reel", "08-faltan-dias-aguinaldo"),
    ("2026-12-07", "story", "01-aguinaldo"),
    ("2026-12-15", "feed", "07-hoy-puedes-gastar"), ("2026-12-15", "story", "03-ticket"),
    ("2026-12-18", "story", "01-aguinaldo"),
]

# Se publica a mano desde GitHub Actions al terminar la configuración (y sirve de prueba).
MANUAL = [("fijado", "feed", "12-quincy")]


def item(date, kind, piece):
    if kind == "feed":
        url, caption, time = MEDIA + f"ig/{piece}.jpg", REPEAT.get((date, piece), CAP[piece]), FEED_TIME
    elif kind == "story":
        url, caption, time = MEDIA + f"ig/story-{piece}.jpg", "", STORY_TIME
    else:
        url, caption, time = MEDIA + f"video/reel-{piece}.mp4", REELS[piece], REEL_TIME
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
        reels.append({"id": rid, "file": f"video/reel-{rid}.mp4", "date": it["date"], "when": fecha(it["date"]),
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
    counts = {k: sum(1 for i in items if i["type"] == k) for k in ("feed", "story", "reel")}
    print("schedule.json:", len(items), "piezas", counts)


if __name__ == "__main__":
    main()
