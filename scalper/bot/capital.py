"""Thin client for the Capital.com API (REST + WebSocket), DEMO environment only.

Endpoints verified in research/01-capital-api.md against https://open-api.capital.com/.
- Session: POST /session with X-CAP-API-KEY -> CST and X-SECURITY-TOKEN headers (they expire after 10 min idle).
  We ping every 4 min and log in again automatically on a 401.
- Limits: 10 req/s per user; position openings 1 every 0.1 s; POST /session 1/s; demo: 1000 openings/hour.
- API failure: retries with exponential backoff, logs ERROR and never takes the bot down.
"""
import asyncio
import json
import random
import time

import httpx

from .config import DEMO_API, STREAM_URL, api_url


class ApiError(Exception):
    def __init__(self, msg, status=None, body=None):
        super().__init__(msg)
        self.status = status
        self.body = body


class RateLimiter:
    def __init__(self, per_sec=8.0):
        self.min_gap = 1.0 / per_sec
        self.last = 0.0
        self.lock = asyncio.Lock()

    async def wait(self):
        async with self.lock:
            gap = time.monotonic() - self.last
            if gap < self.min_gap:
                await asyncio.sleep(self.min_gap - gap)
            self.last = time.monotonic()


class CapitalClient:
    def __init__(self, key, identifier, password, log, base=None):
        self.base = base or api_url()
        assert self.base == DEMO_API, "solo DEMO"
        self.key, self.identifier, self.password = key, identifier, password
        self.log = log
        self.cst = self.token = None
        self.streaming_host = STREAM_URL
        self.session_info = {}
        self.http = httpx.AsyncClient(timeout=20)
        self.rl = RateLimiter(8.0)
        self.login_lock = asyncio.Lock()
        self.last_login = 0.0
        self.trades_hour = []

    # ------------------------------------------------------------- session
    async def login(self):
        async with self.login_lock:
            wait = 1.1 - (time.monotonic() - self.last_login)
            if wait > 0:
                await asyncio.sleep(wait)
            self.last_login = time.monotonic()
            r = await self.http.post(self.base + "/session", headers={"X-CAP-API-KEY": self.key},
                                     json={"identifier": self.identifier, "password": self.password,
                                           "encryptedPassword": False})
            if r.status_code >= 400:
                raise ApiError(f"login falló ({r.status_code}): {r.text[:200]}", r.status_code)
            self.cst, self.token = r.headers.get("CST"), r.headers.get("X-SECURITY-TOKEN")
            body = r.json()
            self.session_info = {k: body.get(k) for k in ("accountType", "currencyIsoCode", "currentAccountId",
                                                           "trailingStopsEnabled", "hasActiveLiveAccounts")}
            host = body.get("streamingHost")
            if host:
                self.streaming_host = host.rstrip("/") + ("/connect" if not host.rstrip("/").endswith("connect") else "")
                if self.streaming_host.startswith("https://"):
                    self.streaming_host = "wss://" + self.streaming_host[8:]
            return body

    def _headers(self):
        return {"X-CAP-API-KEY": self.key, "CST": self.cst or "", "X-SECURITY-TOKEN": self.token or ""}

    async def req(self, method, path, retries=4, **kw):
        last = None
        for attempt in range(retries):
            if not self.cst:
                try:
                    await self.login()
                except (ApiError, httpx.HTTPError) as e:
                    last = e
                    await asyncio.sleep(min(30, 2 ** attempt + random.random()))
                    continue
            await self.rl.wait()
            try:
                r = await self.http.request(method, self.base + path, headers=self._headers(), **kw)
            except httpx.HTTPError as e:
                last = ApiError(f"red: {type(e).__name__}")
                await asyncio.sleep(min(30, 2 ** attempt + random.random()))
                continue
            if r.status_code == 401:
                self.cst = None   # expired session: log in again
                last = ApiError("sesión expirada", 401)
                continue
            if r.status_code == 429 or r.status_code >= 500:
                last = ApiError(f"{method} {path}: {r.status_code}", r.status_code, r.text[:300])
                await asyncio.sleep(min(30, 2 ** attempt + random.random()))
                continue
            if r.status_code >= 400:
                raise ApiError(f"{method} {path}: {r.status_code} {r.text[:300]}", r.status_code, r.text[:300])
            return r.json() if r.text else {}
        raise last or ApiError(f"{method} {path}: sin respuesta")

    async def ping(self):
        return await self.req("GET", "/ping")

    # ------------------------------------------------------------- account
    async def accounts(self):
        return await self.req("GET", "/accounts")

    async def balance(self):
        acc = await self.accounts()
        for a in acc.get("accounts", []):
            if a.get("preferred") or len(acc["accounts"]) == 1:
                b = a.get("balance", {})
                return {"balance": b.get("balance"), "upl": b.get("profitLoss"), "available": b.get("available"),
                        "deposit": b.get("deposit"), "currency": a.get("currency")}
        return {}

    async def preferences(self):
        return await self.req("GET", "/accounts/preferences")

    async def top_up(self, amount):
        return await self.req("POST", "/accounts/topUp", json={"amount": amount}, retries=1)

    # ------------------------------------------------------------- markets
    async def market(self, epic):
        return await self.req("GET", f"/markets/{epic}")

    async def prices(self, epic, resolution="MINUTE_5", start=None, end=None, max_=1000):
        params = {"resolution": resolution, "max": max_}
        if start:
            params["from"] = start
        if end:
            params["to"] = end
        return (await self.req("GET", f"/prices/{epic}", params=params)).get("prices", [])

    async def sentiment(self, market_ids):
        r = await self.req("GET", "/clientsentiment", params={"marketIds": ",".join(market_ids)})
        return r.get("clientSentiments", [])

    # ------------------------------------------------------------- trading
    async def positions(self):
        return (await self.req("GET", "/positions")).get("positions", [])

    async def open_position(self, epic, direction, size, stop_level, profit_level=None):
        now = time.time()
        self.trades_hour = [t for t in self.trades_hour if now - t < 3600]
        if len(self.trades_hour) >= 900:   # demo: max 1000/hour
            raise ApiError("límite demo de aperturas por hora")
        self.trades_hour.append(now)
        body = {"epic": epic, "direction": "BUY" if direction > 0 else "SELL", "size": size,
                "guaranteedStop": False, "trailingStop": False, "stopLevel": stop_level}
        if profit_level:
            body["profitLevel"] = profit_level
        # retries=1: a repeated opening could duplicate the position. If it fails, the caller reconciles.
        return await self.req("POST", "/positions", json=body, retries=1)

    async def confirm(self, deal_ref, tries=8):
        for i in range(tries):
            try:
                c = await self.req("GET", f"/confirms/{deal_ref}", retries=2)
                if c.get("dealStatus"):
                    return c
            except ApiError:
                pass
            await asyncio.sleep(0.5 * (i + 1))
        return {}

    async def update_position(self, deal_id, stop_level, profit_level=None):
        """Always sends the full state (stop + TP + flags): Capital may delete omitted fields."""
        body = {"guaranteedStop": False, "trailingStop": False, "stopLevel": stop_level}
        if profit_level:
            body["profitLevel"] = profit_level
        return await self.req("PUT", f"/positions/{deal_id}", json=body)

    async def close_position(self, deal_id):
        return await self.req("DELETE", f"/positions/{deal_id}")

    async def activity(self, last_period=3600, deal_id=None):
        params = {"lastPeriod": min(86400, int(last_period)), "detailed": "true"}
        if deal_id:
            params["dealId"] = deal_id
        return (await self.req("GET", "/history/activity", params=params)).get("activities", [])

    async def transactions(self, last_period=86400, type_=None):
        params = {"lastPeriod": min(86400, int(last_period))}
        if type_:
            params["type"] = type_
        return (await self.req("GET", "/history/transactions", params=params)).get("transactions", [])

    async def close(self):
        await self.http.aclose()


class Stream:
    """WebSocket of quotes. Reconnects alone with backoff and pings every 4 min."""

    def __init__(self, client: CapitalClient, epics, on_quote, log):
        self.client, self.epics, self.on_quote, self.log = client, list(epics), on_quote, log
        self.connected = False
        self.last_msg = 0.0
        self._corr = 0

    def _msg(self, dest, payload=None):
        self._corr += 1
        m = {"destination": dest, "correlationId": str(self._corr), "cst": self.client.cst,
             "securityToken": self.client.token}
        if payload is not None:
            m["payload"] = payload
        return json.dumps(m)

    async def run(self):
        import websockets
        backoff = 1
        while True:
            try:
                if not self.client.cst:
                    await self.client.login()
                async with websockets.connect(self.client.streaming_host, ping_interval=None, open_timeout=20) as ws:
                    await ws.send(self._msg("marketData.subscribe", {"epics": self.epics[:40]}))
                    self.connected = True
                    backoff = 1
                    self.log("STREAM", "-", f"conectado, {len(self.epics)} instrumentos")
                    pinger = asyncio.create_task(self._pinger(ws))
                    try:
                        async for raw in ws:
                            self.last_msg = time.time()
                            m = json.loads(raw)
                            if m.get("destination") == "quote":
                                p = m.get("payload", {})
                                await self.on_quote(p.get("epic"), float(p["bid"]), float(p["ofr"]),
                                                    p.get("timestamp", time.time() * 1000) / 1000)
                            elif m.get("status") == "ERROR":
                                self.log("ERROR", "-", f"stream: {str(m.get('payload'))[:150]}", "error")
                                self.client.cst = None
                                break
                    finally:
                        pinger.cancel()
            except asyncio.CancelledError:
                raise
            except Exception as e:  # never kill the bot: reconnect
                self.log("ERROR", "-", f"stream caído: {type(e).__name__}; reintento en {backoff}s", "error")
            self.connected = False
            await asyncio.sleep(backoff)
            backoff = min(60, backoff * 2)

    async def _pinger(self, ws):
        while True:
            await asyncio.sleep(240)
            await ws.send(self._msg("ping"))
