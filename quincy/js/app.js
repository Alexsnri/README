// Quincy · arranque: secciones, marca de instituciones, retos recibidos, tasas, app instalable.
(function (FY) {
  const { $, store, CONFIG } = FY;
  const VIEWS = ["hoy", "derechos", "herramientas", "tanda", "futuro", "reto", "mas", "datos"];
  // Cuatro pestañas: las herramientas (tanda, futuro, reto, calculadoras) viven dentro de "Herramientas".
  const TAB = { tanda: "herramientas", futuro: "herramientas", reto: "herramientas", mas: "herramientas" };

  // ---------- secciones ----------
  function go(view, push) {
    if (!VIEWS.includes(view)) view = "hoy";
    VIEWS.forEach((v) => { $("v-" + v).hidden = v !== view; });
    const tab = TAB[view] || view;
    document.querySelectorAll("[data-tab]").forEach((b) => {
      if (b.dataset.tab === tab) b.setAttribute("aria-current", "page"); else b.removeAttribute("aria-current");
    });
    document.querySelectorAll("dialog.sheet[open]").forEach((d) => d.close());
    if (push !== false) { try { history.replaceState(null, "", "#" + view); } catch (e) {} }
    window.scrollTo(0, 0);
    if (view === "futuro") { FY.sim.sizeCanvas(); FY.sim.render(); FY.sim.startWarp(); }
    if (view === "hoy") FY.quincena.render();
    if (view === "derechos") FY.derechos.render();
    if (view === "tanda") FY.tanda.render();
    if (view === "reto") $("challenge").hidden = true;
    if (view === "datos" && FY.datosUI) FY.datosUI.refresh();
    store.set("view", view);
  }
  document.querySelectorAll("[data-go]").forEach((b) => b.addEventListener("click", (e) => { e.preventDefault(); go(b.dataset.go); FY.buzz(5); }));
  // ---------- hojas desde abajo (lo secundario se abre a demanda) ----------
  document.querySelectorAll("[data-sheet]").forEach((b) => b.addEventListener("click", () => {
    const d = $(b.dataset.sheet); if (!d) return;
    d.showModal(); FY.buzz(5);
    const f = d.querySelector("input"); if (f && matchMedia("(pointer: fine)").matches) f.focus();
  }));
  document.querySelectorAll("dialog.sheet").forEach((d) => {
    d.addEventListener("click", (e) => {
      // Toque fuera de la hoja, en la X, o en algo que abre otra pantalla: se cierra.
      if (e.target === d || e.target.closest("[data-close],[data-share],[data-go]")) d.close();
    });
  });
  addEventListener("hashchange", () => { const v = location.hash.slice(1); if (VIEWS.includes(v)) go(v, false); });

  // ---------- parámetros del enlace ----------
  const params = new URLSearchParams(location.search);
  // Marca de una institución: ?marca=Nombre&color=ffb547&cta=https://...&cta_txt=Texto
  const brand = Object.assign({}, store.get("brand", {}));
  if (params.has("marca")) {
    brand.name = params.get("marca").replace(/[<>]/g, "").slice(0, 30);
    const col = (params.get("color") || "").replace("#", "");
    brand.color = /^[0-9a-fA-F]{6}$/.test(col) ? col : "";
    const cta = params.get("cta") || "";
    brand.cta = /^https:\/\/[^\s"'<>]+$/.test(cta) ? cta : "";
    brand.ctaText = (params.get("cta_txt") || "").replace(/[<>]/g, "").slice(0, 60);
    brand.hideSalida = params.get("ocultar") === "salida";
    store.set("brand", brand);
  }
  if (brand.hideSalida) $("mt-salida-card").hidden = true;
  if (brand.name) {
    $("brand-x").hidden = false; $("brand-x").textContent = "× " + brand.name;
    if (brand.color) {
      const c = brand.color, rgb = [0, 2, 4].map((i) => parseInt(c.slice(i, i + 2), 16));
      const lum = (0.3 * rgb[0] + 0.59 * rgb[1] + 0.11 * rgb[2]) / 255;
      document.documentElement.style.setProperty("--sun", "#" + c);
      document.documentElement.style.setProperty("--sun-soft", `rgba(${rgb.join(",")},.14)`);
      document.documentElement.style.setProperty("--sun-ink", lum > 0.55 ? "#1a1205" : "#ffffff");
    }
    if (brand.cta) {
      const a = $("partner-cta");
      a.hidden = false; a.href = brand.cta;
      a.innerHTML = `<span></span><span class="btn btn-sun btn-sm">Ir</span>`;
      a.firstChild.textContent = brand.ctaText || `Empieza hoy con ${brand.name}`;
    }
  }
  // Reto recibido: ?reto=26&p=4
  const rn = parseInt(params.get("reto"), 10), rp = parseInt(params.get("p"), 10);
  if (rn > 0 && rp >= 0 && rp <= 5 && !FY.reto.result().done) {
    $("challenge-text").textContent = rn === FY.reto.today ? `Te retaron: sacaron ${rp}/5 en el Reto #${rn} de hoy. ¿Le ganas?` : `Te retaron con el Reto #${rn}. Juega el de hoy y compara.`;
    $("challenge").hidden = false;
  }
  // Llegó por una tarjeta o enlace compartido: ?ref=futuro|verde|recibo|aguinaldo|tanda|carta|wa…
  else if (params.get("ref") && params.get("ref") !== "recordatorio") {
    const REF = { futuro: ["futuro", "Tu amigo ya vio a su yo del futuro. ¿Y tú?", "Ver el mío"], carta: ["futuro", "Tu amigo ya vio a su yo del futuro. ¿Y tú?", "Ver el mío"],
      aguinaldo: ["derechos", "Tu amigo ya sabe cuánto le toca de aguinaldo. ¿Y tú?", "Calcular el mío"], tanda: ["tanda", "Tu amigo ya organizó su tanda. ¿Y tú?", "Armar la mía"] };
    const [view, txt, cta] = REF[params.get("ref")] || ["hoy", "Tu amigo ya sabe cuánto puede gastar hoy. ¿Y tú?", "Calcular el mío"];
    const b = $("challenge").querySelector("[data-go]");
    b.dataset.go = view; b.textContent = cta;
    b.addEventListener("click", () => { $("challenge").hidden = true; });
    $("challenge-text").textContent = txt;
    $("challenge").hidden = false;
  }
  $("challenge-x").addEventListener("click", () => { $("challenge").hidden = true; });
  if ([...params.keys()].length) { try { history.replaceState(null, "", location.pathname + location.hash); } catch (e) {} }

  // ---------- tasas que se actualizan solas ----------
  function applyRates(d) {
    if (!d || typeof d.cetes28 !== "number" || typeof d.inflacion !== "number") return;
    FY.RATES.cetes = d.cetes28; FY.RATES.inflacion = d.inflacion;
    if (typeof d.optimista === "number") FY.RATES.optimista = d.optimista;
    $("rates-stamp").textContent = `CETES ${FY.RATES.cetes.toFixed(2)}% · Inflación ${FY.RATES.inflacion.toFixed(2)}%`;
    $("veh-cetes").textContent = `${FY.RATES.cetes.toFixed(2)}% nominal`;
    $("veh-opt").textContent = `${FY.RATES.optimista.toFixed(1)}% supuesto`;
    if (d.cetes28_fuente) $("src-cetes").textContent = `${FY.RATES.cetes.toFixed(2)}%. ${d.cetes28_fuente}`;
    if (d.inflacion_fuente) $("src-inf").textContent = `${FY.RATES.inflacion.toFixed(2)}%. ${d.inflacion_fuente}`;
    FY.sim.render(); FY.quincena.render();
  }

  // ---------- borrar mis datos ----------
  $("wipe-ask").addEventListener("click", () => { $("wipe-confirm").hidden = false; $("wipe-ask").hidden = true; });
  $("wipe-no").addEventListener("click", () => { $("wipe-confirm").hidden = true; $("wipe-ask").hidden = false; });
  $("wipe-yes").addEventListener("click", () => {
    FY.perfil.clear();
    try { Object.keys(localStorage).filter((k) => k.startsWith("qc:")).forEach((k) => localStorage.removeItem(k)); } catch (e) {}
    location.replace(location.pathname + "#hoy"); location.reload();
  });

  // ---------- app instalable ----------
  let deferred = null;
  addEventListener("beforeinstallprompt", (e) => { e.preventDefault(); deferred = e; $("install").hidden = false; });
  $("install").addEventListener("click", async () => { if (!deferred) return; deferred.prompt(); try { await deferred.userChoice; } catch (e) {} deferred = null; $("install").hidden = true; });
  if ("serviceWorker" in navigator && window.isSecureContext && !CONFIG.EMBEDDED_VIEWER) navigator.serviceWorker.register("sw.js").catch(() => {});


  // Los botones que abren el selector de fotos también funcionan con teclado.
  document.querySelectorAll("label.btn[for]").forEach((l) => {
    l.tabIndex = 0; l.setAttribute("role", "button");
    l.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); const t = document.getElementById(l.htmlFor); if (t) t.click(); } });
  });

  // ---------- arranque ----------
  FY.sim.init();
  FY.quincena.init();
  FY.derechos.init();
  const tandaLink = FY.tanda.init();
  FY.reto.init();
  FY.share.init();
  FY.datosUI = FY.perfilUI.init();
  // La tanda nueva arranca con la misma frecuencia con la que te pagan.
  if (FY.perfil.exists() && !store.get("tandas", []).length) $("tn-freq").value = FY.perfil.get().pago.freq;
  const first = location.hash.slice(1);
  go(tandaLink ? "tanda" : VIEWS.includes(first) ? first : (store.get("view", "hoy")), false);
  FY.go = go;
  FY.bienvenida.init();
  fetch("data/rates.json", { cache: "no-cache" }).then((r) => (r.ok ? r.json() : null)).then(applyRates).catch(() => {});
  FY.go = go;
})(window.FY);
