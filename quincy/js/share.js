// Quincy · tarjetas para historias (1080×1920): mi futuro, días en verde y mi aguinaldo.
(function (FY) {
  const { $, fmt, state } = FY;
  const CW = 1080, CH = 1920;
  let kind = "futuro", blob = null, url = "", building = 0;

  const loadImg = (src) => new Promise((res) => { const i = new Image(); i.onload = () => res(i); i.onerror = () => res(null); i.src = src; });
  const svgImg = (svg, vb = "0 0 200 220", w = 600, h = 660) => loadImg("data:image/svg+xml;charset=utf-8," + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}" width="${w}" height="${h}">${svg}</svg>`));
  const hide = () => $("hide-amounts").checked;
  const money = (v) => (hide() ? "$ • • •" : fmt(v));

  function backdrop(x, mood) {
    const g = x.createLinearGradient(0, 0, 0, CH);
    if (mood === "ok") { g.addColorStop(0, "#14284f"); g.addColorStop(0.5, "#1b4a63"); g.addColorStop(1, "#07121a"); }
    else if (mood === "bad") { g.addColorStop(0, "#2a1f28"); g.addColorStop(0.55, "#1d2a33"); g.addColorStop(1, "#07121a"); }
    else { g.addColorStop(0, "#0c2433"); g.addColorStop(0.55, "#15384a"); g.addColorStop(1, "#07121a"); }
    x.fillStyle = g; x.fillRect(0, 0, CW, CH);
    // Anillos orbitales: la misma idea visual de la portada.
    x.save(); x.translate(CW / 2, 760);
    for (let i = 0; i < 4; i++) {
      x.strokeStyle = i % 2 ? "rgba(90,214,200,.22)" : "rgba(255,181,71,.25)"; x.lineWidth = 3;
      x.beginPath(); x.ellipse(0, 0, 360 + i * 90, 120 + i * 34, -0.25, 0, Math.PI * 2); x.stroke();
    }
    const r = FY.rng(7);
    for (let i = 0; i < 160; i++) { x.fillStyle = r() < 0.5 ? "rgba(255,181,71,.6)" : "rgba(90,214,200,.6)"; const a = r() * Math.PI * 2, d = 200 + r() * 520; x.fillRect(Math.cos(a) * d, Math.sin(a) * d * 0.6, 3, 3); }
    x.restore();
  }
  function roundRect(x, l, t, w, h, r) { x.beginPath(); x.moveTo(l + r, t); x.arcTo(l + w, t, l + w, t + h, r); x.arcTo(l + w, t + h, l, t + h, r); x.arcTo(l, t + h, l, t, r); x.arcTo(l, t, l + w, t, r); x.closePath(); }
  function text(x, s, y, font, color, maxW = 940) {
    x.font = font; x.fillStyle = color; x.textAlign = "center";
    const words = String(s).split(" "), lines = []; let line = "";
    words.forEach((w) => { const t = line ? line + " " + w : w; if (x.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t; });
    lines.push(line);
    const lh = parseInt(font.match(/(\d+)px/)[1], 10) * 1.15;
    lines.forEach((l, i) => x.fillText(l, CW / 2, y + i * lh));
    return y + lines.length * lh;
  }
  function footer(x) {
    x.fillStyle = "rgba(7,18,26,.8)"; roundRect(x, 90, CH - 250, CW - 180, 150, 40); x.fill();
    text(x, "¿Y a ti cuánto te toca?", CH - 185, "800 46px Unbounded, 'Arial Black', sans-serif", "#eaf3f4");
    text(x, "quincy · gratis y sin registro", CH - 128, "600 32px Figtree, sans-serif", "#5ad6c8");
  }

  // Ticket de papel con los gastos del periodo, como el de una tienda.
  function receipt(x) {
    const q = FY.quincena.ticket();
    backdrop(x, "mid");
    const L = 170, R = CW - 170, top = 150, lines = [];
    const df = (d) => d.toLocaleDateString("es-MX", { day: "2-digit", month: "short" }).toUpperCase();
    const row = (a, b, strong) => lines.push({ a, b, strong });
    row(`PAGO ${q.freq.toUpperCase()}`, money(q.ingreso));
    row("PAGOS FIJOS", "-" + money(q.fijos));
    row("AHORRO (ME PAGUÉ PRIMERO)", "-" + money(q.ahorro));
    lines.push({ sep: true });
    if (q.items.length) q.items.slice(0, 8).forEach(([c, v]) => row(c.toUpperCase(), money(v)));
    else row("SIN GASTOS REGISTRADOS", money(0));
    lines.push({ sep: true });
    row("GASTADO", money(q.spent), true);
    row("ME QUEDA", money(q.left), true);
    if (q.aguante > 0) row("ME AGUANTÉ", money(q.aguante));
    row("DÍAS EN VERDE", `x${q.streak}`);
    const lh = 64, h = 300 + lines.length * lh + (q.ejemplo ? 280 : 230);
    // papel con orilla dentada
    x.save(); x.shadowColor = "rgba(0,0,0,.5)"; x.shadowBlur = 40; x.fillStyle = "#f3f5f4";
    x.beginPath(); x.moveTo(L, top);
    for (let xx = L; xx <= R; xx += 30) x.lineTo(xx + 15, top + (((xx - L) / 30) % 2 ? 0 : 14));
    x.lineTo(R, top + h);
    for (let xx = R; xx >= L; xx -= 30) x.lineTo(xx - 15, top + h - (((R - xx) / 30) % 2 ? 0 : 14));
    x.closePath(); x.fill(); x.restore();
    x.fillStyle = "#14202a"; x.textAlign = "center";
    x.font = "800 64px Unbounded, 'Arial Black', sans-serif"; x.fillText("QUINCY", CW / 2, top + 120);
    x.font = "600 30px 'JetBrains Mono', monospace"; x.fillText("TICKET DE MI QUINCENA", CW / 2, top + 175);
    x.fillText(`${df(q.start)} — ${df(q.end)}`, CW / 2, top + 220);
    let y = top + 300;
    x.font = "600 34px 'JetBrains Mono', monospace";
    lines.forEach((l) => {
      if (l.sep) { x.fillText("- ".repeat(17).trim(), CW / 2, y); y += lh; return; }
      x.font = `${l.strong ? 700 : 500} 34px 'JetBrains Mono', monospace`;
      x.textAlign = "left"; x.fillText(l.a.slice(0, 26), L + 50, y);
      x.textAlign = "right"; x.fillText(l.b, R - 50, y);
      x.textAlign = "center"; y += lh;
    });
    const r = FY.rng(q.spent | 0 + 3);
    let bx = L + 120;
    while (bx < R - 120) { const w = 3 + Math.floor(r() * 9); if (r() > 0.35) x.fillRect(bx, y + 10, w, 110); bx += w + 4; }
    x.font = "600 28px 'JetBrains Mono', monospace"; x.fillText("GRACIAS POR CUIDAR TU QUINCENA", CW / 2, y + 180);
    if (q.ejemplo) { x.fillStyle = "#c0533f"; x.font = "700 30px Figtree, sans-serif"; x.fillText("(números de ejemplo)", CW / 2, y + 230); }
  }

  async function build() {
    const job = ++building;
    $("card-busy").hidden = false;
    try { if (document.fonts && document.fonts.ready) await document.fonts.ready; } catch (e) {}
    const cv = document.createElement("canvas"); cv.width = CW; cv.height = CH;
    const x = cv.getContext("2d");
    if (kind === "futuro") {
      const c = FY.sim.last();
      backdrop(x, c.mood);
      text(x, `MI YO DE ${state.retire} · AÑO ${c.year}`, 200, "600 38px 'JetBrains Mono', monospace", "#eaf3f4");
      text(x, c.mood === "ok" ? "Está en paz." : c.mood === "mid" ? "Está a medias." : "Necesita mi ayuda.", 300, "800 80px Unbounded, 'Arial Black', sans-serif", "#ffffff");
      x.save(); x.beginPath(); x.arc(CW / 2, 760, 330, 0, Math.PI * 2); x.fillStyle = "#0b1f2a"; x.fill(); x.clip();
      const im = await svgImg(FY.avatar.svg(state.retire, c.mood, state.skin, state.hair));
      if (im) x.drawImage(im, CW / 2 - 300, 500, 600, 660);
      x.restore();
      x.strokeStyle = "rgba(255,181,71,.95)"; x.lineWidth = 10; x.beginPath(); x.arc(CW / 2, 760, 335, 0, Math.PI * 2); x.stroke();
      let y = text(x, money(c.bal), 1270, "800 124px Unbounded, 'Arial Black', sans-serif", "#ffb547");
      y = text(x, `en pesos de hoy, guardando ${money(state.monthly)} al mes`, y - 30, "600 42px Figtree, sans-serif", "#eaf3f4");
      text(x, c.mood === "ok" ? "Voy por buen camino." : "Hoy empiezo a cambiarlo.", y + 20, "600 40px Figtree, sans-serif", "#5ad6c8");
    } else if (kind === "verde") {
      const q = FY.quincena.summary();
      backdrop(x, q.streak >= 7 ? "ok" : "mid");
      text(x, "MI QUINCENA BAJO CONTROL", 220, "600 38px 'JetBrains Mono', monospace", "#93adb7");
      if (q.streak > 0) {
        text(x, String(q.streak), 600, "800 320px Unbounded, 'Arial Black', sans-serif", "#86e3a8");
        text(x, q.streak === 1 ? "día en verde" : "días seguidos en verde", 740, "700 60px Figtree, sans-serif", "#eaf3f4");
      } else {
        text(x, "Hoy empiezo", 560, "800 110px Unbounded, 'Arial Black', sans-serif", "#86e3a8");
        text(x, "a no pasarme de mi límite", 690, "700 56px Figtree, sans-serif", "#eaf3f4");
      }
      text(x, "Sin pasarme de lo que me toca gastar cada día para llegar a la quincena.", 980, "600 44px Figtree, sans-serif", "#cfe0e4", 860);
    } else if (kind === "recibo") {
      receipt(x);
    } else if (kind === "tanda") {
      const T = FY.tanda.current(), me = FY.tanda.me(), n = T.personas.length, ds = FY.tanda.dates(T.freq, T.inicio, n), pot = n * T.monto;
      backdrop(x, "ok");
      text(x, T.nombre.toUpperCase(), 220, "600 38px 'JetBrains Mono', monospace", "#93adb7");
      if (me !== undefined && me !== "" && T.personas[me] !== undefined) {
        const k = +me, left = FY.ley.diffDays(new Date(), ds[k]);
        text(x, left > 0 ? String(left) : "HOY", 600, "800 300px Unbounded, 'Arial Black', sans-serif", "#86e3a8");
        text(x, left > 0 ? (left === 1 ? "día para que me toque la tanda" : "días para que me toque la tanda") : "me toca la tanda", 730, "700 56px Figtree, sans-serif", "#eaf3f4", 900);
        const y = text(x, `${money(pot)} · turno ${k + 1} de ${n}`, 900, "800 64px Unbounded, 'Arial Black', sans-serif", "#ffb547");
        text(x, ds[k].toLocaleDateString("es-MX", { weekday: "long", day: "numeric", month: "long" }), y + 10, "600 44px Figtree, sans-serif", "#5ad6c8");
      } else {
        text(x, `${n}`, 600, "800 300px Unbounded, 'Arial Black', sans-serif", "#86e3a8");
        text(x, "personas en nuestra tanda", 730, "700 56px Figtree, sans-serif", "#eaf3f4");
        text(x, `Cada turno: ${money(pot)}`, 900, "800 64px Unbounded, 'Arial Black', sans-serif", "#ffb547");
      }
      text(x, "Turnos sorteados con la ruleta de Quincy", 1180, "600 40px Figtree, sans-serif", "#cfe0e4");
    } else {
      const ag = FY.derechos.aguinaldo(), left = FY.ley.diffDays(new Date(), ag.deadline);
      backdrop(x, "ok");
      text(x, `AGUINALDO ${ag.deadline.getFullYear()}`, 220, "600 38px 'JetBrains Mono', monospace", "#93adb7");
      if (left >= 0) {
        text(x, String(left), 600, "800 320px Unbounded, 'Arial Black', sans-serif", "#ffb547");
        text(x, left === 1 ? "día para mi aguinaldo" : "días para mi aguinaldo", 740, "700 60px Figtree, sans-serif", "#eaf3f4");
      } else text(x, "Ya me tocó", 600, "800 120px Unbounded, 'Arial Black', sans-serif", "#ffb547");
      let y = text(x, hide() ? "Ya sé cuánto me toca." : `Me tocan ${fmt(ag.amount)}`, 1000, "800 70px Unbounded, 'Arial Black', sans-serif", "#ffffff");
      text(x, "Por ley, a más tardar el 19 de diciembre.", y + 10, "600 42px Figtree, sans-serif", "#5ad6c8");
    }
    footer(x);
    const b = await new Promise((res) => cv.toBlob(res, "image/png"));
    if (job !== building) return;
    blob = b;
    if (url) URL.revokeObjectURL(url);
    url = blob ? URL.createObjectURL(blob) : cv.toDataURL("image/png");
    $("card-img").src = url;
    $("card-busy").hidden = true;
    $("wa").href = "https://wa.me/?text=" + encodeURIComponent(shareText());
  }
  function shareText() {
    const link = FY.shareURL({ ref: kind });
    if (kind === "verde") { const q = FY.quincena.summary(); return `Llevo ${q.streak} días sin pasarme de mi límite diario para llegar a la quincena. ¿Tú cuánto puedes gastar hoy? ${link}`; }
    if (kind === "recibo") return `El ticket de mi quincena: ${hide() ? "" : `me quedan ${fmt(FY.quincena.ticket().left)} y `}llevo ${FY.quincena.ticket().streak} días en verde. Arma el tuyo: ${link}`;
    if (kind === "tanda") { const T = FY.tanda.current(); return `Nuestra tanda "${T.nombre}" ya tiene turnos. Mira cuándo te toca: ${FY.CONFIG.SITE}app.html?t=${FY.tanda.encode(T)}#tanda`; }
    if (kind === "aguinaldo") { const ag = FY.derechos.aguinaldo(); return `${hide() ? "Ya calculé mi aguinaldo." : `Me tocan ${fmt(ag.amount)} de aguinaldo.`} ¿Ya sabes cuánto te toca a ti? ${link}`; }
    const c = FY.sim.last();
    return `Vi a mi yo de ${state.retire}: ${c.mood === "ok" ? "está en paz" : c.mood === "mid" ? "está a medias" : "necesita mi ayuda"}. ¿Y el tuyo? ${link}`;
  }
  function setKind(k) {
    kind = k;
    document.querySelectorAll("[data-kind]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.kind === k));
    build().catch(() => { $("card-busy").hidden = true; FY.toast("No pude crear la tarjeta. Inténtalo de nuevo."); });
  }
  function open(k) { $("modal").hidden = false; setKind(k || "futuro"); $("close").focus({ preventScroll: true }); }
  function close() { $("modal").hidden = true; }
  document.querySelectorAll("[data-kind]").forEach((b) => b.addEventListener("click", () => setKind(b.dataset.kind)));
  document.querySelectorAll("[data-share]").forEach((b) => b.addEventListener("click", () => open(b.dataset.share)));
  $("hide-amounts").addEventListener("change", () => setKind(kind));
  $("close").addEventListener("click", close);
  $("modal").addEventListener("click", (e) => { if (e.target.id === "modal") close(); });
  addEventListener("keydown", (e) => { if (e.key === "Escape" && !$("modal").hidden) close(); });
  $("card-share").addEventListener("click", async () => {
    if (!blob) return;
    // Solo la imagen (así Instagram ofrece "Historia"); el texto con el enlace queda copiado para el sticker de enlace.
    if (FY.compartir && navigator.share && navigator.canShare && navigator.canShare({ files: [new File([blob], "quincy.png", { type: "image/png" })] })) {
      FY.compartir.shareStory([blob], "quincy", shareText()); return;
    }
    const ok = await FY.nativeShare({ files: [new File([blob], "quincy.png", { type: "image/png" })], text: shareText() });
    if (!ok) { FY.copyText(shareText()); FY.toast("Texto copiado. Mantén presionada la imagen para guardarla."); }
  });
  $("dl").addEventListener("click", () => { if (blob) FY.download(blob, "quincy.png"); });
  if (FY.CONFIG.EMBEDDED_VIEWER) $("dl").hidden = true;
  FY.share = { init() {}, open };
})(window.FY);
