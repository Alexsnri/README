"""Alerts to your phone over Telegram (your own bot, token in TELEGRAM_TOKEN) and commands from the phone.

Pairing: if you don't set TELEGRAM_CHAT_ID, send your bot `/vincular CODE` (the code shows on the dashboard).
Only that chat can send commands. Commands: /estado /pausa /reanudar /perfil normal|agresivo /reporte
/promover ARM /ayuda
"""
import asyncio
import os
import time

import httpx

from .config import redact

HELP = ("Comandos:\n/estado — balance, posición y estado\n/pausa — no abre nada nuevo (las abiertas siguen con "
        "su stop)\n/reanudar — vuelve a operar\n/perfil normal | /perfil agresivo\n/reporte — resumen del día y "
        "acumulado\n/promover S1-US500 — pasa un brazo de sombra a vivo\n/ayuda")


class Telegram:
    def __init__(self, store, log, pairing_code):
        self.token = os.environ.get("TELEGRAM_TOKEN", "")
        self.chat = os.environ.get("TELEGRAM_CHAT_ID") or store.kv_get("telegram_chat")
        self.store, self.log, self.code = store, log, pairing_code
        self.http = httpx.AsyncClient(timeout=40)
        self.queue = asyncio.Queue()
        self.handlers = {}
        self.last_err = {}
        self.enabled = bool(self.token)

    @property
    def base(self):
        return f"https://api.telegram.org/bot{self.token}"

    def send(self, text):
        if self.enabled and self.chat:
            self.queue.put_nowait(redact(text)[:3900])

    def on_log(self, evento, inst, detalle, nivel):
        """Logger listener: serious errors to the phone (at most 1 per type every 10 min)."""
        if nivel == "error":
            key = detalle[:40]
            if time.time() - self.last_err.get(key, 0) > 600:
                self.last_err[key] = time.time()
                self.send(f"🛑 ERROR {inst}: {detalle}")

    async def sender(self):
        while True:
            text = await self.queue.get()
            for attempt in range(4):
                try:
                    await self.http.post(self.base + "/sendMessage", json={"chat_id": self.chat, "text": text})
                    break
                except httpx.HTTPError:
                    await asyncio.sleep(2 ** attempt)

    async def poller(self):
        offset = self.store.kv_get("telegram_offset", 0)
        while True:
            try:
                r = await self.http.get(self.base + "/getUpdates", params={"timeout": 30, "offset": offset})
                for u in r.json().get("result", []):
                    offset = u["update_id"] + 1
                    self.store.kv_set("telegram_offset", offset)
                    msg = u.get("message") or {}
                    chat = str(msg.get("chat", {}).get("id", ""))
                    text = (msg.get("text") or "").strip()
                    if text.startswith("/vincular"):
                        self.pair_tries = [t for t in getattr(self, "pair_tries", []) if time.time() - t < 3600]
                        if self.chat or len(self.pair_tries) >= 5:
                            continue   # already linked (or too many attempts): ignored
                        self.pair_tries.append(time.time())
                        if text.split()[-1] == self.code:
                            self.chat = chat
                            self.store.kv_set("telegram_chat", chat)
                            self.send("✅ Vinculado. Te aviso cada trade, cada breaker, errores graves y un resumen "
                                      "a las 8:00.\n\n" + HELP)
                            self.log("TELEG", "-", "chat vinculado")
                        continue
                    if not self.chat or chat != str(self.chat):
                        continue   # only the paired chat can give orders
                    cmd, *args = text.split()
                    h = self.handlers.get(cmd.lower().split("@")[0])
                    reply = await h(*args) if h else HELP
                    if reply:
                        self.send(reply)
            except Exception:
                await asyncio.sleep(10)
