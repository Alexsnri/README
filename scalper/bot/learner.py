"""Learner agent: picks and reweights the validated strategies with a bandit (Gaussian Thompson sampling over
R-multiples with discounting), follows the candidates in paper ("shadow") and only changes something with enough
sample. Every change is recorded with its reason. It never learns from a single streak: a minimum of 50 live
trades before cutting risk and 271 before promoting.
"""
import math
import random
import time
from statistics import NormalDist

N = NormalDist()


class Arm:
    def __init__(self, key, prior_mean=0.0, prior_n=50, sigma=1.2):
        self.key = key
        self.prior_mean, self.prior_n, self.sigma = prior_mean, prior_n, sigma
        self.w = 0.0      # discounted sum of weights
        self.sw = 0.0     # discounted sum of R
        self.n_raw = 0
        self.sum_r = 0.0
        self.sum_r2 = 0.0

    def update(self, r, gamma):
        self.w = self.w * gamma + 1.0
        self.sw = self.sw * gamma + r
        self.n_raw += 1
        self.sum_r += r
        self.sum_r2 += r * r

    @property
    def n_eff(self):
        return self.prior_n + self.w

    @property
    def mean(self):
        return (self.prior_mean * self.prior_n + self.sw) / self.n_eff

    @property
    def sd(self):
        if self.n_raw > 10:
            m = self.sum_r / self.n_raw
            v = max(1e-6, self.sum_r2 / self.n_raw - m * m)
            return math.sqrt(v)
        return self.sigma

    @property
    def p_positive(self):
        return N.cdf(self.mean / (self.sd / math.sqrt(self.n_eff)))

    def sample(self, rng=random):
        return rng.gauss(self.mean, self.sd / math.sqrt(self.n_eff))

    def raw_lower95(self):
        if self.n_raw < 2:
            return float("-inf")
        m = self.sum_r / self.n_raw
        return m - 1.96 * self.sd / math.sqrt(self.n_raw)

    def to_dict(self):
        return {k: getattr(self, k) for k in ("key", "prior_mean", "prior_n", "sigma", "w", "sw", "n_raw", "sum_r",
                                               "sum_r2")}

    @classmethod
    def from_dict(cls, d):
        a = cls(d["key"], d["prior_mean"], d["prior_n"], d["sigma"])
        for k in ("w", "sw", "n_raw", "sum_r", "sum_r2"):
            setattr(a, k, d[k])
        return a


class Learner:
    def __init__(self, cfg: dict, arms_cfg: list, priors: dict, store, log):
        self.cfg, self.store, self.log = cfg, store, log
        saved = store.kv_get("learner_arms") or {}
        self.modes = {}
        self.arms = {}
        for a in arms_cfg:
            key = f"{a['estrategia']}-{a['instrumento']}"
            self.modes[key] = a["modo"]
            if key in saved:
                self.arms[key] = Arm.from_dict(saved[key])
            else:
                # prior = half of the backtest OOS expectancy (publication and data-mining discount)
                self.arms[key] = Arm(key, prior_mean=0.5 * priors.get(key, 0.0), prior_n=cfg["prior_trades"])
        self.modes.update(store.kv_get("learner_modes") or {})
        self.mult = store.kv_get("learner_mult") or {k: 1.0 for k in self.arms}
        self.last_reopt = store.kv_get("learner_last_reopt") or 0

    def save(self):
        self.store.kv_set("learner_arms", {k: a.to_dict() for k, a in self.arms.items()})
        self.store.kv_set("learner_modes", self.modes)
        self.store.kv_set("learner_mult", self.mult)

    def record(self, key, cambio, razon):
        self.store.x("INSERT INTO learner_log(ts,arm,cambio,razon) VALUES(?,?,?,?)", (time.time(), key, cambio, razon))
        self.log("LEARN", key, f"{cambio} — {razon}")

    def on_trade(self, key, r):
        if key not in self.arms:
            return
        arm = self.arms[key]
        arm.update(r, self.cfg["descuento"])
        if self.modes.get(key) == "vivo":
            self._review_live(key)
        else:
            self._review_shadow(key)
        self.save()

    def _review_live(self, key):
        a = self.arms[key]
        if a.n_raw < 50:
            return
        p = a.p_positive
        old = self.mult.get(key, 1.0)
        if p < 0.05:
            new, why = 0.0, f"P(E>0)={p:.2f} con {a.n_raw} trades reales: se pausa el brazo"
        elif p < self.cfg["pausar_si_prob_menor"]:
            new, why = 0.5, f"P(E>0)={p:.2f} < {self.cfg['pausar_si_prob_menor']}: medio riesgo"
        elif p > 0.5:
            new, why = 1.0, f"P(E>0)={p:.2f}: riesgo normal"
        else:
            return
        if new != old:
            self.mult[key] = new
            self.record(key, f"multiplicador de riesgo {old:.1f} → {new:.1f}", why)

    def _review_shadow(self, key):
        a = self.arms[key]
        if a.n_raw >= self.cfg["promover_min_trades"] and a.raw_lower95() > 0:
            if self.cfg.get("auto_promover"):
                self.modes[key] = "vivo"
                self.mult[key] = 0.5
                self.record(key, "PROMOVIDO a vivo (medio riesgo)",
                            f"{a.n_raw} trades en sombra, IC95 inferior {a.raw_lower95():+.3f}R > 0")
            elif not self.store.kv_get(f"promo_avisada_{key}"):
                self.store.kv_set(f"promo_avisada_{key}", True)
                self.record(key, "candidato a promover (manda /promover " + key + ")",
                            f"{a.n_raw} trades en sombra, IC95 inferior {a.raw_lower95():+.3f}R > 0")

    def promote(self, key):
        if key in self.arms:
            self.modes[key] = "vivo"
            self.mult[key] = 0.5
            self.record(key, "PROMOVIDO a vivo (medio riesgo) por orden del usuario", "/promover")
            self.save()

    def thompson_order(self, keys):
        """Order of preference among live arms (when several compete for the same risk budget)."""
        return sorted(keys, key=lambda k: -self.arms[k].sample())

    def snapshot(self):
        out = []
        for k, a in self.arms.items():
            out.append({"arm": k, "modo": self.modes.get(k), "n": a.n_raw, "media": a.mean, "p_pos": a.p_positive,
                        "mult": self.mult.get(k, 1.0), "real_media": a.sum_r / a.n_raw if a.n_raw else None})
        return out

    def changes(self, n=10):
        return self.store.q("SELECT ts,arm,cambio,razon FROM learner_log ORDER BY id DESC LIMIT ?", (n,))
