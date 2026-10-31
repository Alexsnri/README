// Quincy · "Me toca": aguinaldo, vacaciones, prima, PTU, finiquito y liquidación, con su calendario.
(function (FY) {
  const { $, fmt, store, ley, LEY } = FY;
  const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const parse = (s) => { const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || ""); return m ? new Date(+m[1], +m[2] - 1, +m[3], 12) : null; };
  const today = () => { const t = new Date(); return new Date(t.getFullYear(), t.getMonth(), t.getDate(), 12); };
  const longDate = (d) => d.toLocaleDateString("es-MX", { day: "numeric", month: "long", year: "numeric" });
  const exampleStart = () => { const t = today(); return iso(new Date(t.getFullYear() - 3, t.getMonth() - 4, 1, 12)); };

  const perfil = Object.assign({ sueldo: 15000, inicio: exampleStart(), zona: "general", agDias: 15, prima: 25, configurado: false }, store.get("perfil", {}));
  const salida = Object.assign({ motivo: "despido", fin: iso(today()), pend: 0, sinPago: 0 }, store.get("salida", {}));
  const save = () => { store.set("perfil", perfil); store.set("salida", salida); };

  function inputs() {
    const sd = ley.dailyFromMonthly(perfil.sueldo);
    let start = parse(perfil.inicio) || parse(exampleStart());
    if (start > today()) start = today();
    return { sd, start, dias: perfil.agDias, prima: perfil.prima / 100 };
  }

  function render() {
    const { sd, start, dias, prima } = inputs();
    const t = today();
    $("mt-example").hidden = perfil.configurado;
    if ($("mt-sum")) $("mt-sum").textContent = perfil.configurado
      ? `Sueldo de ${fmt(perfil.sueldo)} al mes${parse(perfil.inicio) ? `, desde el ${longDate(parse(perfil.inicio))}` : ""}${perfil.zona === "frontera" ? " · frontera norte" : ""}`
      : "Con datos de ejemplo. Pon tu sueldo y tu fecha de ingreso.";
    $("mt-sd").textContent = `Salario diario: ${fmt(sd)} (sueldo mensual ÷ 30)`;
    // Aguinaldo
    const ag = ley.aguinaldo({ sd, start, at: t, dias });
    const agLeft = ley.diffDays(t, ag.deadline);
    $("mt-ag").textContent = fmt(ag.amount);
    $("mt-ag-note").innerHTML = agLeft >= 0
      ? `Te lo deben pagar a más tardar el <b>19 de diciembre</b>: faltan <b class="sun">${agLeft} días</b>. ${ag.full ? `Son ${dias} días de salario.` : `Proporcional a ${ag.days} días trabajados este año.`}`
      : `El de este año ya se debió pagar el 19 de diciembre. Si no te lo dieron, puedes reclamarlo.`;
    $("mt-ag-short").textContent = agLeft >= 0 ? `A más tardar el 19 de diciembre · faltan ${agLeft} días` : "Ya te lo debieron pagar";
    $("mt-ag-tax").textContent = `Exento de ISR hasta ${fmt(ag.exento)} (30 UMA). ${ag.gravado > 0 ? `Sobre ${fmt(ag.gravado)} te retienen ISR.` : "No te deben quitar ISR."}`;
    // Vacaciones
    const v = ley.vacaciones({ sd, start, at: t, prima });
    $("mt-vac").textContent = v.years >= 1 ? `${v.days} días` : "Aún no";
    $("mt-vac-short").textContent = v.years >= 1 ? `Y ${fmt(v.prima)} de prima vacacional` : "Al cumplir tu primer año te tocan 12";
    $("mt-vac-note").innerHTML = v.years >= 1
      ? `Llevas ${v.years} ${v.years === 1 ? "año" : "años"}. Tu prima vacacional (${perfil.prima}%) es de <b class="sun">${fmt(v.prima)}</b>.`
      : `Al cumplir tu primer año te tocan 12 días con goce de sueldo.`;
    $("mt-vac-next").innerHTML = `El <b>${longDate(v.nextDate)}</b> cumples ${v.years + 1} ${v.years + 1 === 1 ? "año" : "años"}: te tocarán <b>${v.nextDays} días</b>. Faltan ${v.daysToNext} días.`;
    // PTU
    const p = ley.ptu({ sd, at: t });
    $("mt-ptu").textContent = fmt(p.tope);
    $("mt-ptu-short").textContent = `Si tu empresa tuvo utilidades · a más tardar el ${p.empresas.toLocaleDateString("es-MX", { day: "numeric", month: "long" })}`;
    $("mt-ptu-note").innerHTML = `Es el máximo que te pueden dar: 3 meses de salario o el promedio de tus últimos 3 años, lo que más te convenga. Las empresas pagan a más tardar el <b>${longDate(p.empresas)}</b>; los patrones personas físicas, el <b>${longDate(p.personas)}</b>.`;
    // Salida
    let fin = parse(salida.fin) || t;
    if (fin < start) fin = start;
    const r = ley.salida({ sd, start, end: fin, motivo: salida.motivo, zona: perfil.zona, dias, prima, vacPendientes: salida.pend, diasSinPago: salida.sinPago });
    document.querySelectorAll("[data-motivo]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.motivo === salida.motivo));
    $("mt-lines").innerHTML = r.lines.filter((l) => l.amount > 0.5 || l.key === "aguinaldo").map((l) => `<tr><td>${l.label}<small>${l.note}</small></td><td class="mono">${fmt(l.amount)}</td></tr>`).join("");
    $("mt-total-label").textContent = r.despido ? "Si hoy te despiden sin causa" : "Si hoy renuncias";
    $("mt-total").textContent = fmt(r.total);
    $("mt-veinte").hidden = !r.despido;
    $("mt-veinte").innerHTML = `Además, en algunos casos (art. 50) aplican <b>20 días por año</b>: <b class="sun">${fmt(r.veinte)}</b> más. Pregunta en PROFEDET si es tu caso.`;
    $("mt-salida-note").innerHTML = r.despido
      ? `Si te despidieron sin causa, tienes <b>2 meses</b> para reclamar. La asesoría de la <a href="https://www.gob.mx/profedet" target="_blank" rel="noopener">PROFEDET</a> es gratuita. No firmes una renuncia que no escribiste.`
      : `Al renunciar te toca tu finiquito. La prima de antigüedad solo aplica si llevas 15 años o más.`;
    timeline({ sd, start, ag, v, p });
    FY.emit("metoca", { aguinaldo: ag.amount, agLeft, vacDays: v.days });
  }

  function timeline({ ag, v, p }) {
    const t = today(), ev = [];
    if (FY.quincena) ev.push({ d: FY.quincena.nextPayday(), t: "Tu próximo pago", n: "Según lo que pusiste en Tus datos." });
    const agDate = ley.diffDays(t, ag.deadline) >= 0 ? ag.deadline : new Date(t.getFullYear() + 1, 11, 19, 12);
    ev.push({ d: agDate, t: `Aguinaldo: ${fmt(ag.amount)}`, n: "Fecha límite para pagarlo (art. 87)." });
    ev.push({ d: v.nextDate, t: `Aniversario: ${v.nextDays} días de vacaciones`, n: `Más prima vacacional de ${fmt(v.nextDays * inputs().sd * inputs().prima)}.` });
    ev.push({ d: p.empresas, t: `Reparto de utilidades (PTU)`, n: `Hasta ${fmt(p.tope)} si tu empresa tuvo utilidades.` });
    ev.push({ d: new Date(t.getMonth() === 0 && t.getDate() === 1 ? t.getFullYear() : t.getFullYear() + 1, 0, 1, 12), t: "Nuevo salario mínimo", n: "Cada 1 de enero se actualiza. Revisa que tu sueldo no quede abajo." });
    ev.sort((a, b) => a.d - b.d);
    $("mt-timeline").innerHTML = ev.map((e) => {
      const n = ley.diffDays(t, e.d);
      return `<li><span class="when mono">${n === 0 ? "Hoy" : n === 1 ? "Mañana" : `${n} días`}</span><div><b>${e.t}</b><span class="mut small">${e.d.toLocaleDateString("es-MX", { day: "numeric", month: "short", year: "numeric" })} · ${e.n}</span></div></li>`;
    }).join("");
  }

  // ---------- controles ----------
  const pf = { "mt-salary": "sueldo", "mt-start": "inicio", "mt-zone": "zona", "mt-agdias": "agDias", "mt-prima": "prima" };
  const fill = () => Object.entries(pf).forEach(([id, key]) => { $(id).value = perfil[key]; });
  Object.entries(pf).forEach(([id, key]) => {
    const el = $(id);
    el.value = perfil[key];
    el.addEventListener("input", () => {
      if (key === "inicio") { if (!parse(el.value)) return; perfil.inicio = el.value; }
      else if (key === "zona") perfil.zona = el.value;
      else if (key === "agDias") perfil.agDias = FY.clamp(+el.value || 15, 15, 120);
      else if (key === "prima") perfil.prima = FY.clamp(+el.value || 25, 25, 200);
      else perfil.sueldo = FY.clamp(+el.value || 0, 0, 2e6);
      perfil.configurado = true; save(); render();
    });
    if (key === "agDias" || key === "prima") el.addEventListener("change", () => { el.value = perfil[key]; });
  });
  $("mt-start").max = iso(today());
  const sf = { "mt-end": "fin", "mt-pend": "pend", "mt-sinpago": "sinPago" };
  Object.entries(sf).forEach(([id, key]) => {
    const el = $(id);
    el.value = salida[key];
    el.addEventListener("input", () => {
      if (key === "fin") { if (!parse(el.value)) return; salida.fin = el.value; }
      else salida[key] = FY.clamp(+el.value || 0, 0, 365);
      save(); render();
    });
  });
  document.querySelectorAll("[data-motivo]").forEach((b) => b.addEventListener("click", () => { salida.motivo = b.dataset.motivo; save(); render(); FY.buzz(6); }));

  // ---------- checklist de derechos ----------
  const CHECK = [
    { id: "imss", t: "Revisa tus semanas cotizadas", d: "Confirma que tu patrón te tiene dado de alta en el IMSS y con tu sueldo real.", url: "https://www.imss.gob.mx" },
    { id: "afore", t: "Encuentra tu Afore", d: "Descarga AforeMóvil (CONSAR) y mira cuánto llevas para tu retiro.", url: "https://www.gob.mx/consar" },
    { id: "infonavit", t: "Consulta tu ahorro en Infonavit", d: "Tu patrón aporta 5% de tu salario a tu subcuenta de vivienda.", url: "https://www.infonavit.org.mx" },
    { id: "cfdi", t: "Guarda tus recibos de nómina", d: "Tus recibos (CFDI) son tu prueba si algún día tienes que reclamar.", url: "https://www.sat.gob.mx" },
    { id: "profedet", t: "Ten a la mano a PROFEDET", d: "Asesoría y defensa laboral gratuita del gobierno federal.", url: "https://www.gob.mx/profedet" },
    { id: "buro", t: "Pide tu reporte de crédito gratis", d: "Tienes derecho a uno gratuito cada 12 meses.", url: "https://www.burodecredito.com.mx" },
    { id: "cetes", t: "Abre tu cuenta de CETES", d: "Desde $100, sin comisiones, en la plataforma del gobierno.", url: "https://www.cetesdirecto.com" },
    { id: "fondo", t: "Arma tu fondo de emergencia", d: "Meta: 3 meses de gastos fijos en un lugar seguro." }
  ];
  const done = new Set(store.get("check", []));
  const box = $("mt-check");
  CHECK.forEach((c) => {
    const el = document.createElement("label");
    el.className = "mission";
    el.innerHTML = `<input type="checkbox" id="c-${c.id}"><div><b>${c.t}</b><p>${c.d}${c.url ? ` <a href="${c.url}" target="_blank" rel="noopener">Ir</a>` : ""}</p></div>`;
    const cb = el.querySelector("input");
    cb.checked = done.has(c.id);
    cb.addEventListener("change", () => { cb.checked ? done.add(c.id) : done.delete(c.id); store.set("check", [...done]); progress(); if (cb.checked) FY.buzz(10); });
    box.appendChild(el);
  });
  function progress() {
    $("mt-check-label").textContent = `${done.size} de ${CHECK.length}`;
    $("mt-check-bar").style.width = (done.size / CHECK.length * 100) + "%";
  }

  function wipe() { done.clear(); }
  function init() { progress(); render(); }
  // Vuelve a leer el perfil (bienvenida, "Tus datos" o respaldo).
  function reload() { Object.assign(perfil, store.get("perfil", {})); fill(); render(); }
  FY.derechos = { init, render, inputs, wipe, reload, aguinaldo: () => { const i = inputs(); return ley.aguinaldo({ sd: i.sd, start: i.start, at: today(), dias: i.dias }); } };
})(window.FY);
