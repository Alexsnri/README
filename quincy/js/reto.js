// Quincy · Reto diario: 5 preguntas iguales para todo México, una vez al día, con resultado para compartir.
(function (FY) {
  const { $, fmt, store } = FY;
  const EPOCH = new Date(2026, 9, 1); // 1 de octubre de 2026 = Reto #1
  const REAL = 0.03; // supuesto fijo del juego: 3% al año arriba de la inflación (parecido a CETES hoy)
  const iM = Math.pow(1 + REAL, 1 / 12) - 1;
  const dayNum = (d = new Date()) => Math.floor((new Date(d.getFullYear(), d.getMonth(), d.getDate()) - EPOCH) / 864e5) + 1;
  const grow = (x, years) => x * Math.pow(1 + REAL, years);
  const annuity = (perMonth, years) => perMonth * (Math.pow(1 + iM, years * 12) - 1) / iM;
  const pick = (r, arr) => arr[Math.floor(r() * arr.length)];
  const nice = (v) => { const m = Math.pow(10, Math.floor(Math.log10(v)) - 1); return Math.round(v / m) * m; };
  const shuffle = (r, a) => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };

  const FACTS = [
    ["Solo 7.9% de quienes tienen cuenta para el retiro hace aportaciones voluntarias.", true, "Dato de la ENIF 2024 (INEGI y CNBV)."],
    ["En México, más hombres que mujeres tienen cuenta para el retiro.", true, "51.4% de los hombres contra 34.2% de las mujeres (ENIF 2024)."],
    ["Guardar dinero bajo el colchón protege su valor de la inflación.", false, "Con inflación de 3.45% al año, el dinero guardado sin rendimiento compra menos cada año."],
    ["En CetesDirecto puedes invertir desde $100.", true, "Es el monto mínimo en la plataforma oficial del gobierno."],
    ["Alrededor de 4 de cada 10 personas en México guarda dinero en casa.", true, "41% de la población lo hace (ENIF 2024)."],
    ["Las tandas le pagan intereses a quienes participan.", false, "En una tanda recibes lo mismo que pusiste. No hay rendimiento y la inflación le resta valor."],
    ["El interés compuesto es ganar intereses sobre tus intereses.", true, "Por eso el tiempo pesa tanto: lo que ganas también empieza a ganar."],
    ["Entre más alto el CAT de una tarjeta, más barata es.", false, "El CAT es el Costo Anual Total. Más alto significa más caro."],
    ["La regla del 4% sugiere retirar cada año el 4% de lo que ahorraste.", true, "Es una referencia de planeación (Bengen, 1994), no una garantía."],
    ["La mayoría de quienes usan internet en México se conecta desde el celular.", true, "97.2% lo hace desde un celular (ENDUTIH 2024, INEGI)."],
    ["Si tu ahorro rinde 0% y la inflación es 3.45%, en un año compras lo mismo que hoy.", false, "Compras alrededor de 3.3% menos. Tu dinero no creció y los precios sí."],
    ["Ver una versión envejecida de tu cara puede hacer que ahorres más.", true, "Lo encontró un estudio de Stanford (Hershfield et al., 2011)."],
    ["Puedes consultar tu Afore gratis en la app AforeMóvil.", true, "Es la app oficial de CONSAR."],
    ["CONDUSEF atiende quejas contra bancos y otras instituciones financieras.", true, "Es gratuita y puedes acudir en línea."],
    ["Empezar a ahorrar 10 años antes casi no cambia el resultado final.", false, "Esos 10 años extra de interés compuesto suelen ser los que más pesan."],
    ["Un rendimiento alto en el pasado garantiza el mismo rendimiento en el futuro.", false, "Ningún rendimiento pasado garantiza el futuro."],
    ["El aguinaldo mínimo por ley es de 15 días de salario.", true, "Lo dice el artículo 87 de la Ley Federal del Trabajo."],
    ["El aguinaldo se puede pagar en enero si la empresa lo decide.", false, "Se debe pagar antes del 20 de diciembre (art. 87 LFT)."],
    ["Si entraste a trabajar en julio, no te toca aguinaldo ese año.", false, "Te toca la parte proporcional a los días que trabajaste."],
    ["Con un año trabajado te tocan 12 días de vacaciones pagadas.", true, "Desde 2023, por la reforma de \"vacaciones dignas\" (art. 76 LFT)."],
    ["La prima vacacional mínima es de 25% del sueldo de tus días de vacaciones.", true, "Artículo 80 de la Ley Federal del Trabajo."],
    ["Tu patrón puede pagarte tus vacaciones en dinero para que no las tomes.", false, "Las vacaciones no se pueden cambiar por dinero mientras sigas en el trabajo (art. 79 LFT)."],
    ["Las empresas reparten a sus trabajadores el 10% de sus utilidades.", true, "Es la PTU, y se paga a más tardar el 30 de mayo cuando el patrón es empresa."],
    ["Si renuncias, pierdes tu aguinaldo y vacaciones proporcionales.", false, "Te los deben pagar en tu finiquito, sin importar por qué te vas."],
    ["Si te despiden sin causa, tienes 2 meses para reclamar.", true, "Artículo 518 de la LFT. La asesoría de PROFEDET es gratuita."],
    ["El salario mínimo general en 2026 es de $315.04 al día.", true, "Lo fijó la CONASAMI y está vigente desde el 1 de enero de 2026."]
  ];

  // Genera las 5 preguntas del día n. Mismo n = mismas preguntas para todos.
  function build(n) {
    const r = FY.rng(n * 7919 + 13);
    const qs = [];
    // 1. ¿Qué vale más?
    if (r() < 0.5) {
      let A, B, a, b, tries = 0;
      do {
        const L = pick(r, [5000, 10000, 20000, 30000, 50000]);
        const w = pick(r, [50, 100, 150, 200, 300]), Y = pick(r, [3, 5, 8, 10]);
        A = `${fmt(L)} hoy, una sola vez`; B = `${fmt(w)} cada semana durante ${Y} años`;
        a = grow(L, 30); b = grow(annuity(w * 4.345, Y), 30 - Y);
      } while (Math.abs(a - b) / Math.max(a, b) < 0.15 && ++tries < 30);
      qs.push({ kind: "¿Qué vale más?", text: "¿Qué vale más dentro de 30 años, si crece 3% al año arriba de la inflación?", opts: [A, B], answer: a > b ? 0 : 1,
        explain: `<b>${A}</b> llega a ${fmt(a)}. <b>${B}</b> llega a ${fmt(b)}. Todo en pesos de hoy.` });
    } else {
      const m = pick(r, [500, 1000, 2000]), early = pick(r, [8, 10, 12]), gap = pick(r, [5, 10]);
      const ana = grow(annuity(m, early), 40 - early), beto = annuity(m, 40 - gap);
      qs.push({ kind: "¿Quién tiene más?", text: `Ana guarda ${fmt(m)} al mes desde los 25 durante ${early} años y luego para. Beto empieza a los ${25 + gap} y guarda ${fmt(m)} al mes hasta los 65. Con 3% al año arriba de la inflación, ¿quién tiene más a los 65?`,
        opts: ["Ana", "Beto"], answer: ana > beto ? 0 : 1,
        explain: `Ana puso ${fmt(m * 12 * early)} y llega a ${fmt(ana)}. Beto puso ${fmt(m * 12 * (40 - gap))} y llega a ${fmt(beto)}.` });
    }
    // El orden de las dos opciones se sortea para que la respuesta no sea siempre la misma letra.
    if (r() < 0.5) { const q0 = qs[0]; q0.opts.reverse(); q0.answer = 1 - q0.answer; }
    // 2. Estimación
    const est = () => {
      if (r() < 0.5) {
        const x = pick(r, [1000, 5000, 10000, 25000]), y = pick(r, [20, 25, 30, 40]);
        return { v: grow(x, y), text: `Si guardas ${fmt(x)} hoy y crece 3% al año arriba de la inflación, ¿cuánto vale en ${y} años, en pesos de hoy?`, why: `${fmt(x)} × 1.03 elevado a ${y}.` };
      }
      const a = pick(r, [["un café de $75", 75 * 30.4], ["unos tacos de $120 a la semana", 120 * 4.345], ["comida a domicilio de $250 a la semana", 250 * 4.345]]);
      return { v: grow(annuity(a[1], 1), 29), text: `Si un año entero dejas ${a[0] === "un café de $75" ? "el café de $75 diario" : a[0]} y lo inviertes, ¿cuánto vale 30 años después, en pesos de hoy?`, why: "Un año de ahorro que sigue creciendo 29 años más al 3% real." };
    };
    const e = est();
    const correct = nice(e.v);
    let opts = shuffle(r, [correct, nice(e.v * 0.55), nice(e.v * 1.7)]);
    qs.push({ kind: "Calcula al ojo", text: e.text, opts: opts.map(fmt), answer: opts.indexOf(correct), explain: `La respuesta es cerca de <b>${fmt(e.v)}</b>. ${e.why}` });
    // 3. Regla del 72
    const rate = pick(r, [3, 4, 6, 8, 9, 12]), yrs = Math.round(72 / rate);
    const pool = [6, 8, 9, 12, 18, 24].filter((v) => v !== yrs);
    opts = shuffle(r, [yrs, ...shuffle(r, pool).slice(0, 2)]);
    qs.push({ kind: "Regla del 72", text: `Si tu dinero crece ${rate}% al año, ¿en cuántos años se duplica, más o menos?`, opts: opts.map((v) => `${v} años`), answer: opts.indexOf(yrs),
      explain: `Divide 72 entre la tasa: 72 ÷ ${rate} ≈ <b>${yrs} años</b>. Sirve para cualquier tasa.` });
    // 4 y 5. ¿Verdadero o falso?
    shuffle(r, FACTS.map((_, i) => i)).slice(0, 2).forEach((i) => {
      const [t, v, why] = FACTS[i];
      qs.push({ kind: "¿Verdadero o falso?", text: t, opts: ["Verdadero", "Falso"], answer: v ? 0 : 1, explain: `<b>${v ? "Verdadero" : "Falso"}.</b> ${why}` });
    });
    return shuffle(r, qs);
  }

  // ---------- estado ----------
  const n = dayNum();
  const qs = build(n);
  let play = store.get("reto", null);
  if (!play || play.day !== n) play = { day: n, answers: [], done: false };
  const stats = Object.assign({ played: 0, total: 0, streak: 0, best: 0, lastDay: 0, dist: [0, 0, 0, 0, 0, 0] }, store.get("retoStats", {}));
  if (stats.lastDay && stats.lastDay < n - 1) stats.streak = 0;
  let idx = play.answers.length;
  const saveState = () => { store.set("reto", play); store.set("retoStats", stats); };

  function dots() {
    $("reto-dots").innerHTML = qs.map((_, i) => `<i class="${i < play.answers.length ? (play.answers[i] ? "ok" : "no") : i === idx && !play.done ? "cur" : ""}"></i>`).join("");
  }
  function showQ() {
    dots();
    if (play.done || idx >= qs.length) return finish(false);
    const q = qs[idx];
    $("q-card").hidden = false; $("reto-done").hidden = true;
    $("q-kind").textContent = `Pregunta ${idx + 1} de ${qs.length} · ${q.kind}`;
    $("q-text").textContent = q.text;
    $("q-explain").hidden = true; $("q-next").hidden = true;
    const box = $("q-opts"); box.innerHTML = "";
    q.opts.forEach((o, i) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "opt"; b.innerHTML = `<span>${o}</span><span class="mono">${String.fromCharCode(65 + i)}</span>`;
      b.addEventListener("click", () => answer(i));
      box.appendChild(b);
    });
  }
  function answer(i) {
    if (play.answers.length > idx) return;
    const q = qs[idx], ok = i === q.answer;
    play.answers.push(ok); saveState();
    FY.buzz(ok ? 15 : [30, 40, 30]);
    [...$("q-opts").children].forEach((b, k) => { b.disabled = true; if (k === q.answer) b.classList.add("right"); else if (k === i) b.classList.add("wrong"); });
    $("q-explain").innerHTML = (ok ? "Correcto. " : "Casi. ") + q.explain;
    $("q-explain").hidden = false;
    const nx = $("q-next");
    nx.textContent = idx === qs.length - 1 ? "Ver mi resultado" : "Siguiente";
    nx.hidden = false; nx.focus({ preventScroll: true });
    dots();
  }
  $("q-next").addEventListener("click", () => { idx++; if (idx >= qs.length) finish(true); else showQ(); });

  const score = () => play.answers.filter(Boolean).length;
  const grid = () => play.answers.map((a) => (a ? "🟩" : "🟥")).join("");
  function finish(fresh) {
    if (!play.done) {
      play.done = true;
      const s = score();
      stats.played++; stats.total += s; stats.dist[s]++;
      stats.streak = stats.lastDay === n - 1 ? stats.streak + 1 : 1;
      stats.best = Math.max(stats.best, stats.streak); stats.lastDay = n;
      saveState();
      if (fresh && s >= 4) FY.confetti();
      FY.emit("reto-done", { score: s });
    }
    $("q-card").hidden = true; $("reto-done").hidden = false;
    $("reto-score").textContent = `${score()}/5`;
    $("reto-grid").textContent = grid();
    $("st-played").textContent = stats.played;
    $("st-avg").textContent = stats.played ? (stats.total / stats.played).toFixed(1) : "0";
    $("st-streak").textContent = stats.streak;
    $("st-best").textContent = stats.best;
    const max = Math.max(1, ...stats.dist);
    $("reto-dist").innerHTML = stats.dist.map((c, k) => `<div><span>${k}</span><i class="${k === score() ? "me" : ""}" style="width:${Math.max(6, c / max * 100)}%">${c}</i></div>`).join("");
    $("reto-wa").href = "https://wa.me/?text=" + encodeURIComponent(shareText());
    dots(); markDot();
  }
  function shareText() {
    return `Quincy · Reto #${n} · ${score()}/5\n${grid()}\nRacha: ${stats.streak}\n¿Le ganas? ${FY.shareURL({ reto: n, p: score() })}`;
  }
  $("reto-share").addEventListener("click", async () => {
    const ok = await FY.nativeShare({ text: shareText() });
    if (!ok) FY.copyText(shareText());
    FY.emit("shared", "reto");
  });
  $("reto-copy").addEventListener("click", () => { FY.copyText(shareText()); FY.emit("shared", "reto"); });
  $("reto-wa").addEventListener("click", () => FY.emit("shared", "reto"));

  function markDot() { document.querySelectorAll('[data-dot="reto"]').forEach((d) => { d.hidden = play.done; }); }
  function countdown() {
    const now = new Date(), next = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
    const s = Math.max(0, Math.floor((next - now) / 1000));
    $("reto-next").textContent = [s / 3600, (s % 3600) / 60, s % 60].map((v) => String(Math.floor(v)).padStart(2, "0")).join(":");
    if (s === 0) setTimeout(() => location.reload(), 1500);
  }
  setInterval(() => { if (!$("v-reto").hidden) countdown(); }, 1000);

  function init() { $("reto-num").textContent = `Reto #${n}`; showQ(); countdown(); markDot(); }
  FY.reto = { init, dayNum, build, today: n, result: () => ({ done: play.done, score: score(), grid: grid(), streak: stats.streak }) };
})(window.FY);
