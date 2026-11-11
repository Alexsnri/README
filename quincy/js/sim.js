// Quincy · "Futuro": simulador de retiro, gráfica, carta y avatar que envejece.
(function (FY) {
  const { $, state, fmt, short, VEH, RATES, store } = FY;
  let scrubAge = state.retire;
  let series = [];
  let lastRetire = null;
  let last = null;

  // ---------- cálculo principal ----------
  function compute() {
    const months = Math.max(1, (state.retire - state.age) * 12);
    const rate = VEH[state.veh].rate();
    const bal = FY.balanceAt(months, rate, state.monthly, state.saved);
    const income = bal * 0.04 / 12;
    const ratio = income / state.need;
    const mood = ratio >= 1 ? "ok" : ratio >= 0.5 ? "mid" : "bad";
    const target = FY.targetFor(state.need);
    const req = FY.requiredMonthly(target, months, rate, state.saved);
    const reqCetes = FY.requiredMonthly(target, months, RATES.cetes, state.saved);
    return { months, rate, bal, income, ratio, mood, req, reqCetes, year: FY.YEAR + state.retire - state.age };
  }
  const moodText = (m) => m === "ok" ? "Tu yo del futuro está en paz" : m === "mid" ? "A medias" : "En apuros";

  // ---------- gráfica ----------
  let W = 640, H = 340;
  const P = { l: 58, r: 16, t: 16, b: 36 };
  const X = (a) => P.l + (a - state.age) / Math.max(1, state.retire - state.age) * (W - P.l - P.r);
  let yMax = 1;
  const Y = (v) => H - P.b - Math.max(0, v) / yMax * (H - P.t - P.b);
  function niceStep(max) {
    const raw = max / 4, mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const n = raw / mag;
    return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * mag;
  }
  function drawChart(c) {
    W = Math.round(Math.min(640, Math.max(300, $("chart-wrap").clientWidth || 640)));
    H = W < 500 ? 260 : 340;
    $("chart").setAttribute("viewBox", `0 0 ${W} ${H}`);
    const target = FY.targetFor(state.need);
    series = [];
    for (let a = state.age; a <= state.retire; a++) {
      const m = (a - state.age) * 12;
      series.push({ a, plan: FY.balanceAt(m, c.rate, state.monthly, state.saved), cash: FY.balanceAt(m, 0, state.monthly, state.saved) });
    }
    const peak = Math.max(target * 1.05, ...series.map((s) => s.plan), 1000);
    const step = niceStep(peak);
    yMax = Math.ceil(peak / step) * step;
    const font = 'font-size="11" font-family="JetBrains Mono, monospace"';
    let g = "";
    for (let v = 0; v <= yMax + 1; v += step) {
      g += `<line x1="${P.l}" x2="${W - P.r}" y1="${Y(v)}" y2="${Y(v)}" stroke="#1e3a4a"/>`;
      g += `<text x="${P.l - 8}" y="${Y(v) + 4}" text-anchor="end" fill="#93adb7" ${font}>${v === 0 ? "$0" : short(v)}</text>`;
    }
    const span = state.retire - state.age, xs = span <= 12 ? 2 : span <= 25 ? 5 : 10;
    for (let a = state.age; a <= state.retire; a++) {
      if ((a - state.age) % xs !== 0 && a !== state.retire) continue;
      if (a !== state.retire && state.retire - a < xs * 0.5) continue;
      g += `<text x="${X(a)}" y="${H - 12}" text-anchor="middle" fill="#93adb7" ${font}>${a}</text>`;
    }
    const line = (k) => series.map((s, j) => `${j ? "L" : "M"}${X(s.a).toFixed(1)} ${Y(s[k]).toFixed(1)}`).join(" ");
    const lastS = series[series.length - 1];
    $("chart").innerHTML = `
      <defs><linearGradient id="gsun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffb547" stop-opacity=".45"/><stop offset="1" stop-color="#ffb547" stop-opacity="0"/></linearGradient></defs>
      ${g}
      <line x1="${P.l}" x2="${W - P.r}" y1="${Y(target)}" y2="${Y(target)}" stroke="#5ad6c8" stroke-dasharray="2 5" stroke-width="2"/>
      <text x="${W - P.r}" y="${Y(target) - 7}" text-anchor="end" fill="#5ad6c8" ${font}>meta ${short(target)}</text>
      <path d="${line("plan")} L${X(state.retire)} ${Y(0)} L${X(state.age)} ${Y(0)} Z" fill="url(#gsun)"/>
      <path d="${line("cash")}" fill="none" stroke="#ff8574" stroke-width="2" stroke-dasharray="6 5"/>
      <path d="${line("plan")}" fill="none" stroke="#ffb547" stroke-width="3" stroke-linejoin="round"/>
      <circle cx="${X(lastS.a)}" cy="${Y(lastS.plan)}" r="6" fill="#ffb547" stroke="#07121a" stroke-width="3"/>
      <line id="cursor" x1="0" x2="0" y1="${P.t}" y2="${H - P.b}" stroke="#5ad6c8" stroke-width="1.5" opacity="0"/>
      <circle id="cursor-dot" r="5" fill="#5ad6c8" opacity="0"/>`;
    $("lg-plan").textContent = VEH[state.veh].label;
    markScrub();
  }
  function markScrub() {
    const s = series.find((r) => r.a === scrubAge), cur = $("cursor"), dot = $("cursor-dot");
    if (!s || !cur) return;
    const on = scrubAge !== state.retire ? 1 : 0;
    cur.setAttribute("x1", X(s.a)); cur.setAttribute("x2", X(s.a)); cur.setAttribute("opacity", on * 0.8);
    dot.setAttribute("cx", X(s.a)); dot.setAttribute("cy", Y(s.plan)); dot.setAttribute("opacity", on);
  }
  const tip = $("tip");
  $("chart-wrap").addEventListener("pointermove", (e) => {
    if (!series.length) return;
    const r = $("chart").getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width * W;
    let best = series[0];
    for (const s of series) if (Math.abs(X(s.a) - px) < Math.abs(X(best.a) - px)) best = s;
    tip.style.left = (X(best.a) / W * r.width) + "px";
    tip.style.top = (Y(best.plan) / H * r.height) + "px";
    tip.innerHTML = `<b>${best.a} años · ${FY.YEAR + best.a - state.age}</b><br><span class="sun">${fmt(best.plan)}</span> plan<br><span style="color:var(--bad)">${fmt(best.cash)}</span> colchón`;
    tip.style.opacity = 1;
  });
  $("chart-wrap").addEventListener("pointerleave", () => { tip.style.opacity = 0; });

  // ---------- carta ----------
  function letterText(c, html) {
    const b = (s) => html ? `<strong>${s}</strong>` : s;
    const yrs = state.retire - state.age, where = VEH[state.veh].name;
    const gap = Math.max(0, state.need - c.income);
    let t;
    if (c.mood === "ok") {
      t = `Hola. Soy tú, en ${c.year}. Tengo ${state.retire} años y te escribo para darte las gracias.\n\nEsos ${b(fmt(state.monthly))} al mes que guardaste en ${where} hoy valen ${b(fmt(c.bal))} en pesos de tu época. Me dan unos ${b(fmt(c.income))} al mes, justo lo que querías.\n\nNo fue suerte. Fueron ${yrs} años de no rendirte. Sigue así, y date un gusto de vez en cuando: también me acuerdo de eso.`;
    } else if (c.mood === "mid") {
      t = `Hola. Soy tú, en ${c.year}. Tengo ${state.retire} años.\n\nLo que guardaste me da unos ${b(fmt(c.income))} al mes. Necesito ${b(fmt(state.need))}, así que me faltan ${b(fmt(gap))} cada mes. Vivo bien, pero con cuidado.\n\nTú todavía puedes cambiarlo. Si subes tu ahorro a ${b(fmt(c.req))} al mes, llego completo. Yo ya no puedo hacer nada. Tú sí.`;
    } else {
      t = `Hola. Soy tú, en ${c.year}. Tengo ${state.retire} años y necesito pedirte algo.\n\nCon lo que guardamos tengo ${b(fmt(c.income))} al mes. Necesito ${b(fmt(state.need))}. Todavía trabajo, y no siempre porque quiera.\n\nNo te escribo para regañarte. Te escribo porque aún hay tiempo: ${b(fmt(c.req))} al mes desde hoy lo arregla. Empieza este mes, aunque sea con poquito.`;
    }
    if (state.veh === "colchon" && c.reqCetes < c.req) t += `\n\nPD: bajo el colchón la inflación me come. En CETES me bastaría con ${b(fmt(c.reqCetes))} al mes.`;
    const h = FY.quincena && FY.quincena.summary();
    if (h && h.streak >= 2) t += `\n\nPD: llevas ${b(h.streak + " días")} seguidos sin pasarte de tu límite. Lo noto.`;
    return t;
  }

  // ---------- portal: tu avatar ----------
  let rafPending = false;
  function schedulePortal() { if (rafPending) return; rafPending = true; requestAnimationFrame(() => { rafPending = false; renderPortal(); }); }
  function renderPortal() {
    const c = last || compute();
    const s = series.find((r) => r.a === scrubAge) || series[series.length - 1] || { plan: c.bal };
    $("avatar").innerHTML = FY.avatar.svg(scrubAge, scrubAge === state.age ? "mid" : c.mood, state.skin, state.hair);
    $("avatar").setAttribute("aria-label", `Tu avatar a los ${scrubAge} años`);
    $("portal-tag").innerHTML = scrubAge === state.age
      ? `Tú hoy · <span>${scrubAge} años</span> · ${fmt(s.plan)}`
      : `Tú · <span>${scrubAge} años</span> · ${FY.YEAR + scrubAge - state.age} · ${short(s.plan)}`;
    $("scrub-out").textContent = `${scrubAge} años`;
    markScrub();
  }
  const faceAt = (age, mood) => ({ svg: FY.avatar.svg(age, mood || "mid", state.skin, state.hair) });

  // ---------- render general ----------
  function setP(el) { const p = (el.value - el.min) / ((el.max - el.min) || 1) * 100; el.style.setProperty("--p", p + "%"); }
  function render() {
    state.retire = Math.max(state.retire, state.age + 2);
    $("retire").value = state.retire;
    const c = compute(); last = c;
    $("age-out").textContent = state.age;
    $("retire-out").textContent = state.retire;
    $("monthly-out").textContent = fmt(state.monthly);
    $("saved-out").textContent = fmt(state.saved);
    $("need-out").textContent = fmt(state.need);
    $("h-age").textContent = state.retire;
    $("res-label").textContent = `A tus ${state.retire} tendrás`;
    $("res-big").textContent = fmt(c.bal);
    $("res-sub").textContent = `en pesos de hoy, guardando ${fmt(state.monthly)} al mes durante ${state.retire - state.age} años`;
    $("res-income").innerHTML = `Eso te da unos <b>${fmt(c.income)} al mes</b> (regla del 4%). Querías ${fmt(state.need)}.`;
    const chip = $("mood-chip"); chip.className = "chip " + c.mood; chip.textContent = moodText(c.mood);
    $("meter").style.width = Math.min(100, c.ratio * 100).toFixed(1) + "%";
    document.querySelectorAll(".veh").forEach((b) => b.setAttribute("aria-pressed", b.dataset.veh === state.veh));
    const sc = $("age-scrub");
    sc.min = state.age; sc.max = state.retire;
    if (lastRetire !== state.retire) scrubAge = state.retire;
    lastRetire = state.retire;
    scrubAge = FY.clamp(scrubAge, state.age, state.retire);
    sc.value = scrubAge;
    ["age", "retire", "monthly", "saved", "need", "age-scrub"].forEach((k) => setP($(k)));
    $("scrub-min").textContent = `Hoy · ${state.age}`;
    $("scrub-max").textContent = `Retiro · ${state.retire}`;
    drawChart(c);
    renderPortal();
    $("letter-body").innerHTML = letterText(c, true);
    $("letter-meta").textContent = `México, ${c.year} · enviada hace ${state.retire - state.age} años`;
    FY.save();
    FY.emit("plan", c);
  }

  // ---------- controles ----------
  ["age", "retire", "monthly", "saved", "need"].forEach((k) => {
    const el = $(k);
    el.value = state[k];
    el.addEventListener("input", () => { state[k] = +el.value; if (k === "age" || k === "retire") boost(); render(); });
  });
  document.querySelectorAll(".veh").forEach((b) => b.addEventListener("click", () => { state.veh = b.dataset.veh; boost(); FY.buzz(8); render(); }));
  $("age-scrub").addEventListener("input", (e) => { scrubAge = +e.target.value; setP(e.target); boost(0.5); schedulePortal(); });
  const skins = $("skins");
  FY.avatar.SKINS.forEach((col, k) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "sw"; b.style.background = col;
    b.setAttribute("aria-label", `Tono de piel ${k + 1}`); b.setAttribute("aria-pressed", k === state.skin);
    b.addEventListener("click", () => { state.skin = k; skins.querySelectorAll(".sw").forEach((x, j) => x.setAttribute("aria-pressed", j === k)); FY.save(); renderPortal(); });
    skins.appendChild(b);
  });
  document.querySelectorAll("[data-hair]").forEach((b) => {
    b.setAttribute("aria-pressed", b.dataset.hair === state.hair);
    b.addEventListener("click", () => { state.hair = b.dataset.hair; document.querySelectorAll("[data-hair]").forEach((x) => x.setAttribute("aria-pressed", x === b)); FY.save(); renderPortal(); });
  });
  $("copy-letter").addEventListener("click", () => FY.copyText(letterText(last || compute(), false) + "\n\n" + FY.shareURL({ ref: "carta" })));

  // Inclinación 3D del portal con el mouse.
  const portal = $("portal");
  if (!FY.reduced) {
    portal.addEventListener("pointermove", (e) => {
      if (e.pointerType !== "mouse") return;
      const r = portal.getBoundingClientRect();
      const rx = ((e.clientY - r.top) / r.height - 0.5) * -8, ry = ((e.clientX - r.left) / r.width - 0.5) * 8;
      portal.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg)`;
    });
    portal.addEventListener("pointerleave", () => { portal.style.transform = ""; });
  }

  // ---------- túnel del tiempo ----------
  const cv = $("warp"), ctx = cv.getContext("2d");
  let stars = [], speed = 0.6, target = 0.6, running = false;
  function sizeCanvas() {
    const r = cv.getBoundingClientRect(), d = Math.min(2, devicePixelRatio || 1);
    cv.width = Math.max(1, r.width * d); cv.height = Math.max(1, r.height * d);
    stars = Array.from({ length: 140 }, () => ({ a: Math.random() * Math.PI * 2, r: Math.random() * cv.width * 0.5, z: Math.random() * 0.8 + 0.2 }));
  }
  function boost(v) { target = Math.max(target, v || 4); }
  function tick() {
    if (document.hidden || $("v-futuro").hidden) { running = false; return; }
    speed += (target - speed) * 0.08; target += (0.6 - target) * 0.03;
    ctx.fillStyle = "rgba(7,18,26,.28)"; ctx.fillRect(0, 0, cv.width, cv.height);
    const cx = cv.width / 2, cy = cv.height * 0.46, max = Math.hypot(cx, cy);
    for (const s of stars) {
      const r0 = s.r;
      s.r += (s.r * 0.012 + 0.4) * speed * s.z;
      if (s.r > max) { s.r = Math.random() * 20; s.a = Math.random() * Math.PI * 2; }
      const k = s.r / max;
      ctx.strokeStyle = k > 0.55 ? `rgba(255,181,71,${k * 0.8})` : `rgba(90,214,200,${0.25 + k})`;
      ctx.lineWidth = 1 + k * 2;
      ctx.beginPath(); ctx.moveTo(cx + Math.cos(s.a) * r0, cy + Math.sin(s.a) * r0); ctx.lineTo(cx + Math.cos(s.a) * s.r, cy + Math.sin(s.a) * s.r); ctx.stroke();
    }
    if (!FY.reduced) requestAnimationFrame(tick); else running = false;
  }
  function startWarp() { if (running) return; running = true; tick(); }
  addEventListener("resize", () => { sizeCanvas(); if (last) drawChart(last); });
  document.addEventListener("visibilitychange", () => { if (!document.hidden) startWarp(); });

  function init() {
    sizeCanvas(); render(); startWarp();
  }
  FY.sim = { init, render, compute, moodText, faceAt, letterText, startWarp, sizeCanvas, getScrub: () => scrubAge, last: () => last || compute() };
})(window.FY);
