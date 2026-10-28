// Quincy · núcleo: configuración, estado, cálculos y utilidades compartidas.
window.FY = Object.assign(window.FY || {}, (() => {
  const CONFIG = {
    SITE: "https://alexsnri.github.io/README/quincy/",
    // Donde llegan las solicitudes de instituciones. Cámbialo por tu correo o formulario.
    CONTACT_URL: "https://github.com/Alexsnri/README/issues/new?template=piloto.yml",
    // Correo de Quincy para empresas. Si existe, "Solicitar piloto" abre un correo ya escrito (mejor que pedir cuenta de GitHub).
    CONTACT_EMAIL: "hola.quincymx@gmail.com",
    // Token de Cloudflare Web Analytics (gratis, sin cookies). Vacío = sin analítica.
    CF_ANALYTICS_TOKEN: "7867bd7b5a2449549624cefc62551f12",
    // Redes de Quincy.
    INSTAGRAM: "https://www.instagram.com/quincy_app/",
    TIKTOK: "https://www.tiktok.com/@quincyapp",
    // Avisos opcionales (audiencia propia, sin registro). Vacío = ese botón no se muestra.
    // whatsappCanal: enlace del canal de WhatsApp. correoForm: enlace del formulario de un servicio de correos.
    // Al llenar cualquiera, enlaza también privacidad.html (llena antes ahí el nombre y correo del responsable).
    AVISOS: {
      whatsappCanal: "https://whatsapp.com/channel/0029VbDxhAFHFxOyjGQ9862q",
      correoForm: "https://b0e92322.sibforms.com/serve/MUIFANod8iT6Q0WKuLJ7dt1xCEk2IO7pZUcY_MRtbf9W5qLTGLM4ymmB4Z4vrMvCAJ4ED5bQhaElq5H-Xv1qy7eYOfF28NiaGsazAX4kDvefqlNVal6tsTRwqULbBFpgP5dE3d5O6p4vDP7gtKSDgB1Wr0J8iBtalOvSkb2HYrgdxWcwaWCrmY1TJqSoTjGzbdkVwD-_wDC7VomXzg=="
    },
    // true en la copia que vive dentro del visor de Claude (ahí no se pueden descargar archivos).
    EMBEDDED_VIEWER: false,
    // Enlaces de referido que el dueño ya dio de alta. Vacío = no se muestra nada.
    // Ejemplo: cetes: { nombre: "Abre tu cuenta en …", url: "https://…", nota: "Banco · protegido por el IPAB" }
    REFERIDOS: {}
  };

  // Analítica sin cookies en todas las páginas, solo en el sitio publicado (no en pruebas ni en el visor).
  if (CONFIG.CF_ANALYTICS_TOKEN && !CONFIG.EMBEDDED_VIEWER && location.hostname === new URL(CONFIG.SITE).hostname
      && !document.querySelector("script[data-cf-beacon]")) {
    const s = document.createElement("script");
    s.defer = true; s.src = "https://static.cloudflareinsights.com/beacon.min.js";
    s.setAttribute("data-cf-beacon", JSON.stringify({ token: CONFIG.CF_ANALYTICS_TOKEN }));
    document.head.appendChild(s);
  }

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

  const raw = {
    get(k, d) { try { const v = localStorage.getItem("qc:" + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem("qc:" + k, JSON.stringify(v)); return true; } catch (e) { return false; } },
    del(k) { try { localStorage.removeItem("qc:" + k); } catch (e) {} }
  };

  // ---- tu perfil: un solo objeto en este teléfono ("qc:yo") ----
  // pago: lo de "Hoy" · trabajo: lo de "Me toca" · futuro: lo de "Futuro". Los módulos siguen pidiendo "q", "perfil" y "state";
  // aquí se traducen a partes del perfil. Mientras no exista perfil (bienvenida sin terminar) nada de eso se guarda.
  const sumFijos = (l) => (l || []).reduce((s, f) => s + (+f.amt || 0), 0);
  const DEF = {
    pago: { freq: "quincenal", proximo: "", ingreso: 7000, fijos: [{ k: "renta", amt: 2000 }, { k: "luz", amt: 300 }, { k: "celular", amt: 300 }, { k: "transporte", amt: 400 }], ahorro: 500, configurado: false },
    trabajo: { sueldo: 15000, inicio: "", zona: "general", agDias: 15, prima: 25, configurado: false },
    futuro: { age: 28, retire: 65, monthly: 1500, saved: 10000, need: 15000, veh: "cetes", skin: 2, hair: "short" }
  };
  let yo = raw.get("yo", null);
  // Quien ya usaba Quincy con las llaves de antes no ve la bienvenida: sus datos pasan al perfil nuevo.
  if (!yo) {
    const q = raw.get("q"), p = raw.get("perfil"), st = raw.get("state");
    // La app de antes guardaba "q" y "state" en cada visita, así que con ellas basta para saber que ya la usaba.
    if (q || p || st) {
      yo = { v: 1, ejemplo: false, migrado: true,
        pago: Object.assign({}, DEF.pago, q || {}, { fijos: q ? [{ k: "fijos", amt: +q.fijos || 0 }] : DEF.pago.fijos }),
        trabajo: Object.assign({}, DEF.trabajo, p || {}),
        futuro: Object.assign({}, DEF.futuro, st || {}) };
      raw.set("yo", yo); ["q", "perfil", "state"].forEach(raw.del);
    }
  }
  const saveYo = () => { if (yo) { yo.actualizado = new Date().toISOString().slice(0, 10); raw.set("yo", yo); } };
  const store = {
    get(k, d) {
      if (k === "q") return yo ? Object.assign({}, yo.pago, { fijos: sumFijos(yo.pago.fijos) }) : d;
      if (k === "perfil") return yo ? Object.assign({}, yo.trabajo) : d;
      if (k === "state") return yo ? Object.assign({}, yo.futuro) : d;
      return raw.get(k, d);
    },
    set(k, v) {
      if (k === "q" || k === "perfil" || k === "state") {
        if (!yo) return false;
        if (k === "q") {
          const fijos = Math.max(0, +v.fijos || 0);
          yo.pago = Object.assign({}, yo.pago, v, { fijos: Math.abs(sumFijos(yo.pago.fijos) - fijos) < 0.5 ? yo.pago.fijos : [{ k: "fijos", amt: fijos }] });
        } else if (k === "perfil") yo.trabajo = Object.assign({}, yo.trabajo, v);
        else yo.futuro = Object.assign({}, yo.futuro, v);
        saveYo(); return true;
      }
      return raw.set(k, v);
    },
    del: raw.del
  };
  const perfil = {
    DEF, sumFijos,
    exists: () => !!yo,
    // Borra el perfil también de la memoria, para que nada lo vuelva a guardar antes de recargar.
    clear() { yo = null; raw.del("yo"); },
    get: () => yo,
    // Crea o reemplaza el perfil completo (bienvenida, ejemplo o respaldo).
    set(next) { yo = Object.assign({ v: 1 }, next); yo.pago = Object.assign({}, DEF.pago, yo.pago); yo.trabajo = Object.assign({}, DEF.trabajo, yo.trabajo); yo.futuro = Object.assign({}, DEF.futuro, yo.futuro); saveYo(); return yo; },
    update(part, values) { if (!yo) return; yo[part] = Object.assign({}, yo[part], values); if (part === "pago" || part === "trabajo") yo.ejemplo = false; saveYo(); },
    // Todo lo que Quincy guarda en este navegador, para el respaldo.
    dump() { const out = {}; try { Object.keys(localStorage).filter((k) => k.startsWith("qc:")).forEach((k) => { out[k.slice(3)] = JSON.parse(localStorage.getItem(k)); }); } catch (e) {} return out; },
    restore(data) {
      if (!data || typeof data !== "object" || !data.yo || !data.yo.pago) return false;
      try { Object.keys(localStorage).filter((k) => k.startsWith("qc:")).forEach((k) => localStorage.removeItem(k)); } catch (e) {}
      const KEYS = ["yo", "gastos", "aguantes", "allow", "check", "salida", "reto", "retoStats", "tandas", "tandaSel", "tandaYo", "view"];
      Object.entries(data).forEach(([k, v]) => { if (KEYS.includes(k)) raw.set(k, v); });
      return true;
    }
  };

  const state = Object.assign(
    Object.assign({}, DEF.futuro),
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
  // Pinta en `el` los referidos pedidos (solo los que existan), siempre con su aviso de comisión.
  function referidos(el, claves) {
    const list = (claves || Object.keys(CONFIG.REFERIDOS)).map((k) => CONFIG.REFERIDOS[k]).filter((r) => r && r.url);
    if (!el || !list.length) return;
    el.replaceChildren(...list.map((r) => {
      const d = document.createElement("div"), a = document.createElement("a"), n = document.createElement("small");
      a.className = "btn btn-sun btn-sm"; a.href = r.url; a.target = "_blank"; a.rel = "sponsored noopener"; a.textContent = r.nombre;
      n.className = "mut"; n.textContent = (r.nota ? r.nota + " · " : "") + "Enlace de referido: Quincy puede recibir una comisión";
      d.append(a, n); return d;
    }));
    el.hidden = false;
  }
  // Pequeño bus de eventos entre módulos.
  const bus = new EventTarget();
  const on = (n, f) => bus.addEventListener(n, (e) => f(e.detail));
  const emit = (n, d) => bus.dispatchEvent(new CustomEvent(n, { detail: d }));

  return {
    CONFIG, YEAR, INITIAL_SEARCH, RATES, VEH, state, save, store, perfil, $, fmt, short, clamp, reduced,
    realAnnual, monthlyReal, balanceAt, requiredMonthly, targetFor, yearsLeft, futureOf, futureOfRecurring, freedomDays,
    dayKey, keyToDate, addDays, rng, toast, buzz, confetti, copyText, nativeShare, download, shareURL, referidos, on, emit
  };
})());
