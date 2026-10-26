// Futuro Yo · tarjetas para historias (1080×1920): antes y después, mi futuro, nosotros y mi racha.
(function (FY) {
  const { $, fmt, store, state } = FY;
  const CW = 1080, CH = 1920;
  let kind = "antes", blob = null, url = "", partner = null, building = 0;

  const loadImg = (src) => new Promise((res) => { const i = new Image(); i.onload = () => res(i); i.onerror = () => res(null); i.src = src; });
  const svgImg = (svg) => loadImg("data:image/svg+xml;charset=utf-8," + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 220" width="600" height="660">${svg}</svg>`));

  function scene(x, mood) {
    const g = x.createLinearGradient(0, 0, 0, CH);
    if (mood === "ok") { g.addColorStop(0, "#1b2a5c"); g.addColorStop(0.45, "#c2547a"); g.addColorStop(0.62, "#ffb05e"); g.addColorStop(0.63, "#1d6f86"); g.addColorStop(1, "#0b3140"); }
    else if (mood === "mid") { g.addColorStop(0, "#0c2433"); g.addColorStop(0.6, "#21485a"); g.addColorStop(1, "#0a1a24"); }
    else { g.addColorStop(0, "#1b2228"); g.addColorStop(0.6, "#2c3a44"); g.addColorStop(1, "#11181d"); }
    x.fillStyle = g; x.fillRect(0, 0, CW, CH);
    const r = FY.rng(5);
    if (mood === "ok") {
      x.fillStyle = "rgba(255,214,140,.95)"; x.beginPath(); x.arc(CW / 2, CH * 0.62, 150, Math.PI, 0); x.fill();
      x.strokeStyle = "rgba(255,220,170,.45)"; x.lineWidth = 6;
      for (let i = 0; i < 16; i++) { const y = CH * 0.65 + i * 38, w = 380 - i * 14; x.beginPath(); x.moveTo(CW / 2 - w / 2 + r() * 40, y); x.lineTo(CW / 2 + w / 2 - r() * 40, y); x.stroke(); }
    } else if (mood === "mid") {
      for (let i = 0; i < 14; i++) {
        const w = 60 + r() * 90, h = 180 + r() * 420, bx = i * 80 - 20;
        x.fillStyle = "#0e2230"; x.fillRect(bx, CH - h - 120, w, h + 120);
        x.fillStyle = "rgba(255,181,71,.55)";
        for (let wy = CH - h - 90; wy < CH - 160; wy += 46) for (let wx = bx + 12; wx < bx + w - 16; wx += 30) if (r() < 0.35) x.fillRect(wx, wy, 12, 18);
      }
    } else {
      x.strokeStyle = "rgba(200,220,230,.22)"; x.lineWidth = 3;
      for (let i = 0; i < 160; i++) { const sx = r() * CW, sy = r() * CH; x.beginPath(); x.moveTo(sx, sy); x.lineTo(sx - 24, sy + 70); x.stroke(); }
    }
    const v = x.createLinearGradient(0, 0, 0, CH);
    v.addColorStop(0, "rgba(7,18,26,.55)"); v.addColorStop(0.3, "rgba(7,18,26,0)"); v.addColorStop(0.7, "rgba(7,18,26,.1)"); v.addColorStop(1, "rgba(7,18,26,.85)");
    x.fillStyle = v; x.fillRect(0, 0, CW, CH);
  }
  async function portrait(x, img, cx, cy, rad, ring) {
    x.save(); x.beginPath(); x.arc(cx, cy, rad, 0, Math.PI * 2); x.closePath();
    x.fillStyle = "#0b1f2a"; x.fill(); x.clip();
    if (img && img.canvas) x.drawImage(img.canvas, cx - rad, cy - rad, rad * 2, rad * 2);
    else if (img && img.svg) { const im = await svgImg(img.svg); if (im) x.drawImage(im, cx - rad * 0.9, cy - rad * 0.86, rad * 1.8, rad * 1.98); }
    x.restore();
    x.strokeStyle = ring; x.lineWidth = 10; x.beginPath(); x.arc(cx, cy, rad + 5, 0, Math.PI * 2); x.stroke();
  }
  function label(x, text, cx, y, bg, fg) {
    x.font = "600 36px 'JetBrains Mono', monospace";
    const w = x.measureText(text).width + 48;
    x.fillStyle = bg; roundRect(x, cx - w / 2, y - 34, w, 60, 30); x.fill();
    x.fillStyle = fg; x.textAlign = "center"; x.fillText(text, cx, y + 8);
  }
  function roundRect(x, l, t, w, h, r) { x.beginPath(); x.moveTo(l + r, t); x.arcTo(l + w, t, l + w, t + h, r); x.arcTo(l + w, t + h, l, t + h, r); x.arcTo(l, t + h, l, t, r); x.arcTo(l, t, l + w, t, r); x.closePath(); }
  function text(x, s, y, font, color, maxW = 940) {
    x.font = font; x.fillStyle = color; x.textAlign = "center";
    const words = s.split(" "), lines = []; let line = "";
    words.forEach((w) => { const t = line ? line + " " + w : w; if (x.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t; });
    lines.push(line);
    const lh = parseInt(font.match(/(\d+)px/)[1], 10) * 1.15;
    lines.forEach((l, i) => x.fillText(l, CW / 2, y + i * lh));
    return y + lines.length * lh;
  }
  function footer(x) {
    x.fillStyle = "rgba(7,18,26,.75)"; roundRect(x, 90, CH - 250, CW - 180, 150, 40); x.fill();
    text(x, "¿Y tu yo del futuro?", CH - 185, "800 46px Unbounded, 'Arial Black', sans-serif", "#eaf3f4");
    text(x, "futuro·yo  ·  gratis y sin subir tu foto", CH - 128, "600 32px Figtree, sans-serif", "#5ad6c8");
  }

  async function build() {
    const job = ++building;
    $("card-busy").hidden = false;
    try { if (document.fonts && document.fonts.ready) await document.fonts.ready; } catch (e) {}
    const c = FY.sim.last();
    const cv = document.createElement("canvas"); cv.width = CW; cv.height = CH;
    const x = cv.getContext("2d");
    const moodLine = c.mood === "ok" ? "Está en paz." : c.mood === "mid" ? "Está a medias." : "Necesita mi ayuda.";
    if (kind === "racha") {
      const h = FY.habits.summary(), lv = h.level;
      scene(x, h.streak >= 7 ? "ok" : "mid");
      text(x, "MI RACHA CON MI YO DEL FUTURO", 230, "600 36px 'JetBrains Mono', monospace", "#93adb7");
      if (h.streak > 0) {
        text(x, String(h.streak), 520, "800 300px Unbounded, 'Arial Black', sans-serif", "#ffb547");
        text(x, h.streak === 1 ? "día seguido" : "días seguidos", 640, "700 60px Figtree, sans-serif", "#eaf3f4");
      } else {
        text(x, "Hoy empiezo", 470, "800 110px Unbounded, 'Arial Black', sans-serif", "#ffb547");
        text(x, "a cuidar a mi yo del futuro", 600, "700 56px Figtree, sans-serif", "#eaf3f4");
      }
      const scn = await loadImg("data:image/svg+xml;charset=utf-8," + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 170" width="880" height="468">${FY.habits.sceneSVG(lv)}</svg>`));
      if (scn) { x.save(); roundRect(x, 100, 740, 880, 468, 36); x.clip(); x.drawImage(scn, 100, 740, 880, 468); x.restore(); }
      let y = text(x, `Mi yo del futuro ya vive en: ${FY.habits.LEVELS[lv].name}`, 1290, "700 44px Figtree, sans-serif", "#eaf3f4");
      y = text(x, `Le he mandado ${fmt(h.future)} a mis ${state.retire}`, y + 20, "600 40px Figtree, sans-serif", "#5ad6c8");
      const rt = FY.reto.result();
      if (rt.done) text(x, `Reto de hoy: ${rt.score}/5  ${rt.grid}`, y + 30, "600 38px 'JetBrains Mono', monospace", "#ffd36b");
    } else if (kind === "antes") {
      scene(x, c.mood);
      text(x, `YO HOY VS. YO A LOS ${state.retire}`, 200, "600 38px 'JetBrains Mono', monospace", "#eaf3f4");
      text(x, moodLine, 300, "800 76px Unbounded, 'Arial Black', sans-serif", "#ffffff");
      await portrait(x, FY.sim.faceAt(state.age, "mid"), 300, 720, 215, "rgba(90,214,200,.9)");
      await portrait(x, FY.sim.faceAt(state.retire, c.mood), 780, 720, 215, "rgba(255,181,71,.95)");
      label(x, `HOY · ${state.age}`, 300, 1000, "rgba(7,18,26,.8)", "#5ad6c8");
      label(x, `${c.year} · ${state.retire}`, 780, 1000, "rgba(7,18,26,.8)", "#ffb547");
      x.strokeStyle = "#ffffff"; x.lineWidth = 8; x.lineCap = "round";
      x.beginPath(); x.moveTo(515, 720); x.lineTo(565, 720); x.moveTo(548, 700); x.lineTo(568, 720); x.lineTo(548, 740); x.stroke();
      let y = text(x, fmt(c.bal), 1220, "800 120px Unbounded, 'Arial Black', sans-serif", "#ffb547");
      y = text(x, `en pesos de hoy, guardando ${fmt(state.monthly)} al mes`, y - 30, "600 42px Figtree, sans-serif", "#eaf3f4");
      text(x, `≈ ${fmt(c.income)} al mes en mi retiro`, y + 14, "500 38px Figtree, sans-serif", "#cfe0e4");
    } else if (kind === "resultado") {
      scene(x, c.mood);
      text(x, `MI YO DE ${state.retire} · AÑO ${c.year}`, 200, "600 38px 'JetBrains Mono', monospace", "#eaf3f4");
      text(x, moodLine, 300, "800 80px Unbounded, 'Arial Black', sans-serif", "#ffffff");
      await portrait(x, FY.sim.faceAt(state.retire, c.mood), CW / 2, 760, 340, "rgba(255,181,71,.95)");
      let y = text(x, fmt(c.bal), 1270, "800 124px Unbounded, 'Arial Black', sans-serif", "#ffb547");
      y = text(x, `en pesos de hoy · ≈ ${fmt(c.income)} al mes`, y - 30, "600 42px Figtree, sans-serif", "#eaf3f4");
      const req = c.mood === "ok" ? "Voy por buen camino." : `Me faltan ${fmt(Math.max(0, c.req - state.monthly))} al mes. Empiezo hoy.`;
      text(x, req, y + 20, "600 40px Figtree, sans-serif", "#5ad6c8");
    } else {
      scene(x, c.mood);
      const years = state.retire - state.age;
      const age2 = FY.clamp(+$("age2").value || state.age, 18, 70);
      text(x, `NOSOTROS EN ${c.year}`, 200, "600 38px 'JetBrains Mono', monospace", "#eaf3f4");
      text(x, "Así nos vamos a ver.", 300, "800 70px Unbounded, 'Arial Black', sans-serif", "#ffffff", 980);
      await portrait(x, FY.sim.faceAt(state.retire, c.mood), 290, 780, 215, "rgba(255,181,71,.95)");
      let p2;
      if (partner) { const a = FY.aging.amounts(age2, age2 + years); p2 = { canvas: FY.aging.render(partner, a.t, a.gray) }; }
      else p2 = { svg: FY.avatar.svg(age2 + years, c.mood, (state.skin + 2) % 5, state.hair === "short" ? "long" : "short") };
      await portrait(x, p2, 790, 780, 215, "rgba(90,214,200,.9)");
      label(x, `${state.retire} años`, 290, 1060, "rgba(7,18,26,.8)", "#ffb547");
      label(x, `${age2 + years} años`, 790, 1060, "rgba(7,18,26,.8)", "#5ad6c8");
      const y = text(x, c.mood === "ok" ? "Y con el retiro resuelto." : "Hoy empezamos a ahorrar para llegar bien.", 1260, "700 52px Figtree, sans-serif", "#eaf3f4");
      text(x, "Hazlo con tu persona favorita", y + 20, "600 40px Figtree, sans-serif", "#5ad6c8");
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
    const c = FY.sim.last();
    if (kind === "racha") { const h = FY.habits.summary(); return `Llevo ${h.streak} días seguidos cuidando a mi yo del futuro. Ya le mandé ${fmt(h.future)}. ¿Te animas? ${FY.shareURL({ ref: "racha" })}`; }
    if (kind === "nosotros") return `Así nos vamos a ver en ${c.year}. Hazlo con tu persona favorita (la foto no sale de tu teléfono): ${FY.shareURL({ ref: "nosotros" })}`;
    return `Vi mi cara a los ${state.retire}: si guardo ${fmt(state.monthly)} al mes tendré ${fmt(c.bal)} en pesos de hoy. ¿Y tu yo del futuro? ${FY.shareURL({ ref: kind })}`;
  }

  function setKind(k) {
    kind = k;
    document.querySelectorAll("[data-kind]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.kind === k));
    $("partner-box").hidden = k !== "nosotros";
    build().catch(() => { $("card-busy").hidden = true; FY.toast("No pude crear la tarjeta. Inténtalo de nuevo."); });
  }
  function open(k) {
    $("modal").hidden = false;
    setKind(k || "antes");
    $("close").focus({ preventScroll: true });
  }
  function close() { $("modal").hidden = true; }
  document.querySelectorAll("[data-kind]").forEach((b) => b.addEventListener("click", () => setKind(b.dataset.kind)));
  document.querySelectorAll("[data-share]").forEach((b) => b.addEventListener("click", () => open(b.dataset.share)));
  $("close").addEventListener("click", close);
  $("modal").addEventListener("click", (e) => { if (e.target.id === "modal") close(); });
  addEventListener("keydown", (e) => { if (e.key === "Escape" && !$("modal").hidden) close(); });
  $("card-share").addEventListener("click", async () => {
    if (!blob) return;
    const ok = await FY.nativeShare({ files: [new File([blob], "mi-yo-del-futuro.png", { type: "image/png" })], text: shareText() });
    if (!ok) { FY.copyText(shareText()); FY.toast("Texto copiado. Mantén presionada la imagen para guardarla."); }
    FY.emit("shared", kind);
  });
  $("wa").addEventListener("click", () => FY.emit("shared", kind));
  $("dl").addEventListener("click", () => { if (blob) { FY.download(blob, "mi-yo-del-futuro.png"); FY.emit("shared", kind); } });
  if (FY.CONFIG.EMBEDDED_VIEWER) $("dl").hidden = true;
  $("age2").addEventListener("change", () => { store.set("age2", +$("age2").value); if (kind === "nosotros") setKind("nosotros"); });
  $("photo2-input").addEventListener("change", async (e) => {
    const f = e.target.files && e.target.files[0]; e.target.value = "";
    if (!f) return;
    $("card-busy").hidden = false;
    try {
      const src = await FY.aging.fileToCanvas(f);
      const p = await FY.aging.detect(src);
      if (!p) { FY.toast("No encontré una cara en esa foto. Prueba otra de frente."); $("card-busy").hidden = true; return; }
      partner = FY.aging.prepare(p);
      store.set("photo2", FY.aging.serialize(p));
      setKind("nosotros");
    } catch (err) { $("card-busy").hidden = true; FY.toast("No se pudo cargar la IA. Revisa tu conexión."); }
  });

  async function init() {
    $("age2").value = store.get("age2", state.age);
    const p = await FY.aging.deserialize(store.get("photo2", null));
    if (p) partner = FY.aging.prepare(p);
  }
  FY.share = { init, open, forgetPartner: () => { partner = null; store.del("photo2"); } };
})(window.FY);
