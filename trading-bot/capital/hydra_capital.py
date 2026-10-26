"""
Hydra para Capital.com: misma lógica que el EA de MT5 y que el backtest, pero opera por la API de
Capital.com. Está pensado para ejecutarse una vez al día (GitHub Actions, gratis): revisa cada
mercado con la última vela diaria cerrada, mueve stops, cierra y abre posiciones, aprende y guarda
su estado en la carpeta STATE_DIR.

Variables de entorno:
  CAPITAL_API_KEY, CAPITAL_IDENTIFIER, CAPITAL_API_PASSWORD   credenciales de la API (secretos)
  CAPITAL_ENV        demo (por defecto) o live
  HYDRA_MODE         conservador | normal | reto | turbo (por defecto turbo)
  HYDRA_START        capital inicial del reto (por defecto 5000). En demo ajusta el saldo la 1a vez.
  HYDRA_GOAL         meta (por defecto 1000000)
  HYDRA_DRY_RUN      1 = sólo muestra lo que haría, sin mandar órdenes
  STATE_DIR          carpeta del estado (por defecto ./state)
"""
import csv, json, math, os, sys, time
from datetime import datetime, timedelta, timezone

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "backtest"))
from backtest import indicators, s_donchian, s_tsmom, s_meanrev  # noqa: E402

# modo -> (% riesgo por trade, % riesgo abierto máx., % drawdown que pausa, apalancamiento nocional)
MODES = {"conservador": (0.5, 6, 25, 10), "normal": (1, 10, 35, 20), "reto": (3, 20, 60, 30), "turbo": (4, 25, 85, 40)}
# (nombre, epic en Capital.com, clase)
MARKETS = [
    ("EURUSD", "EURUSD", "fx"), ("GBPUSD", "GBPUSD", "fx"), ("USDJPY", "USDJPY", "fx"),
    ("AUDUSD", "AUDUSD", "fx"), ("USDCAD", "USDCAD", "fx"), ("XAUUSD", "GOLD", "metal"),
    ("XAGUSD", "SILVER", "metal"), ("USOIL", "OIL_CRUDE", "energy"), ("US500", "US500", "index"),
    ("USTEC", "US100", "index"), ("US30", "US30", "index"), ("DE30", "DE40", "index"),
    ("BTCUSD", "BTCUSD", "crypto"),
]
# código -> (función de señal, multiplicador ATR del stop inicial, multiplicador ATR del trailing)
STRATS = {"D": (s_donchian, 2.5, 2.5), "T": (s_tsmom, 3.0, 3.0), "M": (s_meanrev, 2.5, 0.0)}
LEARN_WINDOW, LEARN_MIN, DD_BRAKE = 30, 8, 0.20


def log(*a):
    print(datetime.now(timezone.utc).strftime("%H:%M:%S"), *a, flush=True)


class ApiError(Exception):
    pass


class Capital:
    def __init__(self, demo, key, ident, pwd):
        import requests
        host = "demo-api-capital" if demo else "api-capital"
        self.base = f"https://{host}.backend-capital.com/api/v1"
        self.s = requests.Session()
        self.s.headers["X-CAP-API-KEY"] = key
        r = self.s.post(self.base + "/session", json={"identifier": ident, "password": pwd, "encryptedPassword": False}, timeout=30)
        if r.status_code >= 400:
            raise ApiError(f"No pude iniciar sesión en Capital.com: {r.status_code} {r.text[:200]}")
        self.s.headers.update({"CST": r.headers["CST"], "X-SECURITY-TOKEN": r.headers["X-SECURITY-TOKEN"]})

    def req(self, method, path, **kw):
        for _ in range(4):
            r = self.s.request(method, self.base + path, timeout=30, **kw)
            if r.status_code != 429:
                break
            time.sleep(2)
        time.sleep(0.15)  # límite de 10 peticiones/seg
        if r.status_code >= 400:
            raise ApiError(f"{method} {path}: {r.status_code} {r.text[:300]}")
        return r.json() if r.text else {}

    def confirm(self, ref):
        for _ in range(5):
            try:
                c = self.req("GET", f"/confirms/{ref}")
                if c.get("dealStatus"):
                    return c
            except ApiError:
                pass
            time.sleep(1)
        return {}


# ---------------------------------------------------------------- estado
class State:
    def __init__(self, folder):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)
        self.path = os.path.join(folder, "state.json")
        self.d = json.load(open(self.path)) if os.path.exists(self.path) else {}
        self.d.setdefault("positions", {})   # dealId -> info del trade
        self.d.setdefault("learning", [])    # [brazo, R]
        self.d.setdefault("peak", 0.0)
        self.d.setdefault("history", [])     # [fecha, capital]

    def save(self):
        json.dump(self.d, open(self.path, "w"), indent=1)

    def mult(self, arm):
        rs = [r for a, r in self.d["learning"] if a == arm][-LEARN_WINDOW:]
        if len(rs) < LEARN_MIN:
            return 1.0
        return max(0.25, min(1.5, 1 + sum(rs) / len(rs)))

    def journal(self, row):
        p = os.path.join(self.folder, "journal.csv")
        new = not os.path.exists(p)
        with open(p, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["fecha", "mercado", "estrategia", "direccion", "entrada", "salida", "tamano", "resultado_usd", "R", "motivo"])
            w.writerow(row)


# ---------------------------------------------------------------- mercado
def daily_bars(api, epic, now):
    js = api.req("GET", f"/prices/{epic}", params={"resolution": "DAY", "max": 1000})
    rows = []
    for p in js.get("prices", []):
        ts = pd.Timestamp(p["snapshotTimeUTC"])
        ts = ts.tz_convert(None) if ts.tzinfo else ts
        mid = lambda k: (p[k]["bid"] + p[k]["ask"]) / 2 if p[k].get("ask") is not None else p[k]["bid"]
        rows.append((ts, mid("openPrice"), mid("highPrice"), mid("lowPrice"), mid("closePrice")))
    df = pd.DataFrame(rows, columns=["t", "o", "h", "l", "c"]).set_index("t").sort_index()
    # sólo velas cerradas: la vela en curso abrió hace menos de 20 horas
    df = df[df.index <= now - timedelta(hours=20)]
    return df


class Info:
    def __init__(self, api, epic, fx):
        m = api.req("GET", f"/markets/{epic}")
        ins, rules, snap = m["instrument"], m["dealingRules"], m["snapshot"]
        self.epic = epic
        self.status = snap.get("marketStatus")
        self.bid, self.offer = snap["bid"], snap["offer"]
        self.decimals = int(snap.get("decimalPlacesFactor", 5))
        self.min_size = rules["minDealSize"]["value"]
        self.step = (rules.get("minSizeIncrement") or {}).get("value") or self.min_size
        self.max_size = (rules.get("maxDealSize") or {}).get("value") or 1e12
        # dólares que gana/pierde 1 unidad de tamaño por cada 1.0 de movimiento del precio
        self.vpp = float(ins.get("lotSize") or 1) * fx(ins.get("currency", "USD"))

    def round_size(self, s):
        s = math.floor(s / self.step + 1e-9) * self.step
        return round(min(s, self.max_size), 8)


def fx_converter(api):
    cache = {"USD": 1.0}

    def fx(cur):
        if cur in cache:
            return cache[cur]
        for epic, inv in ((f"{cur}USD", False), (f"USD{cur}", True)):
            try:
                s = api.req("GET", f"/markets/{epic}")["snapshot"]
                mid = (s["bid"] + s["offer"]) / 2
                cache[cur] = 1 / mid if inv else mid
                return cache[cur]
            except ApiError:
                continue
        raise ApiError(f"No encontré tipo de cambio para {cur}")
    return fx


# ---------------------------------------------------------------- lógica principal
def run():
    demo = os.environ.get("CAPITAL_ENV", "demo").lower() != "live"
    mode = os.environ.get("HYDRA_MODE", "turbo").lower()
    risk_pct, heat_pct, kill_pct, lev = MODES[mode]
    start = float(os.environ.get("HYDRA_START", 5000))
    goal = float(os.environ.get("HYDRA_GOAL", 1_000_000))
    dry = os.environ.get("HYDRA_DRY_RUN", "0") == "1"
    if not demo and mode in ("reto", "turbo") and os.environ.get("HYDRA_ALLOW_AGGRESSIVE_LIVE") != "1":
        sys.exit("Los modos reto y turbo están bloqueados en cuenta real.")

    st = State(os.environ.get("STATE_DIR", os.path.join(os.getcwd(), "state")))
    api = Capital(demo, os.environ["CAPITAL_API_KEY"], os.environ["CAPITAL_IDENTIFIER"], os.environ["CAPITAL_API_PASSWORD"])
    now = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None)
    log(f"Hydra en Capital.com ({'DEMO' if demo else 'REAL'}), modo {mode}{' [simulación]' if dry else ''}")

    # primera vez: cobertura activada y, en demo, saldo igual al capital del reto
    if not st.d.get("initialized"):
        try:
            if not dry:
                api.req("PUT", "/accounts/preferences", json={"hedgingMode": True})
        except ApiError as e:
            log("Aviso: no pude activar el modo cobertura:", e)
        if demo and not dry:
            bal = account(api)["balance"]
            diff = round(start - bal, 2)
            if abs(diff) >= 1:
                try:
                    api.req("POST", "/accounts/topUp", json={"amount": diff})
                    log(f"Saldo demo ajustado a {start:,.0f} (cambio {diff:+,.2f})")
                except ApiError as e:
                    log("Aviso: no pude ajustar el saldo demo:", e)
        st.d["initialized"] = True
        st.d["start"] = start
        st.d["peak"] = 0.0

    fx = fx_converter(api)
    acc = account(api)
    equity = acc["balance"] + acc["profitLoss"]
    st.d["peak"] = max(st.d["peak"], equity)
    dd = 1 - equity / st.d["peak"] if st.d["peak"] else 0
    paused = dd * 100 >= kill_pct
    brake = 0.5 if dd > DD_BRAKE else 1.0
    log(f"Capital {equity:,.2f}  máximo {st.d['peak']:,.2f}  drawdown {dd*100:.1f}%{'  PAUSADO' if paused else ''}")

    # 1) posiciones que cerró el broker por stop desde la última vez
    live = {p["position"]["dealId"]: p for p in api.req("GET", "/positions").get("positions", [])}
    for deal_id, t in list(st.d["positions"].items()):
        if deal_id not in live:
            pnl = t["dir"] * (t["stop"] - t["entry"]) * t["size"] * t["vpp"]
            record_close(st, deal_id, t, t["stop"], pnl, "stop")

    n_mk = len(MARKETS)
    for name, epic, cls in MARKETS:
        try:
            df = daily_bars(api, epic, now)
            if len(df) < 300:
                log(f"{name}: pocos datos ({len(df)} velas), se omite")
                continue
            r = indicators(df).iloc[-1]
            info = Info(api, epic, fx)
        except (ApiError, KeyError) as e:
            log(f"{name}: no disponible ({e})")
            continue
        tradeable = info.status == "TRADEABLE"

        # 2) gestionar posiciones abiertas de este mercado
        for deal_id, t in list(st.d["positions"].items()):
            if t["epic"] != epic or not tradeable:
                continue
            code, d = t["strat"], t["dir"]
            close = False
            if code == "D":
                close = (d == 1 and r.c < r.ex_lo) or (d == -1 and r.c > r.ex_hi)
            elif code == "T":
                close = (d == 1 and r.mom <= 0) or (d == -1 and r.mom >= 0)
            else:
                held = int((df.index > pd.Timestamp(t["opened"])).sum())
                close = r.c > r.sma5 or held >= 10
            if close:
                if dry:
                    log(f"[sim] cerraría {name} {code}")
                    continue
                try:
                    c = api.confirm(api.req("DELETE", f"/positions/{deal_id}")["dealReference"])
                    px = c.get("level") or (info.bid if d == 1 else info.offer)
                    record_close(st, deal_id, t, px, d * (px - t["entry"]) * t["size"] * t["vpp"], "salida de la estrategia")
                except ApiError as e:
                    log(f"{name}: no pude cerrar {deal_id}: {e}")
                continue
            k = STRATS[code][2]
            if k > 0:
                nsl = round(r.c - d * k * r.atr, info.decimals)
                if (d == 1 and nsl > t["stop"]) or (d == -1 and nsl < t["stop"]):
                    if not dry:
                        try:
                            api.req("PUT", f"/positions/{deal_id}", json={"stopLevel": nsl})
                            t["stop"] = nsl
                            log(f"{name} {code}: stop movido a {nsl}")
                        except ApiError as e:
                            log(f"{name}: no pude mover stop: {e}")

        # 3) entradas nuevas
        if paused or not tradeable:
            continue
        for code, (fn, k_stop, _) in STRATS.items():
            if any(t["epic"] == epic and t["strat"] == code for t in st.d["positions"].values()):
                continue
            sig = fn(r, cls)
            if not sig:
                continue
            d = sig[0]
            arm = f"{name}_{code}"
            m = st.mult(arm)
            risk_usd = equity * risk_pct / 100 * m * brake
            heat = open_risk(st)
            if heat + risk_usd > equity * heat_pct / 100:
                log(f"{name} {code}: señal ignorada, riesgo abierto al límite")
                continue
            price = info.offer if d == 1 else info.bid
            dist = k_stop * r.atr
            size = risk_usd / (dist * info.vpp)
            size = min(size, equity * lev / max(1, n_mk / 4) / (price * info.vpp))
            size = info.round_size(size)
            if size < info.min_size:
                if info.min_size * dist * info.vpp <= risk_usd * 1.5:
                    size = info.min_size
                else:
                    log(f"{name} {code}: el tamaño mínimo arriesga demasiado, se omite")
                    continue
            stop = round(price - d * dist, info.decimals)
            real_risk = size * dist * info.vpp
            txt = f"{name} {code} {'COMPRA' if d == 1 else 'VENTA'} tamaño {size} a ~{price} stop {stop} riesgo ${real_risk:,.2f} (x{m:.2f})"
            if dry:
                log("[sim]", txt)
                continue
            try:
                ref = api.req("POST", "/positions", json={"epic": epic, "direction": "BUY" if d == 1 else "SELL",
                                                          "size": size, "stopLevel": stop})["dealReference"]
                c = api.confirm(ref)
                if c.get("dealStatus") != "ACCEPTED":
                    log(f"{name} {code}: orden rechazada {c.get('reason') or c}")
                    continue
                deal_id = (c.get("affectedDeals") or [{}])[0].get("dealId") or c.get("dealId")
                entry = c.get("level") or price
                st.d["positions"][deal_id] = dict(epic=epic, name=name, strat=code, dir=d, entry=entry,
                                                  stop=stop, size=size, vpp=info.vpp, risk=real_risk,
                                                  opened=str(df.index[-1].date()))
                log("Abierta:", txt)
            except ApiError as e:
                log(f"{name} {code}: error al abrir: {e}")

    acc = account(api)
    equity = acc["balance"] + acc["profitLoss"]
    st.d["peak"] = max(st.d["peak"], equity)
    st.d["history"].append([now.strftime("%Y-%m-%d"), round(equity, 2)])
    st.save()
    write_status(st, equity, goal, mode, demo, paused)
    log(f"Listo. Capital {equity:,.2f}, {len(st.d['positions'])} posiciones abiertas.")


def account(api):
    accs = api.req("GET", "/accounts")["accounts"]
    a = next((x for x in accs if x.get("preferred")), accs[0])
    return a["balance"]


def open_risk(st):
    return sum(max(0.0, t["dir"] * (t["entry"] - t["stop"])) * t["size"] * t["vpp"] for t in st.d["positions"].values())


def record_close(st, deal_id, t, px, pnl, why):
    R = pnl / t["risk"] if t["risk"] else 0
    st.d["learning"].append([f"{t['name']}_{t['strat']}", round(R, 4)])
    st.journal([datetime.now(timezone.utc).strftime("%Y-%m-%d"), t["name"], t["strat"],
                "compra" if t["dir"] == 1 else "venta", t["entry"], px, t["size"], round(pnl, 2), round(R, 2), why])
    log(f"Cerrada {t['name']} {t['strat']}: {pnl:+,.2f} USD ({R:+.2f}R, {why}). Nuevo multiplicador x{st.mult(t['name'] + '_' + t['strat']):.2f}")
    del st.d["positions"][deal_id]


def write_status(st, equity, goal, mode, demo, paused):
    start = st.d.get("start", 5000)
    prog = math.log(equity / start) / math.log(goal / start) * 100 if equity > start else 0
    dd = 1 - equity / st.d["peak"] if st.d["peak"] else 0
    names = {"D": "Donchian", "T": "Momentum", "M": "RSI(2)"}
    L = [f"# Hydra: estado al {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC", "",
         f"- Cuenta: Capital.com {'DEMO' if demo else 'REAL'} | modo **{mode}** | {'PAUSADO por drawdown' if paused else 'operando'}",
         f"- Capital: **${equity:,.2f}** (inicio ${start:,.0f}, máximo ${st.d['peak']:,.2f}, drawdown {dd*100:.1f}%)",
         f"- Meta ${goal:,.0f}: progreso {prog:.1f}% (escala logarítmica)", "",
         "## Posiciones abiertas", "", "| Mercado | Estrategia | Dirección | Entrada | Stop | Tamaño |", "|---|---|---|---|---|---|"]
    for t in st.d["positions"].values():
        L.append(f"| {t['name']} | {names[t['strat']]} | {'compra' if t['dir'] == 1 else 'venta'} | {t['entry']} | {t['stop']} | {t['size']} |")
    p = os.path.join(st.folder, "journal.csv")
    if os.path.exists(p):
        rows = list(csv.reader(open(p)))[1:][-15:]
        L += ["", "## Últimos trades cerrados", "", "| Fecha | Mercado | Estrategia | Resultado | R |", "|---|---|---|---|---|"]
        for r in reversed(rows):
            L.append(f"| {r[0]} | {r[1]} | {names.get(r[2], r[2])} | ${float(r[7]):+,.2f} | {r[8]} |")
    open(os.path.join(st.folder, "STATUS.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    run()
