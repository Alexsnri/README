"""Logger agent: writes down every event as `HH:MM EVENTO INSTRUMENTO detalle` (CDMX time).

It writes to a rotating file (it does not fill the disk), to SQLite, and sends each line to the dashboard.
Every text goes through `redact` so that no credential ever ends up in a log.
"""
import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from .config import redact
from .schedule import CDMX


class Hub:
    """In-process bus: the dashboard and Telegram subscribe to events."""

    def __init__(self):
        self.subs = []

    def subscribe(self):
        q = asyncio.Queue(maxsize=500)
        self.subs.append(q)
        return q

    def unsubscribe(self, q):
        if q in self.subs:
            self.subs.remove(q)

    def publish(self, kind, data):
        for q in list(self.subs):
            try:
                q.put_nowait({"kind": kind, "data": data})
            except asyncio.QueueFull:
                pass


class Logger:
    def __init__(self, store, hub, folder):
        os.makedirs(folder, exist_ok=True)
        self.store, self.hub = store, hub
        self.file = logging.getLogger("night")
        self.file.setLevel(logging.INFO)
        if not self.file.handlers:
            h = RotatingFileHandler(os.path.join(folder, "night.log"), maxBytes=5_000_000, backupCount=5,
                                    encoding="utf-8")
            h.setFormatter(logging.Formatter("%(message)s"))
            self.file.addHandler(h)
        self.line_no = (store.q("SELECT COALESCE(MAX(id),0) AS n FROM events")[0]["n"])
        self.listeners = []   # callables(evento, inst, detalle, nivel) -> e.g. Telegram
        self.now = time.time  # the simulation replaces it with its clock

    def __call__(self, evento, inst="-", detalle="", nivel="info"):
        detalle = redact(str(detalle))
        now = self.now()
        hhmm = datetime.fromtimestamp(now, timezone.utc).astimezone(CDMX).strftime("%H:%M")
        line = f"{hhmm} {evento.upper():6s} {inst} {detalle}"
        self.store.x("INSERT INTO events(ts,hhmm,evento,instrumento,detalle,nivel) VALUES(?,?,?,?,?,?)",
                     (now, hhmm, evento.upper(), inst, detalle, nivel))
        self.line_no += 1
        self.file.info(f"{datetime.fromtimestamp(now, timezone.utc).astimezone(CDMX):%Y-%m-%d} {line}")
        print(line, flush=True)
        self.hub.publish("log", {"n": self.line_no, "hhmm": hhmm, "evento": evento.upper(), "inst": inst,
                                 "detalle": detalle, "nivel": nivel})
        for f in self.listeners:
            try:
                f(evento.upper(), inst, detalle, nivel)
            except Exception:  # a notification must never take the bot down
                pass

    def tail(self, n=60):
        rows = self.store.q("SELECT id,hhmm,evento,instrumento,detalle,nivel FROM events ORDER BY id DESC LIMIT ?", (n,))
        return [{"n": r["id"], "hhmm": r["hhmm"], "evento": r["evento"], "inst": r["instrumento"],
                 "detalle": r["detalle"], "nivel": r["nivel"]} for r in reversed(rows)]
