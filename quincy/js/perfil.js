// Quincy · "Tus datos": tu perfil en un solo lugar (pago, trabajo y edad), pagos fijos por concepto,
// avisos opcionales (sin pedir tus números), respaldo en archivo y borrar todo. Todo vive en este teléfono.
(function (FY) {
  const { $, fmt, perfil, CONFIG } = FY;
  const FIJOS = [["renta", "Renta"], ["luz", "Luz"], ["celular", "Celular"], ["internet", "Internet"], ["transporte", "Transporte"], ["deudas", "Deudas"], ["otro", "Otro"]];
  const label = (k) => (FIJOS.find((f) => f[0] === k) || [k, k === "fijos" ? "Pagos fijos" : "Otro"])[1];
  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  // ---------- pagos fijos por concepto (también lo usa la bienvenida) ----------
  // list: [{ k, amt }]. onChange(list) se llama con cada cambio.
  function fijosEditor(host, list, onChange, opts = {}) {
    let items = (list || []).map((f) => ({ k: f.k, amt: +f.amt || 0 }));
    const draw = (focusKey) => {
      const on = new Set(items.map((f) => f.k));
      host.innerHTML = `<div class="chips fj-chips">${FIJOS.map(([k, n]) => `<button type="button" class="chip-btn" data-k="${k}" aria-pressed="${on.has(k)}">${on.has(k) ? "✓ " : "+ "}${n}</button>`).join("")}</div>
        <div class="fj-rows">${items.map((f, i) => `<div class="fj-row"><label for="fj-${opts.id || "x"}-${i}">${esc(label(f.k))}</label><div class="fj-in"><span aria-hidden="true">$</span><input id="fj-${opts.id || "x"}-${i}" type="number" inputmode="numeric" min="0" max="10000000" value="${f.amt || ""}" placeholder="0" data-i="${i}"></div><button type="button" class="x" data-del="${i}" aria-label="Quitar ${esc(label(f.k))}">×</button></div>`).join("")}</div>
        <p class="fj-total small"><span class="mut">Total de pagos fijos</span> <b class="mono">${fmt(perfil.sumFijos(items))}</b></p>`;
      if (focusKey) { const i = items.findIndex((f) => f.k === focusKey); const el = host.querySelector(`[data-i="${i}"]`); if (el) el.focus(); }
    };
    host.addEventListener("click", (e) => {
      const chip = e.target.closest("[data-k]"), del = e.target.closest("[data-del]");
      if (chip) {
        const k = chip.dataset.k, i = items.findIndex((f) => f.k === k);
        if (i >= 0) items.splice(i, 1); else items.push({ k, amt: 0 });
        draw(i >= 0 ? null : k); onChange(items.slice());
      } else if (del) { items.splice(+del.dataset.del, 1); draw(); onChange(items.slice()); }
    });
    host.addEventListener("input", (e) => {
      const i = e.target.dataset && e.target.dataset.i;
      if (i == null) return;
      items[+i].amt = Math.max(0, Math.min(1e7, +e.target.value || 0));
      host.querySelector(".fj-total b").textContent = fmt(perfil.sumFijos(items));
      onChange(items.slice());
    });
    draw();
    return { set(l) { items = (l || []).map((f) => ({ k: f.k, amt: +f.amt || 0 })); draw(); }, get: () => items.slice() };
  }

  // ---------- avisos opcionales (también al final de la bienvenida) ----------
  const nextAguinaldo = () => { const t = new Date(); return new Date(t.getMonth() === 11 && t.getDate() > 19 ? t.getFullYear() + 1 : t.getFullYear(), 11, 19); };
  function avisosICS() {
    const p = (n) => String(n).padStart(2, "0"), ymd = (d) => `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}`;
    const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+/, "");
    const ag = nextAguinaldo(), sm = new Date(new Date().getFullYear() + 1, 0, 1);
    const ev = (d, uid, title, desc, alarm) => ["BEGIN:VEVENT", `UID:${uid}-${ymd(d)}@quincy`, `DTSTAMP:${stamp}`, `DTSTART;VALUE=DATE:${ymd(d)}`, `DTEND;VALUE=DATE:${ymd(new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1))}`,
      `SUMMARY:${title}`, `DESCRIPTION:${desc}`, "BEGIN:VALARM", "ACTION:DISPLAY", `DESCRIPTION:${title}`, `TRIGGER:${alarm}`, "END:VALARM", "END:VEVENT"];
    const body = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Quincy//ES", "CALSCALE:GREGORIAN",
      ...ev(ag, "aguinaldo", "Fecha límite de mi aguinaldo", `Por ley te lo deben pagar a más tardar hoy. Revisa cuánto te toca: ${CONFIG.SITE}app.html?ref=recordatorio#derechos`, "-P3D"),
      ...ev(sm, "minimo", "Sube el salario mínimo", `Revisa que tu sueldo no quede abajo del nuevo mínimo: ${CONFIG.SITE}?ref=recordatorio`, "PT9H"),
      "END:VCALENDAR"].join("\r\n");
    FY.download(new Blob([body], { type: "text/calendar" }), "quincy-avisos.ics");
    FY.toast("Ábrelo para agregar los avisos a tu calendario");
  }
  function avisos(host) {
    const A = CONFIG.AVISOS || {}, online = !!(A.whatsappCanal || A.correoForm);
    host.innerHTML = `<h2 class="h2-sm">¿Te aviso cuando te paguen el aguinaldo o suba el salario mínimo?</h2>
      <p class="mut small">Opcional. Nunca te pedimos ni mandamos tus números: solo tu contacto, si tú quieres.</p>
      <div class="actions"><button type="button" class="btn btn-ghost btn-sm av-cal">Ponerlo en mi calendario</button></div>
      ${online ? `<label class="av-ok"><input type="checkbox" class="av-check"> <span>Acepto recibir avisos de Quincy y el <a href="privacidad.html" target="_blank" rel="noopener">aviso de privacidad</a>. Me puedo salir cuando quiera.</span></label>
      <div class="actions">${A.whatsappCanal ? `<a class="btn btn-ghost btn-sm av-go" aria-disabled="true" target="_blank" rel="noopener" href="${esc(A.whatsappCanal)}">Seguir el canal de WhatsApp</a>` : ""}${A.correoForm ? `<a class="btn btn-ghost btn-sm av-go" aria-disabled="true" target="_blank" rel="noopener" href="${esc(A.correoForm)}">Recibir avisos por correo</a>` : ""}</div>` : ""}`;
    host.querySelector(".av-cal").addEventListener("click", avisosICS);
    const chk = host.querySelector(".av-check");
    if (chk) {
      const sync = () => host.querySelectorAll(".av-go").forEach((a) => a.setAttribute("aria-disabled", String(!chk.checked)));
      chk.addEventListener("change", sync);
      host.querySelectorAll(".av-go").forEach((a) => a.addEventListener("click", (e) => { if (!chk.checked) { e.preventDefault(); FY.toast("Primero marca la casilla de aceptación"); chk.focus(); } }));
    }
  }

  // ---------- vista "Tus datos" ----------
  function init() {
    const yo = perfil.get();
    const ed = fijosEditor($("pd-fijos"), yo ? yo.pago.fijos : perfil.DEF.pago.fijos, (list) => {
      if (!perfil.exists()) return;
      perfil.update("pago", { fijos: list, configurado: true });
      FY.quincena.reload();
    }, { id: "pd" });
    $("pd-age").value = FY.state.age;
    $("pd-age").addEventListener("input", () => {
      const v = Math.round(+$("pd-age").value);
      if (!(v >= 18 && v <= 60)) return;
      const a = $("age"); a.value = v; a.dispatchEvent(new Event("input", { bubbles: true }));
    });
    avisos($("pd-avisos"));
    $("pd-export").addEventListener("click", () => {
      const d = new Date(), name = `quincy-respaldo-${FY.dayKey(d)}.json`;
      const data = { app: "quincy", version: 1, fecha: d.toISOString(), datos: perfil.dump() };
      FY.download(new Blob([JSON.stringify(data, null, 1)], { type: "application/json" }), name);
      FY.toast("Respaldo guardado. Guárdalo donde no se pierda.");
    });
    $("pd-import").addEventListener("change", async (e) => {
      const f = e.target.files && e.target.files[0];
      e.target.value = "";
      if (!f) return;
      try {
        const data = JSON.parse(await f.text());
        const datos = data && data.datos ? data.datos : data;
        if (!datos || !datos.yo || !datos.yo.pago) throw new Error("formato");
        perfil.clear();
        if (!perfil.restore(datos)) throw new Error("formato");
        // Recarga ya, antes de que algo en memoria vuelva a escribir encima del respaldo.
        location.reload();
      } catch (er) { FY.toast("Ese archivo no es un respaldo de Quincy."); }
    });
    return { refresh() { const y = perfil.get(); if (y) ed.set(y.pago.fijos); $("pd-age").value = FY.state.age; } };
  }

  FY.perfilUI = { init, fijosEditor, avisos, avisosICS, FIJOS };
})(window.FY);
