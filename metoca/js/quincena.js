// Me Toca · "Hoy": cuánto puedes gastar hoy para llegar a tu siguiente pago, gastos del día y "¿me alcanza?".
(function (FY) {
  const { $, fmt, store } = FY;
  const CATS = [["comida", "Comida"], ["transporte", "Transporte"], ["super", "Súper"], ["antojo", "Antojo"], ["casa", "Casa"], ["salud", "Salud"], ["otro", "Otro"]];
  const catName = (k) => (CATS.find((c) => c[0] === k) || CATS[CATS.length - 1])[1];

  const cfg = Object.assign({ freq: "quincenal", ingreso: 7000, fijos: 3000, ahorro: 500, configurado: false }, store.get("q", {}));
  const gastos = store.get("gastos", {});   // { "AAAA-MM-DD": [{ amt, cat }] }
  const aguantes = store.get("aguantes", {}); // { "AAAA-MM-DD": [{ amt, label }] }
  const allow = store.get("allow", {});     // { "AAAA-MM-DD": límite de ese día }
  const saveAll = () => { store.set("q", cfg); store.set("gastos", gastos); store.set("aguantes", aguantes); store.set("allow", allow); };
  let cat = "comida";

  // ---------- periodos de pago ----------
  const noon = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate(), 12);
  const lastDay = (y, m) => new Date(y, m + 1, 0).getDate();
  const diff = (a, b) => Math.round((noon(b) - noon(a)) / 864e5);
  function period(freq, today) {
    const t = noon(today), y = t.getFullYear(), m = t.getMonth(), d = t.getDate(), ld = lastDay(y, m);
    let start, next;
    if (freq === "semanal") {
      const back = (t.getDay() - 5 + 7) % 7; // pago en viernes
      start = new Date(y, m, d - back, 12); next = new Date(y, m, d - back + 7, 12);
    } else if (freq === "mensual") {
      if (d === ld) { start = t; next = new Date(y, m + 1, lastDay(y, m + 1), 12); }
      else { start = new Date(y, m, 0, 12); next = new Date(y, m, ld, 12); }
    } else {
      if (d === ld) { start = t; next = new Date(y, m + 1, 15, 12); }
      else if (d >= 15) { start = new Date(y, m, 15, 12); next = new Date(y, m, ld, 12); }
      else { start = new Date(y, m, 0, 12); next = new Date(y, m, 15, 12); }
    }
    return { start, next, daysLeft: Math.max(1, diff(t, next)), len: Math.max(1, diff(start, next)) };
  }
  const sum = (list) => (list || []).reduce((s, e) => s + (e.amt || 0), 0);
  const spentOn = (k) => sum(gastos[k]);
  function spentBetween(a, b) { // [a, b)
    let s = 0;
    for (let d = noon(a); d < noon(b); d = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1, 12)) s += spentOn(FY.dayKey(d));
    return s;
  }

  function snapshot(today = new Date()) {
    const p = period(cfg.freq, today);
    const available = Math.max(0, cfg.ingreso - cfg.fijos - cfg.ahorro);
    const before = spentBetween(p.start, today);
    const k = FY.dayKey(today);
    const limit = Math.max(0, (available - before) / p.daysLeft);
    const spent = spentOn(k);
    return { p, available, before, limit, spent, left: limit - spent, k, periodSpent: before + spent };
  }
  function streak(s) {
    let n = s.left >= 0 && (gastos[s.k] || allow[s.k] !== undefined) ? 1 : 0;
    let d = FY.addDays(new Date(), -1);
    while (true) {
      const k = FY.dayKey(d);
      if (allow[k] === undefined || spentOn(k) > allow[k] + 0.5) break;
      n++; d = FY.addDays(d, -1);
    }
    return n;
  }

  // ---------- render ----------
  const dateFmt = (d) => d.toLocaleDateString("es-MX", { weekday: "short", day: "numeric", month: "short" });
  function render() {
    const s = snapshot();
    allow[s.k] = s.limit; saveAll();
    const green = s.left >= 0;
    $("q-date").textContent = new Date().toLocaleDateString("es-MX", { weekday: "long", day: "numeric", month: "long" });
    $("q-example").hidden = cfg.configurado;
    $("q-big-label").textContent = green ? "Hoy todavía puedes gastar" : "Hoy te pasaste por";
    $("q-big").textContent = fmt(Math.abs(s.left));
    $("q-big").className = "q-big mono " + (green ? (s.left < s.limit * 0.25 ? "warn" : "ok") : "bad");
    const payTxt = s.p.daysLeft === 1 ? "Mañana es día de pago" : `Faltan ${s.p.daysLeft} días para tu pago (${dateFmt(s.p.next)})`;
    $("q-sub").textContent = `Tu límite de hoy es ${fmt(s.limit)} y llevas ${fmt(s.spent)}. ${payTxt}.`;
    const frac = s.limit > 0 ? Math.min(1, s.spent / s.limit) : (s.spent > 0 ? 1 : 0);
    const arc = $("q-ring-arc"), C = 2 * Math.PI * 52;
    arc.setAttribute("stroke-dasharray", `${C}`); arc.setAttribute("stroke-dashoffset", `${C * (1 - frac)}`);
    arc.setAttribute("class", "ring-arc " + (green ? (frac > 0.75 ? "warn" : "ok") : "bad"));
    // Lista de hoy
    const list = $("q-today-list"); list.innerHTML = "";
    (gastos[s.k] || []).forEach((g, i) => {
      const li = document.createElement("li");
      li.innerHTML = `<span>${catName(g.cat)}</span><b class="mono">${fmt(g.amt)}</b>`;
      const x = document.createElement("button");
      x.type = "button"; x.className = "x"; x.setAttribute("aria-label", `Borrar gasto de ${fmt(g.amt)}`); x.textContent = "×";
      x.addEventListener("click", () => { gastos[s.k].splice(i, 1); if (!gastos[s.k].length) delete gastos[s.k]; saveAll(); render(); });
      li.appendChild(x); list.appendChild(li);
    });
    $("q-today-empty").hidden = !!(gastos[s.k] && gastos[s.k].length);
    // Periodo
    const label = cfg.freq === "semanal" ? "semana" : cfg.freq === "mensual" ? "mes" : "quincena";
    $("q-period-title").textContent = `Tu ${label}: ${dateFmt(s.p.start)} → ${dateFmt(FY.addDays(s.p.next, -1))}`;
    const pf = s.available > 0 ? s.periodSpent / s.available : 0;
    $("q-period-bar").style.width = Math.min(100, pf * 100).toFixed(1) + "%";
    $("q-period-bar").className = pf > 1 ? "bad" : "";
    $("q-period-text").textContent = `Llevas ${fmt(s.periodSpent)} de ${fmt(s.available)} para gastar (${fmt(cfg.ingreso)} de pago, menos ${fmt(cfg.fijos)} fijos y ${fmt(cfg.ahorro)} de ahorro).`;
    const days = $("q-days"); days.innerHTML = "";
    for (let i = 0; i < s.p.len; i++) {
      const d = FY.addDays(s.p.start, i), k = FY.dayKey(d), el = document.createElement("i");
      if (k === s.k) el.className = "today " + (green ? "ok" : "bad");
      else if (noon(d) > noon(new Date())) el.className = "future";
      else if (allow[k] !== undefined) el.className = spentOn(k) <= allow[k] + 0.5 ? "ok" : "bad";
      el.title = `${dateFmt(d)}: ${fmt(spentOn(k))}`;
      days.appendChild(el);
    }
    // Por categoría
    const byCat = {};
    for (let d = noon(s.p.start); d <= noon(new Date()); d = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1, 12)) (gastos[FY.dayKey(d)] || []).forEach((g) => { byCat[g.cat] = (byCat[g.cat] || 0) + g.amt; });
    const max = Math.max(1, ...Object.values(byCat));
    $("q-cat-bars").innerHTML = Object.keys(byCat).length
      ? Object.entries(byCat).sort((a, b) => b[1] - a[1]).map(([c, v]) => `<div><span>${catName(c)}</span><i style="width:${(v / max * 100).toFixed(1)}%"></i><b class="mono">${fmt(v)}</b></div>`).join("")
      : `<p class="mut small">Aquí verás en qué se te va el dinero cuando registres tus gastos.</p>`;
    // Aguantes
    let ag = 0;
    for (let d = noon(s.p.start); d <= noon(new Date()); d = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1, 12)) ag += sum(aguantes[FY.dayKey(d)]);
    $("q-aguante").innerHTML = ag > 0 ? `Esta ${label} te aguantaste <b class="tide">${fmt(ag)}</b>. Invertido, a tus ${FY.state.retire} vale <b class="sun">${fmt(FY.futureOf(ag))}</b>.` : "Cuando te aguantes un antojo, aquí se junta lo que te ahorraste.";
    // Racha
    const n = streak(s);
    $("streak-num").textContent = n;
    $("streak-pill").classList.toggle("lit", n > 0 && green);
    document.querySelectorAll('[data-dot="hoy"]').forEach((d) => { d.hidden = !!gastos[s.k]; });
    alcanza();
    FY.emit("hoy", { streak: n, aguante: ag, left: s.left, limit: s.limit });
  }

  // ---------- registrar gasto ----------
  const cats = $("q-cats");
  CATS.forEach(([k, name]) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip-btn"; b.textContent = name; b.setAttribute("aria-pressed", k === cat);
    b.addEventListener("click", () => { cat = k; cats.querySelectorAll(".chip-btn").forEach((x) => x.setAttribute("aria-pressed", x === b)); });
    cats.appendChild(b);
  });
  function addGasto(amt, c) {
    amt = Math.round(+amt * 100) / 100;
    if (!(amt > 0 && amt <= 1e6)) { FY.toast("Escribe un monto entre $1 y $1,000,000."); return false; }
    const k = FY.dayKey();
    (gastos[k] = gastos[k] || []).push({ amt, cat: c || cat });
    saveAll(); FY.buzz(10); render();
    const s = snapshot();
    FY.toast(s.left >= 0 ? `Listo. Te quedan ${fmt(s.left)} para hoy.` : `Te pasaste ${fmt(-s.left)} hoy. Mañana se ajusta tu límite.`);
    return true;
  }
  $("q-add").addEventListener("click", () => { if (addGasto($("q-amount").value)) $("q-amount").value = ""; });
  $("q-amount").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); $("q-add").click(); } });

  // ---------- ¿me alcanza? ----------
  function alcanza() {
    const price = Math.max(0, +$("alc-price").value || 0);
    const s = snapshot();
    const out = $("alc-out");
    if (!price) { out.innerHTML = "Escribe el precio de lo que quieres comprar."; $("alc-future").textContent = ""; return; }
    if (price <= s.left) out.innerHTML = `<b class="ok-t">Sí te alcanza.</b> Te quedarían ${fmt(s.left - price)} para hoy.`;
    else {
      const after = Math.max(0, (s.available - s.periodSpent - price) / Math.max(1, s.p.daysLeft - 1));
      out.innerHTML = s.p.daysLeft > 1
        ? `<b class="bad-t">Hoy no te alcanza.</b> Si lo compras, tu límite de los próximos ${s.p.daysLeft - 1} días baja a ${fmt(after)} diarios.`
        : `<b class="bad-t">Hoy no te alcanza.</b> Mañana es día de pago: espérate un día.`;
    }
    $("alc-future").innerHTML = `Si no lo compras y lo inviertes, a tus ${FY.state.retire} valdría <b class="sun">${fmt(FY.futureOf(price))}</b>.`;
  }
  $("alc-price").addEventListener("input", alcanza);
  $("alc-buy").addEventListener("click", () => { const p = +$("alc-price").value; if (addGasto(p, "antojo")) $("alc-price").value = ""; alcanza(); });
  $("alc-save").addEventListener("click", () => {
    const p = Math.round(+$("alc-price").value);
    if (!(p > 0)) { FY.toast("Escribe el precio primero."); return; }
    const k = FY.dayKey();
    (aguantes[k] = aguantes[k] || []).push({ amt: p, label: "Antojo" });
    saveAll(); FY.confetti(); FY.buzz([10, 40, 10]);
    FY.toast(`Bien. Esos ${fmt(p)} valen ${fmt(FY.futureOf(p))} a tus ${FY.state.retire}.`);
    $("alc-price").value = ""; render();
  });

  // ---------- tus números ----------
  const fields = { "q-freq": "freq", "q-income": "ingreso", "q-fixed": "fijos", "q-saving": "ahorro" };
  Object.entries(fields).forEach(([id, key]) => {
    const el = $(id);
    el.value = cfg[key];
    el.addEventListener("input", () => {
      cfg[key] = key === "freq" ? el.value : Math.max(0, Math.min(1e7, +el.value || 0));
      cfg.configurado = true; saveAll(); render();
    });
  });
  $("q-setup").open = !cfg.configurado;

  // ---------- recordatorios ----------
  function reminders() {
    const t = FY.addDays(new Date(), 1);
    const ymd = `${t.getFullYear()}${String(t.getMonth() + 1).padStart(2, "0")}${String(t.getDate()).padStart(2, "0")}`;
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "America/Mexico_City";
    const text = "Me Toca: registra tus gastos de hoy";
    const details = `Un minuto para saber cuánto te queda: ${FY.CONFIG.SITE}app.html?ref=recordatorio`;
    $("remind-google").href = "https://calendar.google.com/calendar/render?action=TEMPLATE" +
      `&text=${encodeURIComponent(text)}&details=${encodeURIComponent(details)}&dates=${ymd}T210000/${ymd}T210500&ctz=${encodeURIComponent(tz)}&recur=${encodeURIComponent("RRULE:FREQ=DAILY")}`;
    return { ymd, text, details };
  }
  $("remind-ics").addEventListener("click", () => {
    const { ymd, text, details } = reminders();
    const ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Me Toca//ES", "BEGIN:VEVENT", `UID:metoca-${Date.now()}@metoca`, `DTSTAMP:${new Date().toISOString().replace(/[-:]/g, "").slice(0, 15)}Z`,
      `DTSTART:${ymd}T210000`, `DTEND:${ymd}T210500`, "RRULE:FREQ=DAILY", `SUMMARY:${text}`, `DESCRIPTION:${details}`,
      "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:PT0M", `DESCRIPTION:${text}`, "END:VALARM", "END:VEVENT", "END:VCALENDAR"].join("\r\n");
    FY.download(new Blob([ics], { type: "text/calendar" }), "me-toca-recordatorio.ics");
  });
  if (FY.CONFIG.EMBEDDED_VIEWER) $("remind-ics").hidden = true;

  function wipe() { [gastos, aguantes, allow].forEach((o) => Object.keys(o).forEach((k) => delete o[k])); }
  function init() { reminders(); render(); }
  FY.quincena = { init, render, period, snapshot, nextPayday: () => period(cfg.freq, new Date()).next, cfg, summary: () => { const s = snapshot(); return { streak: streak(s), left: s.left, limit: s.limit }; }, wipe };
})(window.FY);
