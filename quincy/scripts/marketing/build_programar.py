"""Genera marketing/programar.html (lista para programar en Instagram desde el celular) y programar-instagram.zip
a partir de marketing/social/schedule.json y reels.json.  Uso:  python3 quincy/scripts/marketing/build_programar.py
"""
import json, os, sys, zipfile, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); M = os.path.normpath(os.path.join(HERE, '..', '..', 'marketing')); SITE = 'https://quincy-mx.github.io/'
DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]; MES = dict(enumerate(["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"], 1))
TITLES = {"01-aguinaldo-tabla": "Aguinaldo 2026", "02-vacaciones-dignas": "Vacaciones dignas", "03-si-renuncias": "Si renuncias", "04-si-te-despiden": "Si te despiden",
  "05-aguinaldo-isr": "Aguinaldo e ISR", "06-tanda-numero": "¿Qué número te conviene?", "07-hoy-puedes-gastar": "Hoy puedes gastar", "08-ptu-tope": "PTU con tope",
  "09-salario-minimo": "Salario mínimo", "10-tanda-ruleta": "Ruleta de la tanda", "11-ticket": "Ticket de la quincena", "12-quincy": "Qué es Quincy", "13-aguinaldo-a-rendir": "Aguinaldo a rendir"}
sched = json.load(open(M + '/social/schedule.json'))['items']
reels = {r['id']: r for r in json.load(open(M + '/social/reels.json'))}
items, seen = [], set()
order = sorted([i for i in sched if i['type'] != 'story'], key=lambda i: ('0' if i['date'] == 'fijado' else i['date'], i['time']))
for it in order:
    piece = it['id'].split('-' + it['type'] + '-')[-1]
    now = it['date'] == 'fijado'
    if now: when = ''
    else:
        d = dt.date.fromisoformat(it['date']); when = f"{DIAS[d.weekday()]} {d.day} {MES[d.month]}"
    hh, mm = map(int, it['time'].split(':')); time = f"{(hh - 1) % 12 + 1}:{mm:02d} {'p. m.' if hh >= 12 else 'a. m.'}"
    rel = it['media'].replace(SITE + 'marketing/', '')
    thumb = {'feed': f"preview/{piece}.jpg", 'reel': f"preview/reel-{piece}.jpg", 'carousel': f"preview/carr-{piece}.jpg"}[it['type']]
    items.append({"id": it['id'], "type": {'feed': 'post', 'reel': 'reel', 'carousel': 'carousel'}[it['type']], "now": now, "when": when, "time": time,
                  "title": it.get('title') or TITLES.get(piece) or reels.get(piece, {}).get('hook', piece), "caption": it['caption'], "media": it['media'], "rel": rel, "thumb": thumb,
                  "children": it.get('children', []), "repeat": it['type'] == 'feed' and piece in seen})
    if it['type'] == 'feed': seen.add(piece)
data = {"items": items, "zip": SITE + 'marketing/programar-instagram.zip', "kit": SITE + 'marketing/kit.html', "page": SITE + 'marketing/programar.html'}
page = open(os.path.join(HERE, 'programar-tpl.html')).read().replace('/*DATA*/null', json.dumps(data, ensure_ascii=False))
open(M + '/programar.html', 'w').write('<!doctype html>\n<html lang="es-MX">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="robots" content="noindex">\n' + page.replace('<!--/head-->', '</head>\n<body>') + '\n</body>\n</html>\n')
# ZIP: files renamed in order, plus all captions in one text file
zp = M + '/programar-instagram.zip'
if os.path.exists(zp): os.remove(zp)
txt = []
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_STORED) as z:
    for n, it in enumerate(items, 1):
        tag = 'hoy-fijar' if it['now'] else it['when'].replace(' ', '-').replace('é', 'e').replace('á', 'a')
        if it['type'] == 'carousel':
            name = f"{n:02d}_{tag}_carrusel"
            for j, u in enumerate(it['children'], 1):
                z.write(os.path.join(M, u.replace(SITE + 'marketing/', '')), f'quincy-instagram/{name}/{j}.jpg')
        else:
            ext = os.path.splitext(it['rel'])[1]
            name = f"{n:02d}_{tag}_{'reel' if it['type'] == 'reel' else 'post'}{ext}"
            z.write(os.path.join(M, it['rel']), 'quincy-instagram/' + name)
        txt.append(f"{name}\n{'Publícalo hoy y fíjalo' if it['now'] else it['when'] + ' · ' + it['time']}\n\n{it['caption']}\n\n" + '-' * 40)
    z.writestr('quincy-instagram/00_textos.txt', '\n\n'.join(txt))
print(len(items), 'items;', os.path.getsize(zp) // 1024 // 1024, 'MB zip')

# Recordatorios de TikTok (.ics): un evento por reel con fecha, 10 minutos antes de las 8 p. m. (hora de la Ciudad de México).
# El UID conserva el dominio viejo para que, al volver a importarlo, el calendario actualice los eventos en lugar de duplicarlos.
def fold(line):
    b, out = line.encode('utf-8'), []
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80: cut -= 1
        out.append(b[:cut].decode('utf-8')); b = b[cut:]
    out.append(b.decode('utf-8'))
    return '\r\n '.join(out)
stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
ev = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Quincy//Recordatorios TikTok//ES", "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:Quincy · TikTok"]
for r in json.load(open(M + '/social/reels.json')):
    if r['date'] == 'fijado': continue
    start = dt.datetime.fromisoformat(r['date'] + 'T20:00').replace(tzinfo=dt.timezone(dt.timedelta(hours=-6))).astimezone(dt.timezone.utc)
    f = lambda d: d.strftime('%Y%m%dT%H%M%SZ')
    ev += [f"BEGIN:VEVENT", f"UID:quincy-tiktok-{r['id']}@alexsnri.github.io", f"DTSTAMP:{stamp}", f"DTSTART:{f(start)}", f"DTEND:{f(start + dt.timedelta(minutes=15))}",
           f"SUMMARY:Subir a TikTok: {r['hook']}",
           f"DESCRIPTION:1) Abre {SITE}marketing/programar.html en Safari y toca Guardar video en el reel \"{r['hook']}\".\\n2) TikTok: + → sube el video → pega el texto (botón Copiar texto) → Publicar.\\nTambién puedes subirlo a YouTube Shorts.",
           f"URL:{SITE}marketing/programar.html", "BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:Subir reel de Quincy a TikTok", "TRIGGER:-PT10M", "END:VALARM", "END:VEVENT"]
ev.append("END:VCALENDAR")
open(M + '/recordatorios-tiktok.ics', 'w', encoding='utf-8', newline='').write('\r\n'.join(fold(l) for l in ev) + '\r\n')
print(sum(1 for l in ev if l == 'BEGIN:VEVENT'), 'recordatorios de TikTok')
