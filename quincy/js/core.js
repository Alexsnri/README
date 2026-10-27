// Quincy · núcleo: configuración, estado, cálculos y utilidades compartidas.
window.FY = Object.assign(window.FY || {}, (() => {
  const CONFIG = {
    SITE: "https://alexsnri.github.io/README/quincy/",
    // Donde llegan las solicitudes de instituciones. Cámbialo por tu correo o formulario.
    CONTACT_URL: "https://github.com/Alexsnri/README/issues/new?template=piloto.yml",
    // Token de Cloudflare Web Analytics (gratis, sin cookies). Vacío = sin analítica.
    CF_ANALYTICS_TOKEN: "",
    // true en la copia que vive dentro del visor de Claude (ahí no se pueden descargar archivos).
    EMBEDDED_VIEWER: false
  };

  const YEAR = new Date().getFullYear();
  const INITIAL_SEARCH = location.search; // app.js limpia la URL; aquí queda la original
  const RATES = { cetes: 6.23, inflacion: 3.45, optimista: 9.0 };
  const $ = (id) => document.getElementById(id);
  const mxn = new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 });
  const fmt = (v) => mxn.format(Math.round(v));
  const short = (v) => v >= 1e6 ? "$" + (v / 1e6).toLocaleString("es-MX", { maximumFractionDigits: 1 }) + " M"
    : v >= 1e3 ? "$" + Math.round(v / 1e3).toLocaleString("es-MX") + " mil" : fmt(v);
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const store = {
    get(k, d) { try { const v = localStorage.getItem("qc:" + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem("qc:" + k, JSON.stringify(v)); return true; } catch (e) { return false; } },
    del(k) { try { localStorage.removeItem("qc:" + k); } catch (e) {} }
  };

  const state = Object.assign(
    { age: 28, retire: 65, monthly: 1500, saved: 10000, need: 15000, veh: "cetes", skin: 2, hair: "short" },
    store.get("state", {})
  );
  const save = () => store.set("state", state);

  const VEH = {
    colchon: { name: "bajo el colchón", label: "Bajo el colchón", rate: () => 0 },
    cetes: { name: "CETES", label: "CETES", rate: () => RATES.cetes },
    optimista: { name: "un portafolio diversificado", label: "Diversificado (supuesto)", rate: () => RATES.optimista }
  };

  // ---- dinero en el tiempo, todo en pesos de hoy ----
  const realAnnual = (nominalPct) => (1 + nominalPct / 100) / (1 + RATES.inflacion / 100) - 1;
  const monthlyReal = (nominalPct) => Math.pow(1 + realAnnual(nominalPct), 1 / 12) - 1;
  function balanceAt(months, nominalPct, monthly, saved) {
    const i = monthlyReal(nominalPct);
    const g = Math.pow(1 + i, months);
    return saved * g + (Math.abs(i) < 1e-9 ? monthly * months : monthly * (g - 1) / i);
  }
  function requiredMonthly(target, months, nominalPct, saved) {
    const i = monthlyReal(nominalPct);
    const g = Math.pow(1 + i, months);
    const left = target - saved * g;
    if (left <= 0) return 0;
    return Math.abs(i) < 1e-9 ? left / months : left * i / (g - 1);
  }
  const targetFor = (need) => need * 12 / 0.04;
  const yearsLeft = () => Math.max(1, state.retire - state.age);
  // Lo que vale a tu retiro un peso que inviertes hoy en CETES (en pesos de hoy).
  const futureOf = (amount) => amount * Math.pow(1 + realAnnual(RATES.cetes), yearsLeft());
  // Una cantidad que se repite: "week" | "month" | "day" hasta tu retiro.
  function futureOfRecurring(amount, every) {
    const perMonth = every === "day" ? amount * 30.4 : every === "week" ? amount * 4.345 : amount;
    return balanceAt(yearsLeft() * 12, RATES.cetes, perMonth, 0);
  }
  // Días de retiro que paga una cantidad, según lo que quieres recibir al mes.
  const freedomDays = (futureAmount) => futureAmount / (state.need / 30.4);

  // ---- fechas locales ----
  const dayKey = (d = new Date()) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const keyToDate = (k) => { const [y, m, d] = k.split("-").map(Number); return new Date(y, m - 1, d); };
  const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };

  // ---- aleatorio con semilla (mismo resultado para todos el mismo día) ----
  function rng(seed) {
    let a = seed >>> 0;
    return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }

  // ---- retroalimentación ----
  function toast(msg) {
    const t = document.createElement("div");
    t.className = "toast"; t.textContent = msg; t.setAttribute("role", "status");
    document.body.appendChild(t); setTimeout(() => t.remove(), 2600);
  }
  function buzz(pattern) { try { if (navigator.vibrate) navigator.vibrate(pattern || 12); } catch (e) {} }
  function confetti() {
    if (reduced) return;
    const c = document.createElement("canvas");
    c.className = "confetti"; c.setAttribute("aria-hidden", "true");
    document.body.appendChild(c);
    const d = Math.min(2, devicePixelRatio || 1);
    c.width = innerWidth * d; c.height = innerHeight * d;
    const x = c.getContext("2d");
    const cols = ["#ffb547", "#5ad6c8", "#86e3a8", "#eaf3f4", "#ff8574"];
    const parts = Array.from({ length: 120 }, () => ({
      x: c.width / 2, y: c.height * 0.55, vx: (Math.random() - 0.5) * 22 * d, vy: (-Math.random() * 22 - 8) * d,
      s: (4 + Math.random() * 6) * d, r: Math.random() * 6, vr: (Math.random() - 0.5) * 0.4, c: cols[(Math.random() * cols.length) | 0]
    }));
    let f = 0;
    (function step() {
      x.clearRect(0, 0, c.width, c.height);
      for (const p of parts) {
        p.vy += 0.9 * d; p.vx *= 0.99; p.x += p.vx; p.y += p.vy; p.r += p.vr;
        x.save(); x.translate(p.x, p.y); x.rotate(p.r); x.fillStyle = p.c; x.fillRect(-p.s / 2, -p.s / 4, p.s, p.s / 2); x.restore();
      }
      if (++f < 90) requestAnimationFrame(step); else c.remove();
    })();
  }
  async function copyText(txt) {
    try { await navigator.clipboard.writeText(txt); toast("Copiado"); return; } catch (e) {}
    const ta = document.createElement("textarea");
    ta.value = txt; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    let ok = false; try { ok = document.execCommand("copy"); } catch (e) {}
    ta.remove();
    toast(ok ? "Copiado" : "No pude copiar. Mantén presionado el texto para copiarlo.");
  }
  // Abre la hoja de compartir del teléfono si existe; si no, devuelve false.
  async function nativeShare(data) {
    try {
      if (data.files && !(navigator.canShare && navigator.canShare({ files: data.files }))) delete data.files;
      if (!navigator.share) return false;
      await navigator.share(data); return true;
    } catch (e) { return e && e.name === "AbortError"; }
  }
  function download(blob, name) {
    if (CONFIG.EMBEDDED_VIEWER) { toast("Mantén presionada la imagen para guardarla"); return; }
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  }
  const shareURL = (params) => {
    const u = new URL(CONFIG.SITE);
    Object.entries(params || {}).forEach(([k, v]) => u.searchParams.set(k, v));
    return u.toString();
  };
  // Pequeño bus de eventos entre módulos.
  const bus = new EventTarget();
  const on = (n, f) => bus.addEventListener(n, (e) => f(e.detail));
  const emit = (n, d) => bus.dispatchEvent(new CustomEvent(n, { detail: d }));

  return {
    CONFIG, YEAR, INITIAL_SEARCH, RATES, VEH, state, save, store, $, fmt, short, clamp, reduced,
    realAnnual, monthlyReal, balanceAt, requiredMonthly, targetFor, yearsLeft, futureOf, futureOfRecurring, freedomDays,
    dayKey, keyToDate, addDays, rng, toast, buzz, confetti, copyText, nativeShare, download, shareURL, on, emit
  };
})());
