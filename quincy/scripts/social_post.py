"""Robot de Instagram de Quincy: publica posts, historias y reels en su fecha.

Usa la API de Instagram con inicio de sesión de Instagram (graph.instagram.com) y un token de tu
propia cuenta profesional. Solo usa la biblioteca estándar de Python.

Acciones:
  probar                Revisa el token, la cuenta, el límite de publicaciones y que cada archivo exista. No publica.
  pendientes            Publica lo que ya tocaba (hasta 30 horas de atraso) y no se ha publicado.
  ahora --pieza ID      Publica una pieza ya, sin importar la fecha (por ejemplo: fijado-reel-00-conoce-quincy).

Variables de entorno:
  INSTAGRAM_TOKEN   token de acceso (obligatorio para publicar)
  GRAPH_BASE        por defecto https://graph.instagram.com/v23.0 (se cambia en pruebas)
  STATE_FILE        por defecto .github/quincy-social/posted.json
  NOW               fecha y hora ISO para pruebas (por ejemplo 2026-11-02T13:40)
  MEDIA_CHECK_BASE  solo pruebas: servidor donde revisar que existan los archivos
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
SCHEDULE = os.path.join(ROOT, "marketing", "social", "schedule.json")
STATE = os.environ.get("STATE_FILE", os.path.join(REPO, ".github", "quincy-social", "posted.json"))
BASE = os.environ.get("GRAPH_BASE", "https://graph.instagram.com/v23.0").rstrip("/")
TOKEN = os.environ.get("INSTAGRAM_TOKEN", "").strip()
CATCH_UP = dt.timedelta(hours=30)
SUMMARY = os.environ.get("GITHUB_STEP_SUMMARY")
POLL_SECONDS = float(os.environ.get("POLL_SECONDS", "10"))


class ApiError(Exception):
    pass


def log(msg):
    print(msg, flush=True)


def summary(md):
    if SUMMARY:
        with open(SUMMARY, "a", encoding="utf-8") as f:
            f.write(md + "\n")


def api(method, path, **params):
    params["access_token"] = TOKEN
    url = f"{BASE}/{path.lstrip('/')}"
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err = json.loads(body).get("error", {})
            msg = f"{err.get('message', body)} (código {err.get('code')}, {err.get('error_subcode', '')})"
        except ValueError:
            msg = body[:300]
        raise ApiError(f"{method} {path}: HTTP {e.code}: {msg}") from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        raise ApiError(f"{method} {path}: sin conexión con Instagram ({e}). Se reintentará en la siguiente corrida.") from None


def media_ok(url):
    alt = os.environ.get("MEDIA_CHECK_BASE")  # solo pruebas: revisa los archivos en otro servidor
    if alt:
        url = url.replace("https://alexsnri.github.io/README/quincy/", alt.rstrip("/") + "/")
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200
    except Exception:
        return False


def load_schedule():
    with open(SCHEDULE, encoding="utf-8") as f:
        data = json.load(f)
    tz = ZoneInfo(data.get("timezone", "America/Mexico_City"))
    for it in data["items"]:
        it["at"] = None
        if it["date"] != "fijado":
            h, m = map(int, it["time"].split(":"))
            y, mo, d = map(int, it["date"].split("-"))
            it["at"] = dt.datetime(y, mo, d, h, m, tzinfo=tz)
    return tz, data["items"]


def load_state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"posted": {}}


def save_state(state):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


def account():
    me = api("GET", "me", fields="user_id,username,account_type")
    uid = me.get("user_id") or me.get("id")
    if not uid:
        raise ApiError(f"No pude leer la cuenta: {me}")
    return str(uid), me.get("username", "?"), me.get("account_type", "?")


def wait_ready(container, kind):
    tries = 60 if kind == "reel" else 12
    for _ in range(tries):
        st = api("GET", container, fields="status_code,status")
        code = st.get("status_code")
        if code in (None, "FINISHED"):
            return
        if code in ("ERROR", "EXPIRED"):
            raise ApiError(f"Instagram no pudo procesar el archivo: {st.get('status') or code}")
        time.sleep(POLL_SECONDS)
    raise ApiError("Instagram tardó demasiado en procesar el archivo; se reintentará en la siguiente corrida.")


def publish(uid, it):
    if not media_ok(it["media"]):
        raise ApiError(f"El archivo no está disponible en {it['media']} (¿ya se publicó el sitio?)")
    kind = it["type"]
    if kind == "feed":
        params = {"image_url": it["media"], "caption": it["caption"]}
    elif kind == "story":
        params = {"image_url": it["media"], "media_type": "STORIES"}
    elif kind == "carousel":
        kids = []
        for u in it["children"]:
            if not media_ok(u):
                raise ApiError(f"El archivo no está disponible en {u}")
            kids.append(api("POST", f"{uid}/media", image_url=u, is_carousel_item="true")["id"])
        for k in kids:
            wait_ready(k, "feed")
        params = {"media_type": "CAROUSEL", "children": ",".join(kids), "caption": it["caption"]}
    elif kind == "reel":
        params = {"video_url": it["media"], "media_type": "REELS", "caption": it["caption"], "share_to_feed": "true", "thumb_offset": "1500"}
    else:
        raise ApiError(f"Tipo desconocido: {kind}")
    container = api("POST", f"{uid}/media", **params)["id"]
    wait_ready(container, kind)
    media_id = api("POST", f"{uid}/media_publish", creation_id=container)["id"]
    link = ""
    try:
        link = api("GET", media_id, fields="permalink").get("permalink", "")
    except ApiError:
        pass
    return media_id, link


def label(it):
    names = {"feed": "Post", "story": "Historia", "reel": "Reel", "carousel": "Carrusel"}
    return f"{names[it['type']]} {it['id']}"


def run_probar(tz, items, state):
    now = now_local(tz)
    log(f"Hora en la Ciudad de México: {now:%Y-%m-%d %H:%M}")
    missing = [u for it in items for u in it.get("children", [it["media"]]) if not media_ok(u)]
    log(f"Archivos revisados: {len(items) - len(missing)} de {len(items)} disponibles.")
    for m in missing:
        log(f"  Falta: {m}")
    pend = [it for it in items if it["at"] and it["at"] >= now - CATCH_UP and it["id"] not in state["posted"]]
    pend.sort(key=lambda i: i["at"])
    rows = "\n".join(f"| {it['at']:%a %d %b %H:%M} | {label(it)} |" for it in pend[:8])
    summary(f"### Siguientes publicaciones\n\n| Cuándo | Qué |\n|---|---|\n{rows}\n")
    if not TOKEN:
        log("No hay token: agrega el secreto INSTAGRAM_TOKEN en GitHub (Settings → Secrets and variables → Actions).")
        summary("**Falta el secreto `INSTAGRAM_TOKEN`.** Sigue la guía paso a paso.")
        return 1
    uid, user, kind = account()
    log(f"Conectado a @{user} (tipo {kind}, id {uid}).")
    try:
        lim = api("GET", f"{uid}/content_publishing_limit", fields="quota_usage,config")
        log(f"Límite de publicaciones: {json.dumps(lim.get('data', lim), ensure_ascii=False)}")
    except ApiError as e:
        log(f"No pude leer el límite de publicaciones ({e}). No es grave.")
    summary(f"**Conectado a @{user}.** {len(items) - len(missing)} de {len(items)} archivos disponibles. Todo listo.")
    return 1 if missing else 0


def now_local(tz):
    if os.environ.get("NOW"):
        return dt.datetime.fromisoformat(os.environ["NOW"]).replace(tzinfo=tz)
    return dt.datetime.now(tz)


def run_publish(tz, items, state, only=None):
    if not TOKEN:
        log("No hay token (secreto INSTAGRAM_TOKEN). No se publica nada; esto no es un error.")
        summary("Sin publicar: falta el secreto `INSTAGRAM_TOKEN`.")
        return 0
    now = now_local(tz)
    if only:
        todo = [it for it in items if it["id"] == only]
        if not todo:
            log(f"No existe la pieza {only}. Opciones: " + ", ".join(i["id"] for i in items))
            return 1
    else:
        todo = [it for it in items if it["at"] and now - CATCH_UP <= it["at"] <= now and it["id"] not in state["posted"]]
        todo.sort(key=lambda i: (i["at"], ["feed", "carousel", "story", "reel"].index(i["type"])))
        skipped = [it for it in items if it["at"] and it["at"] < now - CATCH_UP and it["id"] not in state["posted"] and it["id"] not in state.get("skipped", {})]
        for it in skipped:
            state.setdefault("skipped", {})[it["id"]] = now.isoformat(timespec="minutes")
            log(f"Se omite por atraso de más de 30 horas: {label(it)}")
    if not todo:
        log(f"Nada que publicar a las {now:%H:%M} del {now:%d/%m}.")
        save_state(state)
        return 0
    uid, user, _ = account()
    fails = 0
    for it in todo:
        try:
            media_id, link = publish(uid, it)
            state["posted"][it["id"]] = {"media_id": media_id, "at": now.isoformat(timespec="minutes"), "link": link}
            save_state(state)
            log(f"Publicado en @{user}: {label(it)} {link}")
            summary(f"- Publicado: {label(it)} {link}")
        except ApiError as e:
            fails += 1
            log(f"Error con {label(it)}: {e}")
            summary(f"- **Error** con {label(it)}: {e}")
    save_state(state)
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["probar", "pendientes", "ahora"])
    ap.add_argument("--pieza", default="fijado-reel-00-conoce-quincy")
    a = ap.parse_args()
    tz, items = load_schedule()
    state = load_state()
    try:
        if a.accion == "probar":
            return run_probar(tz, items, state)
        return run_publish(tz, items, state, only=a.pieza if a.accion == "ahora" else None)
    except ApiError as e:
        log(f"Error de Instagram: {e}")
        if "190" in str(e) or "token" in str(e).lower():
            log("El token no sirve o ya venció. Genera uno nuevo (paso 4 de la guía) y reemplaza el secreto INSTAGRAM_TOKEN.")
        summary(f"**Error de Instagram:** {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
