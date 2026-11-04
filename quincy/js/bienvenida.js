// Quincy · bienvenida: la primera vez (sin perfil guardado) le das tu contexto a Quincy en menos de un minuto,
// una pregunta por pantalla, y al final te dice cuánto puedes gastar hoy y lo que ya desbloqueaste.
(function (FY) {
  const { fmt, perfil, ley, store } = FY;
  const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const parse = (s) => { const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || ""); return m ? new Date(+m[1], +m[2] - 1, +m[3], 12) : null; };
  const today = () => { const t = new Date(); return new Date(t.getFullYear(), t.getMonth(), t.getDate(), 12); };
  const num = (v) => Math.max(0, Math.min(1e7, Math.round(+String(v || "").replace(/[^\d.]/g, "") || 0)));
  const nice = (d) => d.toLocaleDateString("es-MX", { weekday: "short", day: "numeric", month: "short" });
  const LOCK = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="10" rx="2.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" stroke-width="2"/></svg>';

  // Sueldo que la persona ya escribió en la portada (?sueldo= o guardado en este navegador).
  function sueldoPortada() {
    const q = parseInt(new URLSearchParams(FY.INITIAL_SEARCH).get("sueldo"), 10);
    if (q > 0 && q < 2e6) return q;
    const p = store.get("portada", null);
    return p && p.sueldo > 0 && p.sueldo < 2e6 ? p.sueldo : 0;
  }

  const d = { freq: "quincenal", proximo: "", proxTocado: false, ingreso: 0, fijos: [], ahorro: 0, sueldo: sueldoPortada(), inicio: "", frontera: false, edad: "" };
  const suggest = (freq) => FY.quincena.period(freq, new Date()).next;
  let el = null, step = 0, editor = null;
  const STEPS = 5; // 0 hola · 1 pago · 2 ingreso · 3 fijos · 4 trabajo · 5 resultado

  function html() {
    return `
    <div class="onb-top">
      <button type="button" class="onb-back" id="onb-back" aria-label="Atrás"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>Atrás</button>
      <div class="onb-bar" id="onb-bar" role="progressbar" aria-label="Avance" aria-valuemin="1" aria-valuemax="4"><i></i><i></i><i></i><i></i></div>
    </div>
    <div class="onb-body">
      <section class="onb-step" data-s="0" aria-labelledby="onb-h0">
        <span class="onb-logo" aria-hidden="true"></span>
        <h1 id="onb-h0" tabindex="-1">Hola, soy Quincy</h1>
        <p class="onb-lede">Dime cómo te pagan y te digo cuánto puedes gastar hoy para llegar completo a tu siguiente pago. Y lo que te toca por ley.</p>
        <div class="privacy-card">${LOCK}<p><b>Tus datos se quedan en este teléfono.</b> Sin cuentas, sin servidores: nadie más los ve, ni nosotros. Los borras cuando quieras.</p></div>
        <div class="onb-actions">
          <button type="button" class="btn btn-sun onb-big" id="onb-start">Empezar (1 minuto)</button>
          <button type="button" class="btn btn-ghost onb-big" id="onb-example">Ver con un ejemplo</button>
        </div>
      </section>

      <section class="onb-step" data-s="1" aria-labelledby="onb-h1" hidden>
        <p class="onb-k">Paso 1 de 4</p>
        <h1 id="onb-h1" tabindex="-1">¿Cada cuánto te pagan?</h1>
        <div class="onb-opts" role="radiogroup" aria-labelledby="onb-h1">
          <button type="button" role="radio" data-freq="quincenal" aria-checked="true"><b>Cada quincena</b><span>El 15 y fin de mes</span></button>
          <button type="button" role="radio" data-freq="semanal" aria-checked="false"><b>Cada semana</b><span>Mismo día cada semana</span></button>
          <button type="button" role="radio" data-freq="mensual" aria-checked="false"><b>Cada mes</b><span>Una vez al mes</span></button>
        </div>
        <label class="onb-label" for="onb-next">¿Cuándo es tu próximo pago?</label>
        <input class="onb-input" type="date" id="onb-next">
        <div class="chips" id="onb-next-chips"></div>
        <div class="onb-actions"><button type="button" class="btn btn-sun onb-big onb-go">Siguiente</button></div>
      </section>

      <section class="onb-step" data-s="2" aria-labelledby="onb-h2" hidden>
        <p class="onb-k">Paso 2 de 4</p>
        <h1 id="onb-h2" tabindex="-1">¿Cuánto te llega cada pago?</h1>
        <p class="onb-lede">Lo que cae en tu cuenta, ya sin impuestos.</p>
        <div class="onb-money"><span aria-hidden="true">$</span><input id="onb-ingreso" type="text" inputmode="numeric" autocomplete="off" placeholder="7,000" aria-labelledby="onb-h2" enterkeyhint="next"></div>
        <p class="onb-err" id="onb-ingreso-err" role="alert"></p>
        <div class="onb-actions"><button type="button" class="btn btn-sun onb-big onb-go">Siguiente</button></div>
      </section>

      <section class="onb-step" data-s="3" aria-labelledby="onb-h3" hidden>
        <p class="onb-k">Paso 3 de 4</p>
        <h1 id="onb-h3" tabindex="-1">Tus pagos fijos hasta tu siguiente pago</h1>
        <p class="onb-lede">Toca los que tienes y pon cuánto. Si no tienes, sigue.</p>
        <div id="onb-fijos" class="fijos" role="group" aria-labelledby="onb-h3"></div>
        <label class="onb-label" for="onb-ahorro">¿Cuánto quieres ahorrar cada pago?</label>
        <div class="onb-money sm"><span aria-hidden="true">$</span><input id="onb-ahorro" type="text" inputmode="numeric" autocomplete="off" placeholder="0" enterkeyhint="next"></div>
        <div class="chips" id="onb-ahorro-chips"></div>
        <div class="onb-actions"><button type="button" class="btn btn-sun onb-big onb-go">Siguiente</button></div>
      </section>

      <section class="onb-step" data-s="4" aria-labelledby="onb-h4" hidden>
        <p class="onb-k">Paso 4 de 4 · opcional</p>
        <h1 id="onb-h4" tabindex="-1">Tu trabajo</h1>
        <p class="onb-lede">Para calcular tu aguinaldo, tus vacaciones y tu yo de 65. Te lo puedes saltar.</p>
        <label class="onb-label" for="onb-sueldo">Sueldo mensual, antes de impuestos</label>
        <div class="onb-money sm"><span aria-hidden="true">$</span><input id="onb-sueldo" type="text" inputmode="numeric" autocomplete="off" placeholder="15,000"></div>
        <label class="onb-label" for="onb-inicio">¿Cuándo entraste a trabajar ahí?</label>
        <input class="onb-input" type="date" id="onb-inicio">
        <label class="onb-switch"><input type="checkbox" id="onb-frontera"> <span>Trabajo en la Zona Libre de la Frontera Norte</span></label>
        <label class="onb-label" for="onb-edad">Tu edad</label>
        <input class="onb-input" type="number" inputmode="numeric" id="onb-edad" min="18" max="60" placeholder="28">
        <div class="onb-actions two-b">
          <button type="button" class="btn btn-ghost onb-big" id="onb-skip">Saltar</button>
          <button type="button" class="btn btn-sun onb-big onb-go">Listo</button>
        </div>
      </section>

      <section class="onb-step onb-final" data-s="5" aria-labelledby="onb-h5" hidden>
        <p class="onb-k">Listo</p>
        <h1 id="onb-h5" tabindex="-1">Hoy puedes gastar</h1>
        <p class="onb-reveal mono" id="onb-reveal" aria-live="polite">$0</p>
        <p class="onb-lede" id="onb-reveal-sub"></p>
        <div class="onb-unlocks" id="onb-unlocks"></div>
        <div class="card avisos-card" id="onb-avisos"></div>
        <div class="onb-actions"><button type="button" class="btn btn-sun onb-big" id="onb-enter">Entrar a Quincy</button></div>
      </section>
    </div>`;
  }

  const $o = (sel) => el.querySelector(sel);
  const fmtIn = (input) => {
    input.addEventListener("input", () => {
      const raw = input.value.replace(/\.\d{0,2}\s*$/, "").replace(/[^\d]/g, "").slice(0, 8), pretty = raw ? (+raw).toLocaleString("es-MX") : "";
      if (input.value !== pretty) { const fromEnd = input.value.length - input.selectionStart; input.value = pretty; const p = Math.max(0, pretty.length - fromEnd); try { input.setSelectionRange(p, p); } catch (e) {} }
    });
  };

  function nextChips() {
    const a = suggest(d.freq), b = FY.quincena.period(d.freq, FY.addDays(a, 1)).next;
    if (!d.proxTocado) { d.proximo = ""; $o("#onb-next").value = iso(a); }
    $o("#onb-next-chips").innerHTML = [a, b].map((x) => `<button type="button" class="chip-btn" data-date="${iso(x)}" aria-pressed="${$o("#onb-next").value === iso(x)}">${nice(x)}</button>`).join("");
  }
  function ahorroChips() {
    const inc = d.ingreso || 0;
    const opts = [["Nada por ahora", 0], ["5%", Math.round(inc * 0.05 / 50) * 50], ["10%", Math.round(inc * 0.1 / 50) * 50]];
    $o("#onb-ahorro-chips").innerHTML = opts.map(([n, v]) => `<button type="button" class="chip-btn" data-ahorro="${v}">${n}${v ? ` <small>${fmt(v)}</small>` : ""}</button>`).join("");
  }

  function go(n) {
    // Validación del paso actual antes de avanzar.
    if (n > step && step === 2) {
      d.ingreso = num($o("#onb-ingreso").value);
      if (!d.ingreso) { $o("#onb-ingreso-err").textContent = "Escribe cuánto te llega para poder calcular."; $o("#onb-ingreso").focus(); return; }
      $o("#onb-ingreso-err").textContent = "";
    }
    if (n > step && step === 1) { const v = $o("#onb-next").value; d.proximo = parse(v) ? v : ""; }
    if (n > step && step === 3) d.ahorro = num($o("#onb-ahorro").value);
    if (n === 5 && step === 4) { d.sueldo = num($o("#onb-sueldo").value); d.inicio = parse($o("#onb-inicio").value) ? $o("#onb-inicio").value : ""; d.frontera = $o("#onb-frontera").checked; d.edad = Math.round(+$o("#onb-edad").value) || ""; }
    step = n;
    el.querySelectorAll(".onb-step").forEach((s) => { s.hidden = +s.dataset.s !== n; });
    el.dataset.step = n;
    const bar = $o("#onb-bar");
    bar.hidden = n === 0 || n === 5; $o("#onb-back").hidden = n === 0 || n === 5;
    [...bar.children].forEach((b, i) => b.classList.toggle("on", i < n));
    bar.setAttribute("aria-valuenow", Math.min(4, Math.max(1, n)));
    if (n === 3) ahorroChips();
    if (n === 5) finish();
    const first = { 1: "#onb-h1", 2: "#onb-ingreso", 3: "#onb-h3", 4: "#onb-h4" }[n] || `#onb-h${n}`;
    requestAnimationFrame(() => { const f = $o(first); if (f) f.focus({ preventScroll: false }); el.scrollTop = 0; });
  }

  // ---------- resultado ----------
  function finish() {
    const t = today(), sd = d.sueldo / 30;
    const yo = perfil.set({
      ejemplo: false, creado: iso(t),
      pago: { freq: d.freq, proximo: d.proximo, ingreso: d.ingreso, fijos: d.fijos.filter((f) => f.amt > 0), ahorro: d.ahorro, configurado: true },
      trabajo: d.sueldo ? { sueldo: d.sueldo, inicio: d.inicio, zona: d.frontera ? "frontera" : "general", configurado: true } : { configurado: false },
      futuro: Object.assign({}, perfil.DEF.futuro, d.edad >= 18 && d.edad <= 60 ? { age: d.edad, retire: Math.max(65, d.edad + 2) } : {})
    });
    const p = FY.quincena.period(d.freq, new Date(), d.proximo);
    const available = Math.max(0, d.ingreso - perfil.sumFijos(yo.pago.fijos) - d.ahorro), limit = available / p.daysLeft;
    $o("#onb-reveal-sub").textContent = available > 0
      ? `Faltan ${p.daysLeft} ${p.daysLeft === 1 ? "día" : "días"} para tu pago (${nice(p.next)}). Si hoy gastas menos, mañana tienes más.`
      : "Tus pagos fijos y tu ahorro se comen todo tu pago. Revisa tus números en Tus datos.";
    countUp($o("#onb-reveal"), limit);
    const cards = [];
    cards.push(`<div class="unl"><span>Días para tu pago</span><b class="mono">${p.daysLeft}</b><small>${nice(p.next)}</small></div>`);
    if (d.sueldo) {
      const start = parse(d.inicio) || new Date(t.getFullYear() - 1, 0, 1, 12);
      const ag = ley.aguinaldo({ sd, start, at: t }), left = ley.diffDays(t, ag.deadline);
      cards.push(`<div class="unl"><span>Tu aguinaldo</span><b class="mono sun">${fmt(ag.amount)}</b><small>${left >= 0 ? `a más tardar el 19 dic · faltan ${left} días` : "ya te lo debieron pagar"}</small></div>`);
      if (parse(d.inicio)) { const v = ley.vacaciones({ sd, start, at: t }); cards.push(`<div class="unl"><span>Tus vacaciones</span><b class="mono">${v.years >= 1 ? `${v.days} días` : "12 días"}</b><small>${v.years >= 1 ? `y ${fmt(v.prima)} de prima` : "al cumplir tu primer año"}</small></div>`); }
    } else cards.push(`<button type="button" class="unl unl-add" id="onb-add-job"><span>Tu aguinaldo</span><b>Pon tu sueldo</b><small>y te digo cuánto te toca</small></button>`);
    $o("#onb-unlocks").innerHTML = cards.join("");
    const add = $o("#onb-add-job"); if (add) add.addEventListener("click", () => go(4));
    FY.perfilUI.avisos($o("#onb-avisos"));
    FY.confetti();
  }
  function countUp(node, to) {
    if (FY.reduced) { node.textContent = fmt(to); return; }
    const t0 = performance.now(), dur = 1100;
    (function f(now) { const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3); node.textContent = fmt(to * e); if (k < 1) requestAnimationFrame(f); })(t0);
  }

  // ---------- abrir y cerrar ----------
  const bg = () => [document.querySelector("main"), document.querySelector("header.top"), document.querySelector(".tabbar"), document.getElementById("challenge")].filter(Boolean);
  function close() {
    el.hidden = true; document.body.classList.remove("onb-open");
    bg().forEach((n) => { n.inert = false; n.removeAttribute("aria-hidden"); });
    Object.assign(FY.state, store.get("state", {}));
    const a = document.getElementById("age"); if (a) { a.value = FY.state.age; document.getElementById("retire").value = FY.state.retire; }
    FY.quincena.reload(); FY.derechos.reload(); FY.sim.render();
    if (FY.datosUI) FY.datosUI.refresh();
    if (FY.go) FY.go("hoy");
  }
  function open(at) {
    if (!el) build();
    el.hidden = false; document.body.classList.add("onb-open");
    bg().forEach((n) => { n.inert = true; n.setAttribute("aria-hidden", "true"); });
    go(at || 0);
  }
  function build() {
    el = document.createElement("div");
    el.className = "onb"; el.id = "onb"; el.setAttribute("role", "dialog"); el.setAttribute("aria-modal", "true"); el.setAttribute("aria-label", "Bienvenida a Quincy");
    el.innerHTML = html(); el.hidden = true;
    document.body.appendChild(el);
    $o("#onb-start").addEventListener("click", () => go(1));
    $o("#onb-example").addEventListener("click", () => {
      const t = today();
      perfil.set({ ejemplo: true, pago: Object.assign({}, perfil.DEF.pago), futuro: Object.assign({}, perfil.DEF.futuro),
        trabajo: Object.assign({}, perfil.DEF.trabajo, { sueldo: d.sueldo || 15000, inicio: iso(new Date(t.getFullYear() - 3, t.getMonth() - 4, 1, 12)) }) });
      close(); FY.toast("Son números de ejemplo. Pon los tuyos cuando quieras.");
    });
    $o("#onb-back").addEventListener("click", () => go(Math.max(0, step - 1)));
    el.querySelectorAll(".onb-go").forEach((b) => b.addEventListener("click", () => go(step + 1)));
    $o("#onb-skip").addEventListener("click", () => { $o("#onb-sueldo").value = ""; $o("#onb-inicio").value = ""; $o("#onb-edad").value = ""; go(5); });
    $o("#onb-enter").addEventListener("click", close);
    el.querySelectorAll("[data-freq]").forEach((b) => b.addEventListener("click", () => {
      d.freq = b.dataset.freq;
      el.querySelectorAll("[data-freq]").forEach((x) => x.setAttribute("aria-checked", String(x === b)));
      nextChips();
    }));
    // Flechas dentro del grupo de opciones, como un radio de verdad.
    $o(".onb-opts").addEventListener("keydown", (e) => {
      if (!["ArrowDown", "ArrowUp", "ArrowRight", "ArrowLeft"].includes(e.key)) return;
      const all = [...el.querySelectorAll("[data-freq]")], i = all.indexOf(document.activeElement);
      const n = all[(i + (e.key === "ArrowDown" || e.key === "ArrowRight" ? 1 : all.length - 1)) % all.length];
      e.preventDefault(); n.focus(); n.click();
    });
    $o("#onb-next").min = iso(today());
    $o("#onb-next").addEventListener("input", () => { d.proxTocado = true; nextChips(); });
    $o("#onb-next-chips").addEventListener("click", (e) => { const c = e.target.closest("[data-date]"); if (!c) return; $o("#onb-next").value = c.dataset.date; d.proxTocado = true; nextChips(); });
    ["#onb-ingreso", "#onb-ahorro", "#onb-sueldo"].forEach((s) => fmtIn($o(s)));
    $o("#onb-ahorro-chips").addEventListener("click", (e) => { const c = e.target.closest("[data-ahorro]"); if (!c) return; $o("#onb-ahorro").value = (+c.dataset.ahorro).toLocaleString("es-MX"); });
    editor = FY.perfilUI.fijosEditor($o("#onb-fijos"), [], (list) => { d.fijos = list; }, { id: "onb" });
    if (d.sueldo) $o("#onb-sueldo").value = d.sueldo.toLocaleString("es-MX");
    $o("#onb-inicio").max = iso(today());
    // Enter avanza (menos en los botones, que ya hacen lo suyo).
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && e.target.tagName === "INPUT" && e.target.type !== "checkbox" && step >= 1 && step <= 4) { e.preventDefault(); go(step + 1); }
    });
    nextChips();
  }

  // Sin perfil: bienvenida. Con un enlace de tanda o de reto se entra directo (vienen a ver eso) y la bienvenida queda para después.
  function init() {
    const ps = new URLSearchParams(FY.INITIAL_SEARCH);
    document.querySelectorAll("[data-onb]").forEach((b) => b.addEventListener("click", () => open(1)));
    if (!perfil.exists() && !ps.has("t") && !ps.has("reto")) { open(0); return true; }
    // Llegó con un sueldo de la portada y aún no tiene datos de trabajo: se lo ponemos.
    const s = sueldoPortada(), yo = perfil.get();
    if (s && yo && !yo.trabajo.configurado) { perfil.update("trabajo", { sueldo: s, configurado: true }); FY.derechos.reload(); }
    return false;
  }

  FY.bienvenida = { init, open };
})(window.FY);
