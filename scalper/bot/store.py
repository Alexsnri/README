"""SQLite persistence: events, trades, positions, stop moves, learner state and live market data.

Everything needed to pick up where the bot left off after a restart lives here (watchdog).
"""
import json
import os
import sqlite3
import threading
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT);
CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, ts REAL, hhmm TEXT, evento TEXT, instrumento TEXT,
    detalle TEXT, nivel TEXT);
CREATE TABLE IF NOT EXISTS positions (deal_id TEXT PRIMARY KEY, arm TEXT, instrumento TEXT, dir INTEGER, size REAL,
    entry REAL, stop REAL, stop0 REAL, tp REAL, atr REAL, opened REAL, best REAL, shadow INTEGER, data TEXT);
CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, deal_id TEXT, arm TEXT, instrumento TEXT, dir INTEGER,
    size REAL, entry REAL, exit REAL, stop0 REAL, opened REAL, closed REAL, pnl REAL, r REAL, motivo TEXT,
    spread_in REAL, slip_in REAL, costos REAL, shadow INTEGER, moves INTEGER);
CREATE TABLE IF NOT EXISTS stop_moves (id INTEGER PRIMARY KEY, deal_id TEXT, ts REAL, old REAL, new REAL, razon TEXT,
    confirmado INTEGER);
CREATE TABLE IF NOT EXISTS learner_log (id INTEGER PRIMARY KEY, ts REAL, arm TEXT, cambio TEXT, razon TEXT);
CREATE TABLE IF NOT EXISTS spreads (ts REAL, instrumento TEXT, bid REAL, ask REAL);
CREATE TABLE IF NOT EXISTS sentiment (ts REAL, instrumento TEXT, long_pct REAL);
CREATE TABLE IF NOT EXISTS bars5 (instrumento TEXT, t INTEGER, o REAL, h REAL, l REAL, c REAL,
    PRIMARY KEY (instrumento, t));
CREATE TABLE IF NOT EXISTS equity (ts REAL, balance REAL, upl REAL);
CREATE INDEX IF NOT EXISTS ix_events_ts ON events(ts);
CREATE INDEX IF NOT EXISTS ix_trades_closed ON trades(closed);
"""


class Store:
    def __init__(self, path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)
        self.lock = threading.Lock()

    def x(self, sql, args=()):
        with self.lock:
            return self.db.execute(sql, args)

    def q(self, sql, args=()):
        with self.lock:
            cur = self.db.execute(sql, args)
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]

    # key/value (bot state, learner, breakers)
    def kv_get(self, k, default=None):
        r = self.q("SELECT v FROM kv WHERE k=?", (k,))
        return json.loads(r[0]["v"]) if r else default

    def kv_set(self, k, v):
        self.x("INSERT INTO kv(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, json.dumps(v)))

    # positions
    def save_position(self, p: dict):
        cols = ["deal_id", "arm", "instrumento", "dir", "size", "entry", "stop", "stop0", "tp", "atr", "opened", "best",
                "shadow"]
        extra = {k: v for k, v in p.items() if k not in cols}
        self.x(f"INSERT OR REPLACE INTO positions({','.join(cols)},data) VALUES({','.join('?' * (len(cols) + 1))})",
               [p.get(c) for c in cols] + [json.dumps(extra, default=str)])

    def positions(self):
        out = []
        for r in self.q("SELECT * FROM positions"):
            extra = json.loads(r.pop("data") or "{}")
            r.update(extra)
            out.append(r)
        return out

    def drop_position(self, deal_id):
        self.x("DELETE FROM positions WHERE deal_id=?", (deal_id,))

    def add_trade(self, t: dict):
        cols = ["deal_id", "arm", "instrumento", "dir", "size", "entry", "exit", "stop0", "opened", "closed", "pnl", "r",
                "motivo", "spread_in", "slip_in", "costos", "shadow", "moves"]
        self.x(f"INSERT INTO trades({','.join(cols)}) VALUES({','.join('?' * len(cols))})", [t.get(c) for c in cols])

    def trades(self, since=0.0, shadow=None):
        sql = "SELECT * FROM trades WHERE closed>=?"
        args = [since]
        if shadow is not None:
            sql += " AND shadow=?"
            args.append(int(shadow))
        return self.q(sql + " ORDER BY closed", args)

    def add_bar(self, inst, t, o, h, l, c):
        self.x("INSERT OR REPLACE INTO bars5 VALUES(?,?,?,?,?,?)", (inst, int(t), o, h, l, c))

    def bars(self, inst, since_t=0):
        return self.q("SELECT t,o,h,l,c FROM bars5 WHERE instrumento=? AND t>=? ORDER BY t", (inst, int(since_t)))

    def prune(self, days_ticks=30, days_events=90):
        now = time.time()
        self.x("DELETE FROM spreads WHERE ts<?", (now - days_ticks * 86400,))
        self.x("DELETE FROM events WHERE ts<?", (now - days_events * 86400,))
        self.x("DELETE FROM equity WHERE ts<?", (now - 365 * 86400,))
