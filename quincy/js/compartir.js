// Quincy · compartir en 1 toque desde cualquier calculadora: WhatsApp con enlace ?ref=wa, tarjeta vertical
// 1080×1920 para historias, "Wrapped" (varias tarjetas seguidas), aviso al llegar por un enlace compartido y recordatorios .ics.
(function (FY) {
  const CW = 1080, CH = 1920;
  const SITE = FY.CONFIG.SITE;
  const SHORT = SITE.replace(/^https?:\/\//, "").replace(/\/$/, "");
  const el = (tag, attrs, html) => { const e = document.createElement(tag); Object.assign(e, attrs || {}); if (html != null) e.innerHTML = html; return e; };

  // ---------- enlaces ----------
  // Enlace público de la página actual (o de `path`, relativo al sitio) con ?ref=…; siempre apunta al sitio publicado.
  function link(ref, path) {
    const base = new URL(SITE).pathname, here = location.pathname;
    const rel = path != null ? path : (here.startsWith(base) ? here.slice(base.length) : here.split("/quincy/")[1] || "").replace(/index\.html$/, "");
    const u = new URL(rel, SITE);
    if (ref) u.searchParams.set("ref", ref);
    return u.toString();
  }
  const waURL = (text) => "https://wa.me/?text=" + encodeURIComponent(text);

  // ---------- tarjeta para historias ----------
  function roundRect(x, l, t, w, h, r) { x.beginPath(); x.moveTo(l + r, t); x.arcTo(l + w, t, l + w, t + h, r); x.arcTo(l + w, t + h, l, t + h, r); x.arcTo(l, t + h, l, t, r); x.arcTo(l, t, l + w, t, r); x.closePath(); }
  function wrap(x, s, y, font, color, maxW = 920, align = "center") {
    x.font = font; x.fillStyle = color; x.textAlign = align;
    const words = String(s).split(" "), lines = []; let line = "";
    words.forEach((w) => { const t = line ? line + " " + w : w; if (x.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t; });
    lines.push(line);
    const lh = parseInt(font.match(/(\d+)px/)[1], 10) * 1.14;
    lines.forEach((l, i) => x.fillText(l, CW / 2, y + i * lh));
    return y + lines.length * lh;
  }
  // Ajusta el tamaño de letra para que el número quepa en una línea.
  function fitFont(x, s, weight, family, max, maxW) {
    let size = max;
    do { x.font = `${weight} ${size}px ${family}`; size -= 6; } while (x.measureText(s).width > maxW && size > 40);
    return x.font;
  }
  function backdrop(x, tone) {
    const g = x.createLinearGradient(0, 0, CW, CH);
    g.addColorStop(0, tone === "tide" ? "#0f3a45" : "#15404f"); g.addColorStop(0.55, "#0b1f2b"); g.addColorStop(1, "#07121a");
    x.fillStyle = g; x.fillRect(0, 0, CW, CH);
    const glow = (cx, cy, r, c) => { const rg = x.createRadialGradient(cx, cy, 0, cx, cy, r); rg.addColorStop(0, c); rg.addColorStop(1, "rgba(7,18,26,0)"); x.fillStyle = rg; x.fillRect(0, 0, CW, CH); };
    glow(880, 260, 620, tone === "tide" ? "rgba(90,214,200,.30)" : "rgba(255,181,71,.30)");
    glow(120, 1500, 700, tone === "tide" ? "rgba(255,181,71,.16)" : "rgba(90,214,200,.18)");
    // Anillos orbitales: el mismo gesto de la marca.
    x.save(); x.translate(CW / 2, 980);
    for (let i = 0; i < 3; i++) { x.strokeStyle = i % 2 ? "rgba(90,214,200,.16)" : "rgba(255,181,71,.18)"; x.lineWidth = 3; x.beginPath(); x.ellipse(0, 0, 420 + i * 110, 140 + i * 40, -0.22, 0, Math.PI * 2); x.stroke(); }
    x.restore();
  }
  function brand(x) {
    // logo arriba
    const lg = x.createRadialGradient(118, 148, 4, 128, 158, 34); lg.addColorStop(0, "#ffd08a"); lg.addColorStop(0.6, "#ffb547"); lg.addColorStop(1, "#e2702e");
    x.fillStyle = lg; x.beginPath(); x.arc(128, 158, 30, 0, Math.PI * 2); x.fill();
    x.font = "800 50px Unbounded, 'Arial Black', sans-serif"; x.textAlign = "left"; x.fillStyle = "#eaf3f4"; x.fillText("quincy", 178, 176);
    x.fillStyle = "#ffb547"; x.fillText(".", 178 + x.measureText("quincy").width, 176);
  }
  function footer(x, cta) {
    x.fillStyle = "rgba(7,18,26,.82)"; roundRect(x, 80, CH - 300, CW - 160, 200, 44); x.fill();
    x.strokeStyle = "rgba(255,181,71,.55)"; x.lineWidth = 3; roundRect(x, 80, CH - 300, CW - 160, 200, 44); x.stroke();
    wrap(x, cta || "¿Y a ti cuánto te toca?", CH - 212, "800 48px Unbounded, 'Arial Black', sans-serif", "#eaf3f4");
    wrap(x, SHORT, CH - 145, "600 32px 'JetBrains Mono', monospace", "#5ad6c8");
  }
  // d: { kicker, big, line, sub, cta, tone }
  async function card(d) {
    try { if (document.fonts && document.fonts.ready) await document.fonts.ready; } catch (e) {}
    const cv = document.createElement("canvas"); cv.width = CW; cv.height = CH;
    const x = cv.getContext("2d");
    backdrop(x, d.tone); brand(x);
    let y = wrap(x, String(d.kicker || "").toUpperCase(), 640, "600 40px 'JetBrains Mono', monospace", "#5ad6c8", 900);
    x.textAlign = "center"; x.fillStyle = d.tone === "tide" ? "#5ad6c8" : "#ffb547";
    x.font = fitFont(x, d.big, 800, "Unbounded, 'Arial Black', sans-serif", 230, 940);
    x.shadowColor = d.tone === "tide" ? "rgba(90,214,200,.45)" : "rgba(255,181,71,.45)"; x.shadowBlur = 60;
    x.fillText(d.big, CW / 2, y + 230); x.shadowBlur = 0;
    y = wrap(x, d.line || "", y + 380, "700 62px Figtree, sans-serif", "#ffffff", 900);
    if (d.sub) wrap(x, d.sub, y + 30, "500 42px Figtree, sans-serif", "#b9ced4", 860);
    footer(x, d.cta);
    return new Promise((res) => cv.toBlob(res, "image/jpeg", 0.9));
  }

  // ---------- subir a historias ----------
  // El menú de compartir del teléfono solo se abre si se llama justo al tocar (sin esperar a dibujar la tarjeta),
  // por eso las tarjetas se preparan antes. Se manda solo la imagen: así Instagram ofrece "Historia" directo.
  const ext = (b) => (b.type === "image/png" ? ".png" : ".jpg");
  const toFile = (b, name) => new File([b], name + ext(b), { type: b.type || "image/jpeg" });
  const canShareFiles = () => { try { return !!(navigator.share && navigator.canShare && navigator.canShare({ files: [toFile(new Blob(["x"], { type: "image/png" }), "x")] })); } catch (e) { return false; } };
  const inApp = /Instagram|FBAN|FBAV|WhatsApp|Line\/|TikTok|musical_ly/i.test(navigator.userAgent || "");
  // Debe llamarse dentro del toque, sin awaits antes. Devuelve una promesa: true si se compartió.
  function shareStory(blobs, name, linkTxt) {
    if (linkTxt) { try { navigator.clipboard.writeText(linkTxt).catch(() => {}); } catch (e) {} }
    const files = blobs.map((b, i) => toFile(b, `${name}${blobs.length > 1 ? "-" + (i + 1) : ""}`));
    return navigator.share({ files }).then(() => {
      FY.toast(linkTxt ? "Tip: en tu historia agrega el sticker de enlace y pega el link (ya lo copiamos)" : "¡Listo!");
      FY.emit && FY.emit("shared", "historia"); return true;
    }).catch((e) => { if (e && e.name !== "AbortError") FY.toast("No se pudo abrir el menú. Guarda la imagen y súbela desde Instagram."); return false; });
  }
  function downloadAll(blobs, name) {
    blobs.forEach((b, i) => setTimeout(() => FY.download(b, `${name}${blobs.length > 1 ? "-" + (i + 1) : ""}${ext(b)}`), i * 350));
  }
  // Hoja con la vista previa cuando no se puede subir directo (computadora, navegador dentro de otra app) o la tarjeta no estaba lista.
  let sheet = null;
  function storySheet(blob, name, linkTxt) {
    if (!sheet) {
      sheet = el("dialog", { className: "wrapped story-sheet" }, `
        <button class="wr-x" type="button" aria-label="Cerrar">×</button>
        <div class="wr-stage"><img alt="Tu tarjeta para historias" class="wr-img"></div>
        <p class="ss-help"></p>
        <div class="wr-actions"><button class="btn btn-sun ss-ig" type="button">Subir a Instagram</button><button class="btn btn-ghost ss-dl" type="button">Descargar</button></div>
        <button class="btn btn-ghost ss-copy" type="button">Copiar enlace para el sticker</button>`);
      document.body.append(sheet);
      sheet.querySelector(".wr-x").addEventListener("click", () => sheet.close());
      sheet.addEventListener("click", (e) => { if (e.target === sheet) sheet.close(); });
    }
    const url = URL.createObjectURL(blob), direct = canShareFiles();
    sheet.querySelector(".wr-img").src = url;
    sheet.querySelector(".ss-ig").hidden = !direct;
    sheet.querySelector(".ss-help").textContent = direct
      ? "Toca «Subir a Instagram», elige Instagram y luego «Historia». Agrega el sticker de enlace con tu link."
      : inApp ? "Este navegador (dentro de otra app) no deja abrir Instagram directo. Mantén presionada la imagen para guardarla, o abre esta página en Chrome o Safari."
      : "Desde aquí no se puede abrir Instagram directo. Descarga la imagen o abre esta página en tu celular.";
    sheet.querySelector(".ss-ig").onclick = () => shareStory([blob], name, linkTxt).then((ok) => { if (ok) sheet.close(); });
    sheet.querySelector(".ss-dl").onclick = () => downloadAll([blob], name);
    sheet.querySelector(".ss-copy").onclick = () => FY.copyText(linkTxt);
    sheet.onclose = () => URL.revokeObjectURL(url);
    if (!sheet.open) sheet.showModal();
  }

  // ---------- barra de compartir ----------
  // get(): { ref, wa (texto sin enlace), card: {kicker,big,line,sub}, name, wrapped?: () => [cards] }
  const IC = {
    wa: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a.9.9 0 0 0-.7.3 2.8 2.8 0 0 0-.9 2.1 4.9 4.9 0 0 0 1 2.6 11.2 11.2 0 0 0 4.3 3.8c1.6.7 2.2.7 3 .6a2.6 2.6 0 0 0 1.7-1.2 2.1 2.1 0 0 0 .1-1.2c0-.1-.2-.2-.4-.3Z"/></svg>',
    story: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="2.5" width="12" height="19" rx="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 7v7m-3-3 3 3 3-3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    spark: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2l2.2 6.3L20.5 10l-6.3 2.2L12 18.5l-2.2-6.3L3.5 10l6.3-1.7Z"/></svg>'
  };
  function bar(host, get) {
    const box = el("div", { className: "share-bar" });
    const wa = el("a", { className: "sbtn sbtn-wa", target: "_blank", rel: "noopener" }, IC.wa + "<span>WhatsApp</span>");
    const st = el("button", { className: "sbtn sbtn-story", type: "button" }, IC.story + "<span>Historias</span>");
    box.append(wa, st);
    const refresh = () => { const d = get(); wa.href = waURL(`${d.wa} ${link(d.ref || "wa")}`); };
    wa.addEventListener("pointerdown", refresh); wa.addEventListener("focus", refresh);
    wa.addEventListener("click", () => { refresh(); FY.emit && FY.emit("shared", "wa"); });
    // Tarjeta preparada de antemano (se rehace cuando cambian los datos) para abrir el menú en el mismo toque.
    let ready = null, timer = 0, job = 0;
    const keyOf = (d) => JSON.stringify(d.card);
    const prebuild = (wait) => {
      clearTimeout(timer);
      timer = setTimeout(async () => {
        const d = get(), key = keyOf(d), n = ++job;
        if (ready && ready.key === key) return;
        try { const blob = await card(d.card); if (n === job) ready = { key, blob }; } catch (e) {}
      }, wait);
    };
    const form = host.closest("form, .calc, main") || document;
    form.addEventListener("input", () => prebuild(700)); form.addEventListener("change", () => prebuild(700));
    // Se prepara con la primera señal de la persona (tocar, desplazarse, escribir), no al cargar, para no frenar la página.
    const first = () => { ["pointerdown", "keydown", "scroll", "touchstart"].forEach((t) => removeEventListener(t, first, true)); prebuild(250); };
    ["pointerdown", "keydown", "scroll", "touchstart"].forEach((t) => addEventListener(t, first, { capture: true, passive: true }));
    st.addEventListener("click", async () => {
      const d = get(), name = d.name || "quincy", linkTxt = link(d.ref === "wa" || !d.ref ? "historia" : d.ref);
      if (ready && ready.key === keyOf(d) && canShareFiles()) { shareStory([ready.blob], name, linkTxt); return; }
      st.disabled = true; st.classList.add("busy");
      try { const blob = await card(d.card); ready = { key: keyOf(d), blob }; storySheet(blob, name, linkTxt); }
      catch (e) { FY.toast("No pude crear la tarjeta. Inténtalo de nuevo."); }
      st.disabled = false; st.classList.remove("busy");
    });
    if (get().wrapped) {
      const w = el("button", { className: "sbtn sbtn-wrapped", type: "button" }, IC.spark + "<span>Tu Wrapped</span>");
      w.addEventListener("click", () => { const d = get(); wrapped(d.wrapped(), link("wrapped"), d.name || "quincy"); });
      box.append(w);
    }
    refresh();
    host.append(box);
    return { refresh };
  }

  // ---------- Wrapped: varias tarjetas tipo historia ----------
  let wrapDlg = null;
  async function wrapped(cards, text, name) {
    if (!wrapDlg) {
      wrapDlg = el("dialog", { className: "wrapped" }, `
        <div class="wr-bars" aria-hidden="true"></div>
        <button class="wr-x" type="button" aria-label="Cerrar">×</button>
        <div class="wr-stage"><img alt="" class="wr-img"><button class="wr-prev" type="button" aria-label="Anterior"></button><button class="wr-next" type="button" aria-label="Siguiente"></button></div>
        <div class="wr-actions"><button class="btn btn-sun wr-share" type="button">Subir esta a Instagram</button><button class="btn btn-ghost wr-dl" type="button">Descargar todas</button></div>`);
      document.body.append(wrapDlg);
      wrapDlg.querySelector(".wr-x").addEventListener("click", () => wrapDlg.close());
      wrapDlg.addEventListener("click", (e) => { if (e.target === wrapDlg) wrapDlg.close(); });
    }
    const D = wrapDlg, img = D.querySelector(".wr-img"), bars = D.querySelector(".wr-bars");
    bars.innerHTML = cards.map(() => "<i></i>").join("");
    img.src = ""; img.alt = "Creando tus tarjetas…";
    if (!D.open) D.showModal();
    const blobs = await Promise.all(cards.map(card));
    const urls = blobs.map((b) => URL.createObjectURL(b));
    let i = 0, timer = null;
    const show = (k) => {
      i = (k + cards.length) % cards.length;
      img.src = urls[i]; img.alt = `${cards[i].kicker}: ${cards[i].big}. ${cards[i].line || ""}`;
      [...bars.children].forEach((b, j) => b.className = j < i ? "done" : j === i ? "on" : "");
      clearTimeout(timer); if (!FY.reduced) timer = setTimeout(() => { if (D.open && i < cards.length - 1) show(i + 1); }, 4200);
    };
    D.querySelector(".wr-prev").onclick = () => show(i - 1);
    D.querySelector(".wr-next").onclick = () => show(i + 1);
    D.onkeydown = (e) => { if (e.key === "ArrowRight") show(i + 1); if (e.key === "ArrowLeft") show(i - 1); };
    // Una por una: Instagram sube a historias una imagen a la vez.
    const direct = canShareFiles();
    D.querySelector(".wr-share").textContent = direct ? "Subir esta a Instagram" : "Descargar esta";
    D.querySelector(".wr-share").onclick = () => { clearTimeout(timer); if (direct) shareStory([blobs[i]], `${name}-wrapped-${i + 1}`, text); else FY.download(blobs[i], `${name}-wrapped-${i + 1}${ext(blobs[i])}`); };
    D.querySelector(".wr-dl").onclick = () => downloadAll(blobs, name + "-wrapped");
    D.onclose = () => { clearTimeout(timer); urls.forEach((u) => URL.revokeObjectURL(u)); };
    show(0);
  }

  // ---------- llegaste por un enlace compartido ----------
  // Muestra "Tu amigo ya sabe cuánto le toca, ¿y tú?" y lleva al primer campo de la calculadora.
  function welcome(host, focusSel, msg) {
    const ref = new URLSearchParams(FY.INITIAL_SEARCH || location.search).get("ref");
    if (!ref || !host) return false;
    const BY_REF = { futuro: "Tu amigo ya vio a su yo del futuro.", carta: "Tu amigo ya vio a su yo del futuro.", verde: "Tu amigo ya sabe cuánto puede gastar hoy.",
      recibo: "Tu amigo ya sabe cuánto puede gastar hoy.", tanda: "Tu amigo ya organizó su tanda.", reto: "Tu amigo ya jugó el reto de hoy." };
    const b = el("div", { className: "ref-hello", role: "status" },
      `<span class="ref-dot" aria-hidden="true"></span><p><b>${BY_REF[ref] || msg || "Tu amigo ya sabe cuánto le toca."}</b> ¿Y tú? Calcula lo tuyo en 10 segundos.</p><button class="btn btn-sun btn-sm" type="button">Calcular</button><button class="ref-x" type="button" aria-label="Cerrar">×</button>`);
    b.querySelector(".btn").addEventListener("click", () => { const f = document.querySelector(focusSel); if (f) { f.scrollIntoView({ block: "center", behavior: FY.reduced ? "auto" : "smooth" }); f.focus({ preventScroll: true }); } b.remove(); });
    b.querySelector(".ref-x").addEventListener("click", () => b.remove());
    host.prepend(b);
    return true;
  }

  // ---------- recordatorio en el calendario (.ics) ----------
  function ics({ title, date, desc, alarmDays = 1, name = "quincy-recordatorio" }) {
    const p = (n) => String(n).padStart(2, "0");
    const d = `${date.getFullYear()}${p(date.getMonth() + 1)}${p(date.getDate())}`;
    const e = new Date(date); e.setDate(e.getDate() + 1);
    const d2 = `${e.getFullYear()}${p(e.getMonth() + 1)}${p(e.getDate())}`;
    const now = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+/, "");
    const esc = (s) => String(s).replace(/([,;\\])/g, "\\$1").replace(/\n/g, "\\n");
    const body = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Quincy//ES", "CALSCALE:GREGORIAN", "BEGIN:VEVENT",
      `UID:${d}-${name}@quincy`, `DTSTAMP:${now}`, `DTSTART;VALUE=DATE:${d}`, `DTEND;VALUE=DATE:${d2}`,
      `SUMMARY:${esc(title)}`, `DESCRIPTION:${esc(desc)}`,
      "BEGIN:VALARM", "ACTION:DISPLAY", `DESCRIPTION:${esc(title)}`, `TRIGGER:${alarmDays ? `-P${alarmDays}D` : "PT9H"}`, "END:VALARM",
      "END:VEVENT", "END:VCALENDAR"].join("\r\n");
    FY.download(new Blob([body], { type: "text/calendar" }), name + ".ics");
  }

  // ---------- piezas de temporada que usan la portada y las calculadoras ----------
  // Las 5 tarjetas de "Tu Aguinaldo Wrapped" a partir del resultado de FY.ley.aguinaldo.
  function aguinaldoWrapped(ag, left) {
    const fmt = FY.fmt, y = ag.deadline.getFullYear(), libre = Math.min(ag.amount, ag.exento), cetes = ag.amount * FY.RATES.cetes / 100;
    const dias = (n) => `${n} ${n === 1 ? "día" : "días"}`;
    return [
      { kicker: `Tu aguinaldo ${y}`, big: fmt(ag.amount), line: ag.full ? `${FY.LEY.aguinaldoDias} días de salario, por ley.` : `Proporcional a ${dias(ag.days)} trabajados.`, sub: "Artículo 87 de la Ley Federal del Trabajo." },
      { kicker: "Cuenta regresiva", big: left >= 0 ? String(left) : "¡Ya!", line: left >= 0 ? (left === 1 ? "día para cobrarlo" : "días para cobrarlo") : "Ya te lo debieron pagar", sub: "Fecha límite: 19 de diciembre.", tone: "tide" },
      { kicker: "Libre de ISR", big: fmt(libre), line: ag.gravado > 0 ? `Sobre ${fmt(ag.gravado)} te retienen ISR.` : "Todo tu aguinaldo está libre de ISR.", sub: `Exento hasta 30 UMA (${fmt(ag.exento)}).` },
      { kicker: "Si lo pones en CETES un año", big: "+" + fmt(cetes), line: "de rendimiento, antes de impuestos.", sub: `Con CETES a 28 días al ${FY.RATES.cetes.toFixed(2)}% anual, si la tasa se mantiene.`, tone: "tide" },
      { kicker: "Ahora te toca a ti", big: "¿Y tú?", line: "Calcula tu aguinaldo en 10 segundos.", sub: "Gratis y sin registro." }
    ];
  }
  // Cuenta regresiva en vivo (días, horas, minutos, segundos) dentro de `host`.
  function countdown(host, target, label) {
    const id = "cd" + Math.random().toString(36).slice(2, 7);
    host.innerHTML = `<p class="cd-label" id="${id}">${label}</p><div class="cd-grid" role="timer" aria-labelledby="${id}">` +
      ["días", "horas", "min", "seg"].map((u) => `<span><b>--</b><small>${u}</small></span>`).join("") + "</div>";
    const b = host.querySelectorAll("b"), pad = (n) => String(n).padStart(2, "0");
    const tick = () => {
      let ms = Math.max(0, target - new Date());
      const d = Math.floor(ms / 864e5); ms -= d * 864e5;
      const h = Math.floor(ms / 36e5); ms -= h * 36e5;
      const m = Math.floor(ms / 6e4), s = Math.floor((ms - m * 6e4) / 1000);
      b[0].textContent = d; b[1].textContent = pad(h); b[2].textContent = pad(m); b[3].textContent = pad(s);
    };
    tick(); setInterval(tick, 1000);
  }

  FY.compartir = { link, waURL, card, shareStory, storySheet, bar, wrapped, welcome, ics, aguinaldoWrapped, countdown };
})(window.FY);
