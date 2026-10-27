// Quincy · Tandas: organiza una tanda, sortea los turnos con una ruleta, compártela por WhatsApp
// y descubre qué número te conviene comparado con invertir en CETES.
(function (FY) {
  const { $, fmt, store } = FY;
  const FREQ = { semanal: "cada semana", quincenal: "cada quincena (15 y fin de mes)", mensual: "cada mes" };
  const MAX = 30;

  // ---------- fechas de pago ----------
  const noon = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate(), 12);
  const lastDay = (y, m) => new Date(y, m + 1, 0).getDate();
  function nextPayday(d) { // 15 o último día del mes, igual o después de d
    const y = d.getFullYear(), m = d.getMonth(), day = d.getDate(), ld = lastDay(y, m);
    if (day <= 15) return new Date(y, m, 15, 12);
    if (day <= ld) return new Date(y, m, ld, 12);
    return new Date(y, m + 1, 15, 12);
  }
  function dates(freq, startISO, n) {
    const [y, m, d] = startISO.split("-").map(Number);
    let cur = noon(new Date(y, m - 1, d));
    const out = [];
    if (freq === "quincenal") cur = nextPayday(cur);
    for (let i = 0; i < n; i++) {
      out.push(cur);
      if (freq === "semanal") cur = new Date(cur.getFullYear(), cur.getMonth(), cur.getDate() + 7, 12);
      else if (freq === "mensual") { const t = new Date(y, m - 1 + i + 1, 1, 12); cur = new Date(t.getFullYear(), t.getMonth(), Math.min(d, lastDay(t.getFullYear(), t.getMonth())), 12); }
      else cur = nextPayday(new Date(cur.getFullYear(), cur.getMonth(), cur.getDate() + 1, 12));
    }
    return out;
  }
  // Tasa de CETES por periodo de la tanda (nominal).
  function periodRate(freq) {
    const annual = FY.RATES.cetes / 100;
    const per = freq === "semanal" ? 52 : freq === "quincenal" ? 24 : 12;
    return Math.pow(1 + annual, 1 / per) - 1;
  }
  // Ganancia o pérdida de recibir en el turno k (1..n) frente a invertir cada aportación en CETES,
  // medida al final de la tanda. Positivo: te conviene; negativo: te cuesta.
  function turnValue(n, amount, k, r) {
    const pot = n * amount;
    const receive = pot * Math.pow(1 + r, n - k);
    let paid = 0;
    for (let j = 1; j <= n; j++) paid += amount * Math.pow(1 + r, n - j);
    return receive - paid;
  }

  // ---------- enlace para compartir ----------
  const b64u = (s) => btoa(unescape(encodeURIComponent(s))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  const unb64u = (s) => decodeURIComponent(escape(atob(s.replace(/-/g, "+").replace(/_/g, "/"))));
  function encode(t) { return b64u(JSON.stringify({ v: 1, n: t.nombre, a: t.monto, f: t.freq, s: t.inicio, p: t.personas })); }
  function decode(code) {
    try {
      const o = JSON.parse(unb64u(code));
      const clean = (x, l) => String(x || "").replace(/[<>]/g, "").trim().slice(0, l);
      if (!o || !Array.isArray(o.p) || o.p.length < 2 || o.p.length > MAX) return null;
      if (!FREQ[o.f] || !/^\d{4}-\d{2}-\d{2}$/.test(o.s) || !(o.a > 0 && o.a <= 1e6)) return null;
      return { nombre: clean(o.n, 40) || "Tanda", monto: Math.round(o.a), freq: o.f, inicio: o.s, personas: o.p.map((x) => clean(x, 24)).filter(Boolean), sorteada: true };
    } catch (e) { return null; }
  }
  const link = (t) => `${FY.CONFIG.SITE}app.html?t=${encode(t)}#tanda`;

  // ---------- estado ----------
  const today = new Date();
  const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const ejemplo = { nombre: "Tanda de la oficina", monto: 1000, freq: "quincenal", inicio: iso(today), personas: ["Ana", "Beto", "Caro", "Dani", "Eli", "Fer", "Gaby", "Hugo", "Iván", "Juli"], sorteada: false, ejemplo: true };
  let lista = store.get("tandas", []);
  let cur = Math.min(store.get("tandaSel", 0), Math.max(0, lista.length - 1));
  let yo = store.get("tandaYo", {});
  const saveAll = () => { store.set("tandas", lista); store.set("tandaSel", cur); store.set("tandaYo", yo); };
  const t = () => lista[cur] || ejemplo;

  function importFromURL() {
    const code = new URLSearchParams(FY.INITIAL_SEARCH || "").get("t");
    if (!code) return false;
    const got = decode(code);
    if (!got) { FY.toast("El enlace de la tanda no es válido."); return false; }
    const same = lista.findIndex((x) => encode(x) === encode(got));
    if (same >= 0) cur = same; else { lista.push(got); cur = lista.length - 1; }
    saveAll();
    return true;
  }

  // ---------- render ----------
  const dateFmt = (d) => d.toLocaleDateString("es-MX", { weekday: "short", day: "numeric", month: "short", year: "numeric" });
  function render() {
    const T = t(), n = T.personas.length, ds = dates(T.freq, T.inicio, n), r = periodRate(T.freq);
    $("tn-example").hidden = !T.ejemplo;
    $("tn-name").value = T.nombre; $("tn-amount").value = T.monto; $("tn-freq").value = T.freq; $("tn-start").value = T.inicio;
    $("tn-people").value = T.personas.join("\n");
    $("tn-pick").hidden = lista.length < 2;
    $("tn-pick").innerHTML = lista.map((x, i) => `<option value="${i}"${i === cur ? " selected" : ""}>${x.nombre.replace(/</g, "")}</option>`).join("");
    const pot = n * T.monto;
    $("tn-summary").innerHTML = `${n} personas ponen <b>${fmt(T.monto)}</b> ${FREQ[T.freq]}. Cada turno alguien recibe <b class="sun">${fmt(pot)}</b>. Termina el <b>${dateFmt(ds[n - 1])}</b>.`;
    // ¿quién eres?
    const key = encode(T), me = yo[key];
    $("tn-me").innerHTML = `<option value="">¿Quién eres tú?</option>` + T.personas.map((p, i) => `<option value="${i}"${String(me) === String(i) ? " selected" : ""}>${p.replace(/</g, "")}</option>`).join("");
    const meBox = $("tn-mine");
    if (me !== undefined && me !== "" && T.personas[me] !== undefined) {
      const k = +me, d = ds[k], left = FY.ley.diffDays(today, d), v = turnValue(n, T.monto, k + 1, r);
      meBox.hidden = false;
      meBox.innerHTML = `<p class="eyebrow">Tu turno</p><b class="tn-big">${left > 0 ? `Te toca en ${left} ${left === 1 ? "día" : "días"}` : left === 0 ? "¡Hoy te toca!" : "Ya te tocó"}</b>
        <p>Recibes <b class="sun">${fmt(pot)}</b> el <b>${dateFmt(d)}</b> (turno ${k + 1} de ${n}).</p>
        <p class="small ${v >= 0 ? "ok-t" : "bad-t"}">${v >= 0 ? `Tu número te conviene: es como un préstamo sin intereses que vale unos ${fmt(v)}.` : `Tu número te cuesta unos ${fmt(-v)} comparado con invertir tus aportaciones en CETES.`}</p>`;
      $("tn-cal").href = calLink(`Me toca la tanda: ${fmt(pot)}`, d, `Turno ${k + 1} de ${n} en "${T.nombre}". ${link(T)}`);
      $("tn-cal").hidden = false;
    } else { meBox.hidden = true; $("tn-cal").hidden = true; }
    $("tn-pay-cal").href = payCal(T, ds);
    // Calendario de turnos
    $("tn-table").innerHTML = T.personas.map((p, i) => {
      const v = turnValue(n, T.monto, i + 1, r), left = FY.ley.diffDays(today, ds[i]);
      return `<tr class="${String(me) === String(i) ? "me" : ""}${left < 0 ? " past" : ""}"><td class="mono">${i + 1}</td><td>${p.replace(/</g, "")}</td><td>${dateFmt(ds[i])}</td><td class="mono ${v >= 0 ? "ok-t" : "bad-t"}">${v >= 0 ? "+" : "−"}${fmt(Math.abs(v))}</td></tr>`;
    }).join("");
    // Gráfica de ganancia por turno
    const vals = T.personas.map((_, i) => turnValue(n, T.monto, i + 1, r));
    const max = Math.max(1, ...vals.map(Math.abs)), W = 600, H = 180, bw = W / n;
    $("tn-chart").setAttribute("viewBox", `0 0 ${W} ${H + 24}`);
    $("tn-chart").innerHTML = `<line x1="0" x2="${W}" y1="${H / 2}" y2="${H / 2}" stroke="#2c5468"/>` + vals.map((v, i) => {
      const h = Math.abs(v) / max * (H / 2 - 8), y = v >= 0 ? H / 2 - h : H / 2;
      return `<rect x="${(i * bw + bw * 0.18).toFixed(1)}" y="${y.toFixed(1)}" width="${(bw * 0.64).toFixed(1)}" height="${Math.max(1, h).toFixed(1)}" rx="3" fill="${v >= 0 ? "#86e3a8" : "#ff8574"}" opacity="${String(me) === String(i) ? 1 : 0.75}"/>` +
        (n <= 16 || i % 2 === 0 ? `<text x="${(i * bw + bw / 2).toFixed(1)}" y="${H + 16}" text-anchor="middle" fill="#93adb7" font-size="11" font-family="JetBrains Mono, monospace">${i + 1}</text>` : "");
    }).join("");
    $("tn-insight").innerHTML = `Con CETES al ${FY.RATES.cetes.toFixed(2)}% anual, el turno 1 gana unos <b class="ok-t">${fmt(vals[0])}</b> y el último pierde unos <b class="bad-t">${fmt(-vals[n - 1])}</b>. La tanda es un préstamo sin intereses para los primeros y un ahorro sin rendimiento para los últimos.`;
    drawWheel();
    FY.emit("tanda", { T, me });
  }

  function calLink(text, d, details) {
    const ymd = iso(d).replace(/-/g, "");
    const next = iso(new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1)).replace(/-/g, "");
    return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(text)}&details=${encodeURIComponent(details)}&dates=${ymd}/${next}`;
  }
  function payCal(T, ds) {
    const rule = T.freq === "semanal" ? `RRULE:FREQ=WEEKLY;COUNT=${ds.length}` : T.freq === "mensual" ? `RRULE:FREQ=MONTHLY;COUNT=${ds.length}` : `RRULE:FREQ=MONTHLY;BYMONTHDAY=15,-1;COUNT=${ds.length}`;
    const d = ds[0], ymd = iso(d).replace(/-/g, ""), next = iso(new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1)).replace(/-/g, "");
    return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(`Pago de la tanda: ${fmt(T.monto)}`)}&details=${encodeURIComponent(`"${T.nombre}". ${link(T)}`)}&dates=${ymd}/${next}&recur=${encodeURIComponent(rule)}`;
  }

  // ---------- editar ----------
  function readForm() {
    const personas = $("tn-people").value.split(/\n|,/).map((x) => x.replace(/[<>]/g, "").trim().slice(0, 24)).filter(Boolean).slice(0, MAX);
    return { nombre: $("tn-name").value.replace(/[<>]/g, "").trim().slice(0, 40) || "Mi tanda", monto: Math.max(1, Math.min(1e6, Math.round(+$("tn-amount").value || 0))), freq: $("tn-freq").value, inicio: /^\d{4}-\d{2}-\d{2}$/.test($("tn-start").value) ? $("tn-start").value : iso(today), personas, sorteada: false };
  }
  function commit() {
    const f = readForm();
    if (f.personas.length < 2) { FY.toast("Una tanda necesita al menos 2 personas."); return; }
    if (t().ejemplo || !lista.length) { lista.push(f); cur = lista.length - 1; } else lista[cur] = f;
    saveAll(); render();
  }
  ["tn-name", "tn-amount", "tn-freq", "tn-start"].forEach((id) => $(id).addEventListener("change", commit));
  $("tn-people").addEventListener("change", commit);
  $("tn-me").addEventListener("change", (e) => { const T = t(); if (T.ejemplo) commit(); yo[encode(t())] = e.target.value; saveAll(); render(); });
  $("tn-pick").addEventListener("change", (e) => { cur = +e.target.value; saveAll(); render(); });
  $("tn-new").addEventListener("click", () => {
    lista.push({ nombre: `Tanda ${lista.length + 1}`, monto: 500, freq: "quincenal", inicio: iso(today), personas: ["Yo", "Persona 2", "Persona 3", "Persona 4", "Persona 5"], sorteada: false });
    cur = lista.length - 1; saveAll(); render(); $("tn-name").focus();
  });

  // ---------- ruleta ----------
  let angle = 0, spinning = false, pool = null, order = [];
  const COLS = ["#ffb547", "#5ad6c8", "#86e3a8", "#ff8574", "#9fb7ff", "#ffd36b"];
  function drawWheel() {
    const cv = $("tn-wheel"), x = cv.getContext("2d"), S = cv.width, R = S / 2 - 6;
    const names = pool || t().personas;
    x.clearRect(0, 0, S, S);
    x.save(); x.translate(S / 2, S / 2); x.rotate(angle);
    const seg = (Math.PI * 2) / Math.max(1, names.length);
    names.forEach((nm, i) => {
      x.beginPath(); x.moveTo(0, 0); x.arc(0, 0, R, i * seg, (i + 1) * seg); x.closePath();
      x.fillStyle = COLS[i % COLS.length]; x.globalAlpha = 0.9; x.fill(); x.globalAlpha = 1;
      x.strokeStyle = "#07121a"; x.lineWidth = 2; x.stroke();
      x.save(); x.rotate(i * seg + seg / 2); x.fillStyle = "#07121a"; x.font = `700 ${names.length > 14 ? 11 : 14}px Figtree, sans-serif`; x.textAlign = "right";
      x.fillText(nm.slice(0, 12), R - 10, 5); x.restore();
    });
    x.restore();
    x.beginPath(); x.arc(S / 2, S / 2, 22, 0, Math.PI * 2); x.fillStyle = "#07121a"; x.fill();
    x.strokeStyle = "#ffb547"; x.lineWidth = 3; x.stroke();
    $("tn-order").innerHTML = order.length ? order.map((p, i) => `<li><span class="mono">${i + 1}</span>${p.replace(/</g, "")}</li>`).join("") : "";
  }
  function spin() {
    if (spinning) return;
    const T = t();
    if (!pool) { pool = T.personas.slice(); order = []; }
    if (!pool.length) return;
    spinning = true; $("tn-spin").disabled = true;
    const seg = (Math.PI * 2) / pool.length, pick = Math.floor(Math.random() * pool.length);
    // La flecha está arriba (−90°): llevamos el centro del segmento elegido ahí.
    const target = -Math.PI / 2 - (pick * seg + seg / 2);
    const TWO = Math.PI * 2, turns = FY.reduced ? 0 : 5;
    const delta = ((target - angle) % TWO + TWO) % TWO;
    const from = angle, to = angle + delta + turns * TWO;
    const dur = FY.reduced ? 1 : 2600, t0 = performance.now();
    (function step(now) {
      const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 4);
      angle = from + (to - from) * e; drawWheel();
      if (k < 1) return requestAnimationFrame(step);
      angle = to % TWO;
      const name = pool.splice(pick, 1)[0];
      order.push(name); FY.buzz(20);
      $("tn-result").textContent = `Turno ${order.length}: ${name}`;
      spinning = false; $("tn-spin").disabled = false;
      if (!pool.length) finishDraw(); else drawWheel();
    })(performance.now());
  }
  function finishDraw() {
    const T = t().ejemplo ? readForm() : t();
    const f = Object.assign({}, T, { personas: order.slice(), sorteada: true });
    if (t().ejemplo || !lista.length) { lista.push(f); cur = lista.length - 1; } else lista[cur] = f;
    pool = null; saveAll();
    FY.confetti(); $("tn-result").textContent = "¡Listo! Ya quedaron todos los turnos.";
    render(); order = [];
  }
  $("tn-spin").addEventListener("click", spin);
  $("tn-draw-all").addEventListener("click", () => {
    const T = t(), arr = T.personas.slice();
    for (let i = arr.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [arr[i], arr[j]] = [arr[j], arr[i]]; }
    pool = []; order = arr; finishDraw();
  });

  // ---------- compartir ----------
  function message(T) {
    const ds = dates(T.freq, T.inicio, T.personas.length), pot = T.personas.length * T.monto;
    return `*${T.nombre}*\nCada quien pone ${fmt(T.monto)} ${FREQ[T.freq]}. Cada turno recibe ${fmt(pot)}.\n\n` +
      T.personas.map((p, i) => `${i + 1}. ${p}: ${ds[i].toLocaleDateString("es-MX", { day: "numeric", month: "short" })}`).join("\n") +
      `\n\nMira cuándo te toca y pon tus recordatorios aquí: ${link(T)}`;
  }
  $("tn-wa").addEventListener("click", () => { const T = t(); $("tn-wa").href = "https://wa.me/?text=" + encodeURIComponent(message(T)); FY.emit("shared", "tanda"); });
  $("tn-copy").addEventListener("click", () => FY.copyText(link(t())));
  $("tn-share-card").addEventListener("click", () => FY.share && FY.share.open("tanda"));

  function init() { const imported = importFromURL(); render(); return imported; }
  FY.tanda = { init, render, dates, turnValue, periodRate, encode, decode, current: t, me: () => yo[encode(t())] };
})(window.FY);
