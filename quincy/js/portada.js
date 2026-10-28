// Quincy · portada: calculadora de temporada arriba (cambia sola por fecha), cuenta regresiva en vivo y la retícula de tarjetas.
// Para probar otra temporada: ?temporada=aguinaldo|cuesta|minimo|ptu|vacaciones|quincena
(function (FY) {
  const { fmt, ley, LEY } = FY;
  const $ = (id) => document.getElementById(id);
  const now = () => new Date();
  const today = () => { const t = now(); return new Date(t.getFullYear(), t.getMonth(), t.getDate(), 12); };
  const dshort = (d) => d.toLocaleDateString("es-MX", { day: "numeric", month: "long" });
  const num = (s) => +String(s || "").replace(/[^\d.]/g, "") || 0;
  const plural = (n, a, b) => `${n} ${n === 1 ? a : b}`;

  // Próxima quincena: el 15 o el último día del mes.
  function nextPayday(t = today()) {
    const d = t.getDate(), last = new Date(t.getFullYear(), t.getMonth() + 1, 0).getDate();
    return d === last ? new Date(t.getFullYear(), t.getMonth() + 1, 15, 12) : d >= 15 ? new Date(t.getFullYear(), t.getMonth(), last, 12) : new Date(t.getFullYear(), t.getMonth(), 15, 12);
  }
  const endOf = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1, 0, 0, 0); // la cuenta llega a cero al terminar ese día

  // ---------- temporadas ----------
  // from/to: [mes (0-11), día], ambos incluidos. El orden importa: gana la primera que coincide.
  const SEASONS = [
    { id: "aguinaldo", from: [9, 15], to: [11, 19] },
    { id: "cuesta", from: [11, 20], to: [0, 15] },
    { id: "minimo", from: [0, 16], to: [2, 31] },
    { id: "ptu", from: [3, 1], to: [5, 29] },
    { id: "vacaciones", from: [5, 30], to: [7, 15] },
    { id: "quincena", from: [7, 16], to: [9, 14] }
  ];
  function pickSeason(t) {
    const forced = new URLSearchParams(FY.INITIAL_SEARCH).get("temporada");
    if (forced && SEASONS.some((s) => s.id === forced)) return forced;
    const k = t.getMonth() * 100 + t.getDate();
    for (const s of SEASONS) {
      const a = s.from[0] * 100 + s.from[1], b = s.to[0] * 100 + s.to[1];
      if (a <= b ? k >= a && k <= b : k >= a || k <= b) return s.id;
    }
    return "quincena";
  }

  const salField = (label) => ({ l1: label });
  const DEF = {
    aguinaldo: {
      eyebrow: `Temporada de aguinaldo · ${LEY.year}`, h1: "¿Cuánto te toca de <em>aguinaldo</em>?",
      lede: `Pon tu sueldo y listo. Con la Ley Federal del Trabajo y los valores de ${LEY.year}.`,
      ...salField("Tu sueldo mensual, antes de impuestos"), ex: 15000,
      f2: `<label class="chk"><input type="checkbox" id="h-new"> Entré a trabajar este año</label><div id="h-new-box" hidden><label for="h-start" class="sr">Fecha de ingreso</label><input type="date" id="h-start"></div>`,
      target: () => endOf(new Date(today().getFullYear(), 11, 19)), countLabel: "Faltan para la fecha límite, 19 de diciembre",
      more: ["aguinaldo/", "Ver el cálculo completo y cuánto paga ISR"],
      calc(sal, ex) {
        const t = today(), sd = sal / 30, isNew = $("h-new") && $("h-new").checked;
        let st = new Date(t.getFullYear() - 1, 0, 1);
        if (isNew) { const v = $("h-start").value; const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v); if (m) st = new Date(+m[1], +m[2] - 1, +m[3], 12); }
        const ag = ley.aguinaldo({ sd, start: st, at: t }), left = ley.diffDays(t, ag.deadline);
        const libre = Math.min(ag.amount, ag.exento);
        return {
          label: "Te tocan", big: fmt(ag.amount),
          note: ex ? `Con ${fmt(sal)} al mes y el año completo. Escribe tu sueldo.` : `${ag.full ? `${LEY.aguinaldoDias} días de salario.` : `Proporcional a ${plural(ag.days, "día", "días")} trabajados.`} ${fmt(libre)} libres de ISR.${left >= 0 ? ` Te lo deben pagar a más tardar el 19 de diciembre.` : ""}`,
          wa: `Ya sé cuánto me toca de aguinaldo${left >= 0 ? ` y faltan ${plural(left, "día", "días")} para cobrarlo` : ""}. ¿Y a ti cuánto te toca? Calcúlalo en 10 segundos:`,
          card: { kicker: `Mi aguinaldo ${t.getFullYear()}`, big: fmt(ag.amount), line: left >= 0 ? `y faltan ${plural(left, "día", "días")} para cobrarlo` : "ya me tocó", sub: "Por ley, a más tardar el 19 de diciembre." },
          name: "mi-aguinaldo",
          wrapped: () => FY.compartir.aguinaldoWrapped(ag, left)
        };
      }
    },
    cuesta: {
      eyebrow: "Sobrevive la cuesta de enero", h1: "¿Cuánto puedes <em>gastar hoy</em>?",
      lede: "Lo que te llega, menos tus pagos fijos, entre los días que faltan para tu quincena.",
      l1: "Lo que te llega cada quincena", ex: 8000,
      f2: `<label for="h-x">Tus pagos fijos de la quincena</label><div class="money"><span aria-hidden="true">$</span><input id="h-x" type="text" inputmode="numeric" placeholder="3,500" autocomplete="off"></div>`,
      target: () => endOf(nextPayday()), countLabel: () => `Faltan para tu próxima quincena, ${dshort(nextPayday())}`,
      more: ["quincena/", "Calcula con tu ahorro y lo que ya gastaste"],
      calc: (sal, ex) => quincenaCalc(sal, ex)
    },
    minimo: {
      eyebrow: `Salario mínimo ${LEY.year}`, h1: "¿Tu sueldo está arriba del <em>mínimo</em>?",
      lede: `El salario mínimo de ${LEY.year} es de ${fmt(LEY.sm.general * 30)} al mes (${LEY.sm.general.toFixed(2)} al día) y en la frontera norte de ${fmt(LEY.sm.frontera * 30)}.`,
      l1: "Tu sueldo mensual, antes de impuestos", ex: 12000, f2: "",
      target: () => endOf(nextPayday()), countLabel: () => `Faltan para tu próxima quincena, ${dshort(nextPayday())}`,
      more: ["aguinaldo/", "Y calcula lo que te toca de aguinaldo"],
      calc(sal, ex) {
        const min = LEY.sm.general * 30, diff = sal - min, x = sal / min;
        return {
          label: diff >= 0 ? "Ganas el mínimo por" : "Te faltan para el mínimo", big: diff >= 0 ? `${x.toLocaleString("es-MX", { maximumFractionDigits: 1 })} veces` : fmt(-diff),
          note: ex ? `Con ${fmt(sal)} al mes. Escribe tu sueldo.` : diff >= 0 ? `Estás ${fmt(diff)} arriba del mínimo general de ${LEY.year}.` : "Por ley nadie puede ganar menos que el mínimo por una jornada completa. PROFEDET te asesora gratis.",
          wa: `El salario mínimo de ${LEY.year} es de ${fmt(min)} al mes. ¿Tu sueldo está arriba? Revísalo aquí:`,
          card: { kicker: `Salario mínimo ${LEY.year}`, big: fmt(min), line: "al mes, por una jornada completa", sub: "¿Tu sueldo está arriba?" }, name: "salario-minimo"
        };
      }
    },
    ptu: {
      eyebrow: "Temporada de reparto de utilidades", h1: "¿Cuánto te puede tocar de <em>PTU</em>?",
      lede: "El tope es de 3 meses de salario o el promedio de tus últimos 3 años, lo que más te convenga.",
      l1: "Tu sueldo mensual, antes de impuestos", ex: 15000, f2: "",
      target: () => { const p = ley.ptu({ sd: 1, at: today() }); return endOf(today() > p.empresas ? p.personas : p.empresas); },
      countLabel: () => { const p = ley.ptu({ sd: 1, at: today() }); return today() > p.empresas ? `Faltan para el ${dshort(p.personas)} (patrón persona física)` : `Faltan para el ${dshort(p.empresas)}, fecha límite de las empresas`; },
      more: ["ptu/", "Ver fechas y cómo se reparte"],
      calc(sal, ex) {
        const p = ley.ptu({ sd: sal / 30, at: today() });
        return {
          label: "Tu PTU puede llegar hasta", big: fmt(p.tope),
          note: ex ? `Con ${fmt(sal)} al mes. Escribe tu sueldo.` : `Si tu empresa tuvo utilidades. Libre de ISR hasta ${fmt(p.exento)} (15 UMA).`,
          wa: "Ya sé hasta cuánto me puede tocar de reparto de utilidades. ¿Y a ti?",
          card: { kicker: "Mi PTU, hasta", big: fmt(p.tope), line: "si mi empresa tuvo utilidades", sub: "Tope: 3 meses de salario o el promedio de 3 años." }, name: "mi-ptu"
        };
      }
    },
    vacaciones: {
      eyebrow: "Temporada de vacaciones", h1: "¿Cuántos días de <em>vacaciones</em> te tocan?",
      lede: "Con la reforma de vacaciones dignas: 12 días el primer año y suben cada año.",
      l1: "Tu sueldo mensual, antes de impuestos", ex: 15000,
      f2: `<label for="h-x">Años que llevas en tu trabajo</label><input id="h-x" type="number" inputmode="numeric" min="1" max="45" value="1">`,
      target: () => endOf(nextPayday()), countLabel: () => `Faltan para tu próxima quincena, ${dshort(nextPayday())}`,
      more: ["vacaciones/", "Ver la tabla completa"],
      calc(sal, ex) {
        const yrs = Math.max(1, Math.min(45, num($("h-x") && $("h-x").value) || 1)), days = ley.vacationDays(yrs), prima = days * sal / 30 * LEY.primaVacacional;
        return {
          label: "Te tocan", big: `${days} días`,
          note: `${ex ? `Con ${fmt(sal)} al mes: p` : "P"}rima vacacional de ${fmt(prima)} (25%). Llevas ${plural(yrs, "año", "años")} en tu trabajo.`,
          wa: `Me tocan ${days} días de vacaciones por ley. ¿Cuántos te tocan a ti?`,
          card: { kicker: "Mis vacaciones", big: `${days} días`, line: `y ${fmt(prima)} de prima vacacional`, sub: "Vacaciones dignas, artículo 76 de la LFT." }, name: "mis-vacaciones"
        };
      }
    },
    quincena: {
      eyebrow: "Regreso a clases · cuida tu quincena", h1: "¿Cuánto puedes <em>gastar hoy</em>?",
      lede: "Lo que te llega, menos tus pagos fijos, entre los días que faltan para tu quincena.",
      l1: "Lo que te llega cada quincena", ex: 8000,
      f2: `<label for="h-x">Tus pagos fijos de la quincena</label><div class="money"><span aria-hidden="true">$</span><input id="h-x" type="text" inputmode="numeric" placeholder="3,500" autocomplete="off"></div>`,
      target: () => endOf(nextPayday()), countLabel: () => `Faltan para tu próxima quincena, ${dshort(nextPayday())}`,
      more: ["quincena/", "Calcula con tu ahorro y lo que ya gastaste"],
      calc: (sal, ex) => quincenaCalc(sal, ex)
    }
  };
  function quincenaCalc(inc, ex) {
    const fix = num($("h-x") && $("h-x").value) || (ex ? 3500 : 0), next = nextPayday(), n = Math.max(1, ley.diffDays(today(), next)), left = inc - fix, daily = Math.max(0, left / n);
    return {
      label: "Hoy puedes gastar", big: fmt(daily),
      note: left <= 0 ? "Tus pagos fijos se comen todo tu pago. Ahí está la primera alerta." : `${ex ? `Con ${fmt(inc)} y ${fmt(fix)} de pagos fijos. ` : ""}Faltan ${plural(n, "día", "días")} para tu quincena. Si hoy gastas menos, mañana tienes más.`,
      wa: "Ya sé cuánto puedo gastar hoy para llegar a la quincena. ¿Y tú?",
      card: { kicker: "Hoy puedo gastar", big: fmt(daily), line: `y llego completo a la quincena`, sub: `Faltan ${plural(n, "día", "días")}.`, tone: "tide" }, name: "mi-limite-de-hoy"
    };
  }

  // ---------- portada de temporada ----------
  const season = pickSeason(today());
  const S = DEF[season];
  document.documentElement.dataset.season = season;
  if (season !== "aguinaldo") {
    $("h-eyebrow").lastChild.textContent = S.eyebrow;
    $("h-title").innerHTML = S.h1; $("h-lede").textContent = S.lede;
    $("h-l1").textContent = S.l1; $("h-sal").placeholder = S.ex.toLocaleString("es-MX");
    $("h-more").firstChild.textContent = S.more[1] + " ";
  }
  $("h-more").href = S.more[0];
  $("h-more2").hidden = season !== "aguinaldo";
  if (season !== "aguinaldo") { $("h-f2").innerHTML = S.f2; $("h-f2").hidden = !S.f2; }
  const countLabel = typeof S.countLabel === "function" ? S.countLabel() : S.countLabel;
  $("h-count-label").textContent = countLabel;

  let current = null;
  const SUELDO = ["aguinaldo", "minimo", "ptu", "vacaciones"];
  function run() {
    const typed = num($("h-sal").value), ex = !typed;
    current = S.calc(typed || S.ex, ex);
    $("h-rlabel").textContent = current.label;
    $("h-big").textContent = current.big;
    $("h-note").textContent = current.note;
    $("h-form").classList.toggle("is-ex", ex);
    // La app llega con este sueldo ya puesto (solo en temporadas donde lo que escribes es tu sueldo mensual).
    if (SUELDO.includes(season)) {
      if (typed) FY.store.set("portada", { sueldo: typed });
      document.querySelectorAll('a[href^="app.html"]').forEach((a) => {
        const [base, hash] = a.getAttribute("href").split("#");
        a.setAttribute("href", base.split("?")[0] + (typed ? `?sueldo=${typed}` : "") + (hash ? "#" + hash : ""));
      });
    }
  }
  // Formato con comas mientras escribes, sin mover el cursor al final si no hace falta.
  $("h-sal").addEventListener("input", (e) => {
    const el = e.target, raw = el.value.replace(/\.\d{0,2}\s*$/, "").replace(/[^\d]/g, "").slice(0, 8);
    const pretty = raw ? (+raw).toLocaleString("es-MX") : "";
    if (el.value !== pretty) { const fromEnd = el.value.length - el.selectionStart; el.value = pretty; const p = Math.max(0, pretty.length - fromEnd); try { el.setSelectionRange(p, p); } catch (er) {} }
    run();
  });
  $("h-f2").addEventListener("input", run); $("h-f2").addEventListener("change", run);
  if ($("h-new")) $("h-new").addEventListener("change", () => {
    $("h-new-box").hidden = !$("h-new").checked;
    if ($("h-new").checked && !$("h-start").value) { const t = today(); $("h-start").value = `${t.getFullYear()}-${String(Math.min(t.getMonth() + 1, 6)).padStart(2, "0")}-01`; }
    run();
  });
  run();
  FY.compartir.bar($("h-share"), () => ({ ref: "wa", ...current }));
  FY.compartir.welcome($("hero"), "#h-sal", season === "aguinaldo" ? "Tu amigo ya sabe cuánto le toca de aguinaldo." : null);

  // ---------- cuenta regresiva en vivo ----------
  const target = S.target();
  const pad = (n) => String(n).padStart(2, "0");
  function tick() {
    let ms = Math.max(0, target - now());
    const d = Math.floor(ms / 864e5); ms -= d * 864e5;
    const h = Math.floor(ms / 36e5); ms -= h * 36e5;
    const m = Math.floor(ms / 6e4); const s = Math.floor((ms - m * 6e4) / 1000);
    $("cd-d").textContent = d; $("cd-h").textContent = pad(h); $("cd-m").textContent = pad(m); $("cd-s").textContent = pad(s);
  }
  tick(); setInterval(tick, 1000);

  // ---------- tarjeta "Hoy": cuánto puedes gastar ----------
  function setP(r) { r.style.setProperty("--p", ((r.value - r.min) / (r.max - r.min) * 100) + "%"); }
  function demoHoy() {
    const inc = +$("d-income").value, fix = +$("d-fixed").value, n = Math.max(1, ley.diffDays(today(), nextPayday()));
    $("d-income-out").textContent = fmt(inc); $("d-fixed-out").textContent = fmt(fix);
    $("d-daily").textContent = fmt(Math.max(0, (inc - fix) / n));
    $("d-daily").className = "mono " + (inc - fix > 0 ? "ok-t" : "bad-t");
    $("d-days").textContent = inc - fix > 0 ? `Faltan ${plural(n, "día", "días")} para tu quincena.` : "Tus pagos fijos se comen todo tu pago.";
    ["d-income", "d-fixed"].forEach((id) => setP($(id)));
  }
  ["d-income", "d-fixed"].forEach((id) => $(id).addEventListener("input", demoHoy));
  demoHoy();

  // ---------- calendario ----------
  (function dates() {
    const t = today(), y = t.getFullYear();
    const after = (m, d) => { const x = new Date(y, m, d, 12); return ley.diffDays(t, x) >= 0 ? x : new Date(y + 1, m, d, 12); };
    const ev = [
      { d: nextPayday(), t: "Tu próxima quincena", s: "El 15 y el último día de cada mes." },
      { d: after(11, 19), t: "Aguinaldo", s: "Fecha límite por ley.", href: "aguinaldo/" },
      { d: after(0, 1), t: "Nuevo salario mínimo", s: "Revisa que tu sueldo no quede abajo." },
      { d: after(4, 30), t: "Reparto de utilidades", s: "Si tu empresa tuvo ganancias.", href: "ptu/" }
    ].sort((a, b) => a.d - b.d);
    $("dates").innerHTML = ev.map((e) => {
      const n = ley.diffDays(t, e.d);
      const inner = `<span class="n mono">${n === 0 ? "Hoy" : n}<small>${n === 0 ? "" : n === 1 ? "día" : "días"}</small></span><span><b>${e.t}</b><span>${e.d.toLocaleDateString("es-MX", { day: "numeric", month: "short" })} · ${e.s}</span></span>`;
      return `<li>${e.href ? `<a href="${e.href}">${inner}</a>` : `<div>${inner}</div>`}</li>`;
    }).join("");
  })();

  // En celular el calendario empieza cerrado (es secundario); en temporada de aguinaldo, "ponlo a rendir" va primero.
  if (matchMedia("(max-width:640px)").matches) $("cal").open = false;
  if (season === "aguinaldo") { const g = document.querySelector(".calc-grid"), r = g.querySelector('a[href="aguinaldo-a-rendir/"]'); if (r) g.prepend(r); }

  // ---------- avatar ----------
  if (FY.avatar) $("l-avatar").innerHTML = FY.avatar.svg(65, "ok", 2, "long");

  // ---------- avísame ----------
  $("rem-ag").addEventListener("click", () => {
    const y = today().getMonth() === 11 && today().getDate() > 19 ? today().getFullYear() + 1 : today().getFullYear();
    FY.compartir.ics({ title: "Fecha límite de mi aguinaldo", date: new Date(y, 11, 19), desc: `Por ley te lo deben pagar a más tardar hoy. Calcula cuánto te toca: ${FY.compartir.link("recordatorio", "aguinaldo/")}`, alarmDays: 3, name: "aguinaldo" });
  });
  $("rem-q").addEventListener("click", () => {
    FY.compartir.ics({ title: "Hoy es quincena", date: nextPayday(), desc: `Un minuto para saber cuánto puedes gastar al día: ${FY.compartir.link("recordatorio", "app.html")}`, alarmDays: 0, name: "quincena" });
  });
  if (FY.CONFIG.AVISOS.whatsappCanal) { $("rem-wa").hidden = false; $("rem-wa").href = FY.CONFIG.AVISOS.whatsappCanal; }
  $("ig").href = FY.CONFIG.INSTAGRAM; $("tt").href = FY.CONFIG.TIKTOK;

})(window.FY);
