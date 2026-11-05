"""Configuration: config.yaml + environment variables (.env). Includes the DEMO-ONLY guard."""
import os
import secrets

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_API = "https://demo-api-capital.backend-capital.com/api/v1"
STREAM_URL = "wss://api-streaming-capital.backend-capital.com/connect"
SECRET_KEYS = ("CAPITAL_API_KEY", "CAPITAL_IDENTIFIER", "CAPITAL_API_PASSWORD", "TELEGRAM_TOKEN", "DASHBOARD_PASSWORD")


class NotDemoError(SystemExit):
    pass


def load_env(path=None):
    """Reads .env (KEY=value) without overwriting variables that already exist in the environment."""
    path = path or os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def api_url():
    """The only allowed URL is the DEMO one. If someone configures another (e.g. live), the bot refuses to start."""
    url = os.environ.get("CAPITAL_API_URL", DEMO_API).rstrip("/")
    if not url.endswith("/api/v1"):
        url += "/api/v1"
    if url != DEMO_API:
        raise NotDemoError(
            f"CAPITAL_API_URL={url!r} no es el entorno DEMO. Este bot solo opera en {DEMO_API} y se niega a arrancar.")
    if os.environ.get("CAPITAL_ENV", "demo").lower() != "demo":
        raise NotDemoError("CAPITAL_ENV debe ser 'demo'. Este bot se niega a operar una cuenta real.")
    return url


def load(path=None):
    load_env()
    path = path or os.environ.get("BOT_CONFIG", os.path.join(ROOT, "config.yaml"))
    cfg = yaml.safe_load(open(path, encoding="utf-8"))
    cfg["api_url"] = api_url()
    cfg["data_dir"] = os.environ.get("DATA_DIR", os.path.join(ROOT, "state"))
    os.makedirs(cfg["data_dir"], exist_ok=True)
    cfg["port"] = int(os.environ.get("PORT", "8080"))
    cfg["sim"] = os.environ.get("BOT_SIM", "0") == "1"          # replay of history (tests and preview)
    cfg["has_credentials"] = all(os.environ.get(k) for k in SECRET_KEYS[:3])
    return cfg


def profile(cfg, name=None):
    return cfg["perfiles"][name or cfg["perfil"]]


def dashboard_password(store):
    """DASHBOARD_PASSWORD from the environment or, if missing, one generated and saved the first time."""
    pw = os.environ.get("DASHBOARD_PASSWORD")
    if pw:
        return pw
    pw = store.kv_get("dashboard_password")
    if not pw:
        pw = secrets.token_urlsafe(9)
        store.kv_set("dashboard_password", pw)
    return pw


def redact(text: str) -> str:
    """Removes any secret value that might slip into a message or log."""
    for k in SECRET_KEYS:
        v = os.environ.get(k)
        if v and len(v) >= 4:
            text = text.replace(v, "***")
    return text
