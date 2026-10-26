// Futuro Yo · "Hoy": racha diaria, registro rápido, antojómetro, casa del yo del futuro, misiones.
(function (FY) {
  const { $, fmt, short, store } = FY;
  const log = store.get("log", {});           // { "AAAA-MM-DD": [{ k, amt, fut, label }] }
  const meta = Object.assign({ shields: 0, used: [], best: 0, awarded: "" }, store.get("streak", {}));
  const saveAll = () => { store.set("log", log); store.set("streak", meta); };

  const today = () => FY.dayKey();
  const active = (k) => (log[k] && log[k].length > 0) || meta.used.includes(k);
  const prevKey = (k, n = 1) => FY.dayKey(FY.addDays(FY.keyToDate(k), -n));

  // Si ayer (o antier) no hubo registro, un escudo salva la racha.
  function applyShields() {
    const t = today();
    let gap = [], k = prevKey(t);
    while (!active(k) && gap.length <= meta.shields) { gap.push(k); k = prevKey(k); }
    if (gap.length && gap.length <= meta.shields && active(k)) {
      meta.used.push(...gap); meta.shields -= gap.length;
      FY.toast(gap.length === 1 ? "Un escudo salvó tu racha de ayer." : `${gap.length} escudos salvaron tu racha.`);
      saveAll();
    }
  }
  function streak() {
    let k = today(), n = 0;
    if (!active(k)) k = prevKey(k);
    while (active(k)) { n++; k = prevKey(k); }
    return n;
  }
  function totals() {
    let amt = 0, fut = 0;
    Object.values(log).forEach((list) => list.forEach((e) => { amt += e.amt || 0; fut += e.fut || 0; }));
    return { amt, fut };
  }
  function summary() { const t = totals(); return { streak: streak(), future: t.fut, amount: t.amt, best: Math.max(meta.best, streak()), level: levelOf(t.fut) }; }

  function add(entry) {
    const t = today();
    const wasActive = active(t);
    (log[t] = log[t] || []).push(entry);
    const s = streak();
    meta.best = Math.max(meta.best, s);
    if (s > 0 && s % 7 === 0 && meta.awarded !== t && meta.shields < 2) {
      meta.shields++; meta.awarded = t;
      setTimeout(() => FY.toast(`${s} días seguidos. Ganaste un escudo de racha.`), 900);
    }
    saveAll();
    if (!wasActive) { FY.confetti(); FY.buzz([15, 50, 25]); $("flame").classList.add("pop"); setTimeout(() => $("flame").classList.remove("pop"), 500); }
    render();
    FY.emit("habit", entry);
  }

  // ---------- niveles: dónde vive tu yo del futuro ----------
  const LEVELS = [
    { min: 0, name: "Cuarto rentado" }, { min: 5000, name: "Depa con balcón" }, { min: 25000, name: "Casita propia" },
    { min: 75000, name: "Casa con jardín" }, { min: 200000, name: "Casa con alberca" }, { min: 500000, name: "Casa frente al mar" },
    { min: 1000000, name: "Vuelta al mundo" }
  ];
  function levelOf(fut) { let i = 0; LEVELS.forEach((l, k) => { if (fut >= l.min) i = k; }); return i; }
  function sceneSVG(lv) {
    const sky = lv >= 5 ? ["#2b3f7a", "#ff9a62"] : ["#0e2a3a", "#1d4a5e"];
    let s = `<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${sky[0]}"/><stop offset="1" stop-color="${sky[1]}"/></linearGradient></defs>
      <rect width="320" height="170" fill="url(#sky)"/>
      <circle cx="${lv >= 5 ? 160 : 268}" cy="${lv >= 5 ? 112 : 38}" r="${lv >= 5 ? 26 : 14}" fill="#ffb547" opacity=".95"/>`;
    if (lv >= 5) s += `<rect y="112" width="320" height="58" fill="#1a6d84"/><path d="M0 120h320M20 132h90M180 128h110M60 146h200" stroke="#ffd8a8" stroke-opacity=".5" stroke-width="2"/><rect y="150" width="320" height="20" fill="#e9c98f"/>`;
    else s += `<rect y="138" width="320" height="32" fill="#16323f"/>`;
    const ground = lv >= 5 ? 150 : 138;
    if (lv === 0) s += `<rect x="30" y="40" width="120" height="98" fill="#20404f"/><rect x="170" y="62" width="110" height="76" fill="#1b3644"/>` +
      [0, 1, 2].map((r) => [0, 1, 2].map((c) => `<rect x="${42 + c * 36}" y="${52 + r * 28}" width="18" height="16" fill="${r === 2 && c === 1 ? "#ffb547" : "#2c5468"}"/>`).join("")).join("");
    if (lv === 1) s += `<rect x="90" y="30" width="140" height="108" fill="#2a4f60"/>` +
      [0, 1, 2].map((r) => [0, 1, 2].map((c) => `<rect x="${104 + c * 42}" y="${42 + r * 30}" width="22" height="18" fill="${r === 1 && c === 2 ? "#ffb547" : "#3b6a7d"}"/>`).join("")).join("") +
      `<rect x="186" y="78" width="40" height="5" fill="#5ad6c8"/><path d="M190 78v-9M200 78v-9M210 78v-9M220 78v-9" stroke="#5ad6c8" stroke-width="2"/>`;
    if (lv >= 2) {
      const hx = lv >= 5 ? 196 : 104, w = lv >= 4 ? 120 : 96;
      s += `<rect x="${hx}" y="${ground - 56}" width="${w}" height="56" fill="#f1e3c8"/><path d="M${hx - 10} ${ground - 54}L${hx + w / 2} ${ground - 92}L${hx + w + 10} ${ground - 54}Z" fill="#d0643b"/>
        <rect x="${hx + 14}" y="${ground - 40}" width="20" height="16" fill="#ffb547"/><rect x="${hx + w - 34}" y="${ground - 40}" width="20" height="16" fill="#ffb547"/><rect x="${hx + w / 2 - 9}" y="${ground - 30}" width="18" height="30" fill="#7a4a2a"/>`;
    }
    if (lv >= 3) s += `<rect x="${lv >= 5 ? 20 : 34}" y="${ground - 44}" width="8" height="44" fill="#6b4329"/><circle cx="${lv >= 5 ? 24 : 38}" cy="${ground - 52}" r="22" fill="#3f9b6e"/>` +
      (lv < 5 ? `<path d="M230 ${ground}v-14M244 ${ground}v-14M258 ${ground}v-14M272 ${ground}v-14M286 ${ground}v-14M224 ${ground - 8}h68" stroke="#e9e1cf" stroke-width="3"/>` : "");
    if (lv === 4) s += `<rect x="236" y="${ground + 6}" width="70" height="20" rx="6" fill="#5ad6c8"/>`;
    if (lv >= 5) s += `<path d="M120 150c4-30 8-44 2-70" stroke="#6b4329" stroke-width="5" fill="none"/><path d="M122 80c-20-8-34 0-40 8M122 80c18-10 32-4 38 4M122 80c-4-16-16-22-26-22M122 80c8-14 20-16 28-14" stroke="#3f9b6e" stroke-width="6" fill="none" stroke-linecap="round"/>`;
    if (lv >= 6) s += `<path d="M30 40l40 8 26-14 8 4-18 16 26 6 8-5 6 3-10 10-34-4-24 10-6-4 14-12-34-8z" fill="#eaf3f4"/>`;
    return s;
  }

  // ---------- render ----------
  function render() {
    const s = streak(), t = totals(), lit = active(today());
    $("streak-num").textContent = s;
    $("streak-pill").classList.toggle("lit", lit);
    $("streak-big").textContent = s;
    $("streak-label").textContent = s === 1 ? "día seguido" : "días seguidos";
    $("flame").classList.toggle("lit", lit);
    $("shields").textContent = `${meta.shields} ${meta.shields === 1 ? "escudo" : "escudos"}`;
    $("best-streak").textContent = Math.max(meta.best, s);
    $("checkin-status").textContent = lit ? "Listo por hoy. Tu racha está a salvo. Puedes sumar más." : s > 0 ? `Registra algo hoy para no perder tus ${s} días.` : "Un toque empieza tu racha.";
    const todays = log[today()] || [];
    document.querySelectorAll(".quick-btn").forEach((b) => {
      const k = b.dataset.quick || "reto";
      b.classList.toggle("done", todays.some((e) => e.k === k));
    });
    $("tot-today").textContent = fmt(t.amt);
    $("tot-future").textContent = fmt(t.fut);
    $("tot-age").textContent = FY.state.retire;
    $("tot-days").textContent = Math.round(FY.freedomDays(t.fut)).toLocaleString("es-MX");
    const lv = levelOf(t.fut), next = LEVELS[lv + 1];
    $("world-svg").innerHTML = sceneSVG(lv);
    $("level-chip").textContent = `Nivel ${lv + 1}`;
    $("level-name").textContent = LEVELS[lv].name;
    $("level-next").textContent = next ? `Te faltan ${fmt(next.min - t.fut)} de futuro para "${next.name}"` : "Llegaste al nivel máximo";
    $("level-bar").style.width = next ? ((t.fut - LEVELS[lv].min) / (next.min - LEVELS[lv].min) * 100).toFixed(1) + "%" : "100%";
    // Mapa de calor
    const heat = $("heat"); heat.innerHTML = "";
    const tk = today(); let count = 0;
    for (let i = 34; i >= 0; i--) {
      const k = FY.dayKey(FY.addDays(new Date(), -i));
      const el = document.createElement("i");
      if (log[k] && log[k].length) { el.className = "on"; count++; } else if (meta.used.includes(k)) el.className = "shield-day";
      if (k === tk) el.classList.add("today");
      el.title = k;
      heat.appendChild(el);
    }
    $("heat-count").textContent = `${count} ${count === 1 ? "día activo" : "días activos"}`;
    $("today-date").textContent = new Date().toLocaleDateString("es-MX", { weekday: "long", day: "numeric", month: "long" });
    quincena();
    document.querySelectorAll('[data-dot="hoy"]').forEach((d) => { d.hidden = lit; });
  }
  function quincena() {
    const d = new Date(), day = d.getDate(), lastDay = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
    const el = $("quincena");
    if (day === 15 || day === lastDay) { el.innerHTML = "<b>Hoy es quincena.</b> Págate primero: aparta tu ahorro antes de gastar y regístralo aquí."; return; }
    const next = day < 15 ? 15 : lastDay, n = next - day;
    el.innerHTML = `Faltan <b>${n} ${n === 1 ? "día" : "días"}</b> para la quincena. Decide desde hoy cuánto le vas a mandar a tu yo del futuro.`;
  }

  // ---------- registro rápido ----------
  const AMOUNTS = [50, 100, 200, 500, 1000];
  const chips = $("amount-chips");
  AMOUNTS.forEach((a) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip-btn"; b.textContent = fmt(a);
    b.addEventListener("click", () => saveAmount(a));
    chips.appendChild(b);
  });
  function saveAmount(a) {
    a = Math.round(+a);
    if (!(a > 0 && a <= 1e6)) { FY.toast("Escribe una cantidad entre $1 y $1,000,000."); return; }
    add({ k: "ahorro", amt: a, fut: FY.futureOf(a), label: "Ahorro" });
    $("amount-box").hidden = true; $("amount-input").value = "";
    FY.toast(`Le mandaste ${fmt(FY.futureOf(a))} a tu yo de ${FY.state.retire}.`);
  }
  document.querySelector('[data-quick="ahorro"]').addEventListener("click", () => { const box = $("amount-box"); box.hidden = !box.hidden; if (!box.hidden) $("amount-input").focus({ preventScroll: true }); });
  document.querySelector('[data-quick="antojo"]').addEventListener("click", () => { $("antojometro").scrollIntoView({ behavior: FY.reduced ? "auto" : "smooth", block: "start" }); $("antojo-price").focus({ preventScroll: true }); });
  $("amount-save").addEventListener("click", () => saveAmount($("amount-input").value));
  $("amount-input").addEventListener("keydown", (e) => { if (e.key === "Enter") saveAmount($("amount-input").value); });

  // ---------- antojómetro ----------
  const ANTOJOS = [
    { n: "Tacos", p: 120, f: "week" }, { n: "Café de cafetería", p: 75, f: "day" }, { n: "Comida a domicilio", p: 250, f: "week" },
    { n: "Cervezas con los cuates", p: 300, f: "week" }, { n: "Streaming", p: 199, f: "month" }, { n: "Tenis nuevos", p: 1800, f: "once" },
    { n: "Concierto", p: 2500, f: "once" }, { n: "Celular nuevo", p: 15000, f: "once" }
  ];
  const FREQ = { once: "una vez", day: "diario", week: "cada semana", month: "cada mes" };
  let antojoName = ANTOJOS[0].n;
  const ac = $("antojo-chips");
  ANTOJOS.forEach((a, i) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip-btn"; b.setAttribute("aria-pressed", i === 0);
    b.innerHTML = `${a.n}<small>${fmt(a.p)}</small>`;
    b.addEventListener("click", () => {
      antojoName = a.n; $("antojo-price").value = a.p; $("antojo-freq").value = a.f;
      ac.querySelectorAll(".chip-btn").forEach((x) => x.setAttribute("aria-pressed", x === b));
      antojo(); FY.buzz(6);
    });
    ac.appendChild(b);
  });
  function antojoValues() {
    const price = Math.max(0, +$("antojo-price").value || 0), f = $("antojo-freq").value;
    const fut = f === "once" ? FY.futureOf(price) : FY.futureOfRecurring(price, f);
    return { price, f, fut, days: FY.freedomDays(fut) };
  }
  function antojo() {
    const v = antojoValues();
    $("antojo-what").textContent = `${antojoName} ${FREQ[v.f]} (${fmt(v.price)}), invertido en CETES hasta tus ${FY.state.retire}:`;
    $("antojo-future").textContent = fmt(v.fut);
    const d = Math.round(v.days);
    $("antojo-days").innerHTML = d >= 1 ? `Eso paga <b class="tide">${d.toLocaleString("es-MX")} ${d === 1 ? "día" : "días"}</b> de tu retiro, con lo que quieres recibir al mes.` : "Menos de un día de tu retiro. Disfrútalo sin culpa.";
  }
  ["antojo-price", "antojo-freq"].forEach((id) => $(id).addEventListener("input", () => { if (id === "antojo-price") { antojoName = "Tu antojo"; ac.querySelectorAll(".chip-btn").forEach((x) => x.setAttribute("aria-pressed", "false")); } antojo(); }));
  $("antojo-save").addEventListener("click", () => {
    const v = antojoValues();
    if (!(v.price > 0)) { FY.toast("Escribe el precio del antojo."); return; }
    add({ k: "antojo", amt: v.price, fut: FY.futureOf(v.price), label: antojoName });
    FY.toast(`Bien. Esos ${fmt(v.price)} valen ${fmt(FY.futureOf(v.price))} a tus ${FY.state.retire}.`);
  });
  $("antojo-buy").addEventListener("click", () => FY.toast("Disfrútalo. Tu yo del futuro también quiere que vivas hoy."));

  // ---------- recordatorios ----------
  function reminderLinks() {
    const t = FY.addDays(new Date(), 1);
    const ymd = `${t.getFullYear()}${String(t.getMonth() + 1).padStart(2, "0")}${String(t.getDate()).padStart(2, "0")}`;
    const tz = (Intl.DateTimeFormat().resolvedOptions().timeZone) || "America/Mexico_City";
    const text = "Futuro Yo: ¿qué hiciste hoy por tu yo del futuro?";
    const details = `Un toque para mantener tu racha: ${FY.shareURL({ ref: "recordatorio" })}`;
    $("remind-google").href = "https://calendar.google.com/calendar/render?action=TEMPLATE" +
      `&text=${encodeURIComponent(text)}&details=${encodeURIComponent(details)}&dates=${ymd}T210000/${ymd}T210500&ctz=${encodeURIComponent(tz)}&recur=${encodeURIComponent("RRULE:FREQ=DAILY")}`;
    return { ymd, text, details };
  }
  $("remind-ics").addEventListener("click", () => {
    const { ymd, text, details } = reminderLinks();
    const ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Futuro Yo//ES", "BEGIN:VEVENT", `UID:futuroyo-${Date.now()}@futuroyo`, `DTSTAMP:${new Date().toISOString().replace(/[-:]/g, "").slice(0, 15)}Z`,
      `DTSTART:${ymd}T210000`, `DTEND:${ymd}T210500`, "RRULE:FREQ=DAILY", `SUMMARY:${text}`, `DESCRIPTION:${details}`,
      "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:PT0M", `DESCRIPTION:${text}`, "END:VALARM", "END:VEVENT", "END:VCALENDAR"].join("\r\n");
    FY.download(new Blob([ics], { type: "text/calendar" }), "futuro-yo-recordatorio.ics");
  });
  if (FY.CONFIG.EMBEDDED_VIEWER) $("remind-ics").hidden = true;

  // ---------- misiones ----------
  const MISSIONS = [
    { id: "afore", t: "Encuentra tu Afore", d: "Descarga AforeMóvil (CONSAR) y mira cuánto llevas.", xp: 100, url: "https://www.gob.mx/consar" },
    { id: "cetes", t: "Abre tu cuenta de CETES", d: "Desde $100 en CetesDirecto, sin comisiones.", xp: 150, url: "https://www.cetesdirecto.com" },
    { id: "auto", t: "Automatiza tu ahorro", d: "Programa un traspaso el día de quincena. Lo que no ves, no lo gastas.", xp: 150 },
    { id: "fondo", t: "Arma tu fondo de emergencia", d: "Meta: 3 meses de gastos en un lugar seguro y disponible.", xp: 100 },
    { id: "deuda", t: "Liquida la tarjeta más cara", d: "Revisa el CAT de cada tarjeta y ataca primero la de mayor costo.", xp: 100, url: "https://www.condusef.gob.mx" },
    { id: "volunt", t: "Haz una aportación voluntaria", d: "Aunque sean $100 a tu Afore. Solo 7.9% lo hace.", xp: 100 },
    { id: "carta", t: "Comparte tu tarjeta", d: "Mándala a alguien a quien quieras ver bien a los 65.", xp: 50 },
    { id: "revisa", t: "Pon una cita contigo", d: "Agenda revisar este plan cada 6 meses.", xp: 50 }
  ];
  const done = new Set(store.get("missions", []));
  const ml = $("mission-list");
  MISSIONS.forEach((m) => {
    const el = document.createElement("label");
    el.className = "mission";
    el.innerHTML = `<input type="checkbox" id="m-${m.id}"><div><b>${m.t}</b><p>${m.d}${m.url ? ` <a href="${m.url}" target="_blank" rel="noopener">Ir</a>` : ""}</p><em>+${m.xp} XP</em></div>`;
    const cb = el.querySelector("input");
    cb.checked = done.has(m.id);
    cb.addEventListener("change", () => setMission(m.id, cb.checked, true));
    ml.appendChild(el);
  });
  function setMission(id, on, byHand) {
    const m = MISSIONS.find((x) => x.id === id);
    if (!m || done.has(id) === on) return;
    on ? done.add(id) : done.delete(id);
    store.set("missions", [...done]);
    const cb = $("m-" + id); if (cb) cb.checked = on;
    xp();
    if (on) { add({ k: "mision", amt: 0, fut: 0, label: m.t }); if (byHand) FY.toast(`+${m.xp} XP. Tu yo del futuro lo notó.`); }
  }
  function xp() {
    const total = MISSIONS.reduce((s, m) => s + m.xp, 0);
    const got = MISSIONS.filter((m) => done.has(m.id)).reduce((s, m) => s + m.xp, 0);
    $("xp-label").textContent = `${got} / ${total} XP`;
    $("xp-bar").style.width = (got / total * 100) + "%";
    $("xp-rank").textContent = "Rango: " + (got >= total ? "Arquitecto del tiempo" : got >= 500 ? "Navegante" : got >= 200 ? "Explorador" : "Viajero novato");
  }

  FY.on("reto-done", () => { if (!(log[today()] || []).some((e) => e.k === "reto")) add({ k: "reto", amt: 0, fut: 0, label: "Reto diario" }); });
  FY.on("shared", () => setMission("carta", true, false));
  FY.on("plan", () => { if (!$("v-hoy").hidden) { render(); antojo(); } });

  function wipe() { Object.keys(log).forEach((k) => delete log[k]); meta.shields = 0; meta.used = []; meta.best = 0; meta.awarded = ""; done.clear(); }
  function init() { applyShields(); render(); antojo(); xp(); reminderLinks(); }
  FY.habits = { init, render, summary, levelOf, LEVELS, sceneSVG, wipe, refresh: () => { render(); antojo(); } };
})(window.FY);
