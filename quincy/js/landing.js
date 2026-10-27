// Quincy · portada: campo de partículas en 3D que cambia de forma con el scroll, y textos sincronizados.
(function (FY) {
  const { fmt, ley } = FY;
  const $ = (id) => document.getElementById(id);
  const reduced = FY.reduced;
  const smooth = (a, b, v) => { const t = Math.min(1, Math.max(0, (v - a) / (b - a))); return t * t * (3 - 2 * t); };
  const chapters = [...document.querySelectorAll(".ch")];
  const rail = [...document.querySelectorAll("#rail a")];

  // ---------- palabra que cambia en la portada ----------
  const WORDS = ["toca", "queda", "deben"];
  let wi = 0;
  if (!reduced) setInterval(() => {
    const em = $("swap").firstElementChild;
    em.classList.add("out");
    setTimeout(() => { wi = (wi + 1) % WORDS.length; em.textContent = WORDS[wi]; em.classList.remove("out"); }, 350);
  }, 2600);

  // ---------- demo: cuánto puedes gastar hoy ----------
  function daysToPayday() {
    const t = new Date(), d = t.getDate(), last = new Date(t.getFullYear(), t.getMonth() + 1, 0).getDate();
    const next = d === last ? new Date(t.getFullYear(), t.getMonth() + 1, 15) : d >= 15 ? new Date(t.getFullYear(), t.getMonth(), last) : new Date(t.getFullYear(), t.getMonth(), 15);
    return Math.max(1, ley.diffDays(t, next));
  }
  function demoHoy() {
    const inc = +$("d-income").value, fix = +$("d-fixed").value, n = daysToPayday();
    $("d-income-out").textContent = fmt(inc); $("d-fixed-out").textContent = fmt(fix);
    const daily = Math.max(0, (inc - fix) / n);
    $("d-daily").textContent = fmt(daily);
    $("d-daily").className = "mono " + (inc - fix > 0 ? "ok-t" : "bad-t");
    $("d-days").textContent = inc - fix > 0 ? `Faltan ${n} ${n === 1 ? "día" : "días"} para tu quincena.` : "Tus pagos fijos se comen todo tu pago. Ahí está la primera alerta.";
  }
  ["d-income", "d-fixed"].forEach((id) => $(id).addEventListener("input", demoHoy));

  // ---------- demo: lo que te toca por ley ----------
  let barValues = [1, 1, 1, 1];
  function demoLey() {
    const sal = +$("d-salary").value, yrs = +$("d-years").value, sd = sal / 30;
    const vac = ley.vacationDays(yrs), ag = sd * FY.LEY.aguinaldoDias, prima = vac * sd * FY.LEY.primaVacacional, ptu = sd * 90;
    $("d-salary-out").textContent = fmt(sal); $("d-years-out").textContent = yrs === 1 ? "1 año" : `${yrs} años`;
    $("d-ag").textContent = fmt(ag); $("d-vac").textContent = `${vac} días`; $("d-prima").textContent = fmt(prima); $("d-ptu").textContent = fmt(ptu);
    barValues = [ag, vac * sd, prima, ptu];
    if (scene) scene.rebuild(3);
  }
  ["d-salary", "d-years"].forEach((id) => $(id).addEventListener("input", demoLey));

  // ---------- demo: qué número de la tanda te conviene ----------
  function demoTanda() {
    const n = 10, A = 1000, k = +$("d-turn").value, r = Math.pow(1 + FY.RATES.cetes / 100, 1 / 24) - 1;
    let paid = 0; for (let j = 1; j <= n; j++) paid += A * Math.pow(1 + r, n - j);
    const v = n * A * Math.pow(1 + r, n - k) - paid;
    $("d-turn-out").textContent = `${k} de ${n}`;
    $("d-turn-val").textContent = (v >= 0 ? "+" : "−") + fmt(Math.abs(v));
    $("d-turn-val").className = "mono " + (v >= 0 ? "ok-t" : "bad-t");
    $("d-turn-note").textContent = v >= 0 ? "Te prestan sin intereses: tu número te conviene." : "Ahorras sin rendimiento: tu número te cuesta.";
  }
  $("d-turn").addEventListener("input", demoTanda);

  // ---------- calendario ----------
  function dates() {
    const t = new Date(), y = t.getFullYear();
    const after = (m, d) => { const x = new Date(y, m, d); return ley.diffDays(t, x) >= 0 ? x : new Date(y + 1, m, d); };
    const pay = FY.addDays(t, daysToPayday());
    const ev = [
      { d: pay, t: "Tu próxima quincena", s: "El 15 y el último día de cada mes." },
      { d: after(11, 19), t: "Aguinaldo", s: "Fecha límite por ley: mínimo 15 días de salario." },
      { d: after(0, 1), t: "Nuevo salario mínimo", s: "Revisa que tu sueldo no quede abajo." },
      { d: after(4, 30), t: "Reparto de utilidades", s: "Si tu empresa tuvo ganancias, te toca PTU." }
    ].sort((a, b) => a.d - b.d);
    $("dates").innerHTML = ev.map((e, i) => {
      const n = ley.diffDays(t, e.d);
      return `<li class="glass" data-in="${(0.12 + i * 0.1).toFixed(2)}"><span class="n">${n === 0 ? "Hoy" : n}<small>${n === 0 ? "" : n === 1 ? "día" : "días"}</small></span><div><b>${e.t} · ${e.d.toLocaleDateString("es-MX", { day: "numeric", month: "short" })}</b><span>${e.s}</span></div></li>`;
    }).join("");
  }

  // ---------- avatar que envejece con el scroll ----------
  let lastAge = -1;
  function avatarAt(age) {
    if (age === lastAge) return;
    lastAge = age;
    $("l-avatar").innerHTML = FY.avatar.svg(age, age < 40 ? "mid" : "ok", 2, "long");
    $("l-age").textContent = age; $("l-year").textContent = FY.YEAR + (age - 28);
  }

  // ---------- escena 3D ----------
  let scene = null;
  function initScene() {
    if (!window.THREE) throw new Error("three");
    const T = window.THREE;
    const canvas = $("scene");
    const renderer = new T.WebGLRenderer({ canvas, antialias: false, alpha: true, powerPreference: "high-performance" });
    const PR = Math.min(1.75, devicePixelRatio || 1);
    renderer.setPixelRatio(PR);
    const camera = new T.PerspectiveCamera(45, 1, 0.1, 100);
    camera.position.set(0, 0, 7.2);
    const world = new T.Scene();
    const group = new T.Group(); world.add(group);
    const N = innerWidth < 760 ? 4200 : 8500;

    // Formas: cada una devuelve posiciones y colores para N partículas.
    const C = { sun: [1, 0.71, 0.28], tide: [0.35, 0.84, 0.78], ok: [0.53, 0.89, 0.66], ice: [0.86, 0.93, 0.95], dim: [0.16, 0.36, 0.42] };
    const mixc = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
    function make(fn) {
      const pos = new Float32Array(N * 3), col = new Float32Array(N * 3), r = FY.rng(fn.length * 97 + 7);
      for (let i = 0; i < N; i++) { const p = fn(i, r); pos.set(p.p, i * 3); col.set(p.c, i * 3); }
      return { pos, col };
    }
    const orb = () => make((i, r) => {
      if (i < N * 0.66) {
        const k = i / (N * 0.66), y = 1 - 2 * k, rad = Math.sqrt(1 - y * y), th = i * 2.399963;
        const R = 1.45 + (r() - 0.5) * 0.06;
        return { p: [Math.cos(th) * rad * R, y * R, Math.sin(th) * rad * R], c: mixc(C.tide, C.sun, (y + 1) / 2) };
      }
      const a = r() * Math.PI * 2, R = 2.15 + r() * 0.75, x = Math.cos(a) * R, z = Math.sin(a) * R, yy = (r() - 0.5) * 0.05;
      const tilt = 0.42, cy = yy * Math.cos(tilt) - z * Math.sin(tilt), cz = yy * Math.sin(tilt) + z * Math.cos(tilt);
      return { p: [x, cy, cz], c: mixc(C.sun, C.ice, r() * 0.4) };
    });
    function textPoints(str) {
      const W = 640, H = 320, cv = document.createElement("canvas"); cv.width = W; cv.height = H;
      const x = cv.getContext("2d", { willReadFrequently: true });
      x.fillStyle = "#fff"; x.textAlign = "center"; x.textBaseline = "middle";
      x.font = "800 250px Unbounded, 'Arial Black', sans-serif"; x.fillText(str, W / 2, H / 2 + 10);
      const d = x.getImageData(0, 0, W, H).data, pts = [];
      for (let yy = 0; yy < H; yy += 2) for (let xx = 0; xx < W; xx += 2) if (d[(yy * W + xx) * 4 + 3] > 128) pts.push([xx, yy]);
      return { pts, W, H };
    }
    let fifteen = null;
    const text15 = () => { const t = textPoints("15"); return make((i, r) => {
      const q = t.pts[Math.floor(r() * t.pts.length)] || [t.W / 2, t.H / 2];
      const px = (q[0] / t.W - 0.5) * 5.2, py = -(q[1] / t.H - 0.5) * 2.6;
      return { p: [px + (r() - 0.5) * 0.02, py + (r() - 0.5) * 0.02, (r() - 0.5) * 0.45], c: mixc(C.sun, C.tide, (px + 2.6) / 5.2 * 0.6) };
    }); };
    const gauge = () => make((i, r) => {
      const u = r() * Math.PI * 2, v = r() * Math.PI * 2, R = 1.75, rr = 0.16 + r() * 0.03;
      const frac = ((u / (Math.PI * 2)) + 0.25) % 1; // 0 arriba
      return { p: [(R + rr * Math.cos(v)) * Math.cos(u), (R + rr * Math.cos(v)) * Math.sin(u), rr * Math.sin(v)], c: frac < 0.7 ? C.ok : C.dim };
    });
    const bars = () => {
      const max = Math.max(...barValues, 1), cols = [C.sun, C.tide, C.ok, C.ice];
      return make((i, r) => {
        const b = i % 4, h = 0.35 + 2.6 * barValues[b] / max, x0 = -1.05 + b * 0.78, w = 0.5;
        const face = r(), a = r(), c = r();
        let p;
        if (face < 0.18) p = [x0 + (a - 0.5) * w, -1.4 + h, (c - 0.5) * w];
        else { const side = Math.floor(r() * 4); const s = (a - 0.5) * w, y = -1.4 + c * h; p = side === 0 ? [x0 + s, y, w / 2] : side === 1 ? [x0 + s, y, -w / 2] : side === 2 ? [x0 + w / 2, y, s] : [x0 - w / 2, y, s]; }
        return { p, c: mixc(cols[b], C.ice, face < 0.18 ? 0.35 : 0) };
      });
    };
    const calendar = () => make((i, r) => {
      const cell = i % 35, col = cell % 7, row = Math.floor(cell / 7), today = (new Date().getDate() - 1) % 35;
      const sz = 0.36, gap = 0.1, x0 = (col - 3) * (sz + gap), y0 = (2 - row) * (sz + gap);
      const hot = cell === today, s = hot ? sz * 1.25 : sz;
      return { p: [x0 + (r() - 0.5) * s, y0 + (r() - 0.5) * s, (r() - 0.5) * (hot ? 0.5 : 0.12) + (hot ? 0.25 : 0)], c: hot ? C.sun : mixc(C.dim, C.tide, 0.35 + r() * 0.3) };
    });
    const hourglass = () => make((i, r) => {
      const k = r();
      if (k < 0.12) { const a = r() * Math.PI * 2, R = Math.sqrt(r()) * 1.25, top = r() < 0.5; return { p: [Math.cos(a) * R, top ? 1.75 : -1.75, Math.sin(a) * R], c: C.ice }; }
      if (k < 0.3) { const a = r() * Math.PI * 2, hgt = r() * 0.7, R = (1 - hgt / 0.7) * 1.05 * Math.sqrt(r()); return { p: [Math.cos(a) * R, -1.7 + hgt, Math.sin(a) * R], c: C.sun }; }
      if (k < 0.36) return { p: [(r() - 0.5) * 0.05, (r() - 0.5) * 3.2, (r() - 0.5) * 0.05], c: C.sun };
      const y = (r() * 2 - 1) * 1.7, a = r() * Math.PI * 2, R = 0.06 + 1.1 * Math.abs(y) / 1.7;
      return { p: [Math.cos(a) * R, y, Math.sin(a) * R], c: mixc(C.tide, C.ice, Math.abs(y) / 1.7 * 0.5) };
    });
    const galaxy = () => make((i, r) => {
      const arm = i % 3, rad = Math.pow(r(), 0.55) * 3.1, ang = rad * 1.5 + arm * (Math.PI * 2 / 3) + (r() - 0.5) * 0.5;
      return { p: [Math.cos(ang) * rad, (r() - 0.5) * 0.18 * (3.2 - rad), Math.sin(ang) * rad], c: mixc(C.sun, C.tide, Math.min(1, rad / 3)) };
    });
    // Círculo de personas: la tanda. Una persona brilla porque "le toca".
    const circle = () => make((i, r) => {
      const ppl = 10, k = i % ppl;
      if (r() < 0.16) { const a = r() * Math.PI * 2; return { p: [Math.cos(a) * 1.6, (r() - 0.5) * 0.04, Math.sin(a) * 1.6], c: C.dim }; }
      const a = (k / ppl) * Math.PI * 2 + Math.PI / 2, cx = Math.cos(a) * 1.6, cz = Math.sin(a) * 1.6;
      const u = r() * 2 - 1, th = r() * Math.PI * 2, rad = Math.sqrt(1 - u * u), R = k === 0 ? 0.32 : 0.22;
      return { p: [cx + Math.cos(th) * rad * R, u * R + (k === 0 ? 0.25 : 0), cz + Math.sin(th) * rad * R], c: k === 0 ? C.sun : mixc(C.tide, C.ice, 0.25) };
    });
    const builders = [orb, text15, gauge, bars, calendar, circle, hourglass, galaxy];
    // Inclinación y giro por forma: las letras miran de frente, el planeta y la galaxia giran.
    const POSE = [{ tilt: 0.18, spin: 1 }, { tilt: 0, spin: 0.12 }, { tilt: 0, spin: 0.25 }, { tilt: 0.12, spin: 0.6 }, { tilt: 0, spin: 0.15 }, { tilt: 0.55, spin: 1 }, { tilt: 0.05, spin: 1 }, { tilt: 0.95, spin: 1 }];
    const shapes = builders.map((b) => b());

    const geo = new T.BufferGeometry();
    const rand = new Float32Array(N); { const r = FY.rng(3); for (let i = 0; i < N; i++) rand[i] = r(); }
    geo.setAttribute("position", new T.BufferAttribute(new Float32Array(shapes[0].pos), 3));
    geo.setAttribute("aFrom", new T.BufferAttribute(new Float32Array(shapes[0].pos), 3));
    geo.setAttribute("aTo", new T.BufferAttribute(new Float32Array(shapes[1].pos), 3));
    geo.setAttribute("cFrom", new T.BufferAttribute(new Float32Array(shapes[0].col), 3));
    geo.setAttribute("cTo", new T.BufferAttribute(new Float32Array(shapes[1].col), 3));
    geo.setAttribute("aRand", new T.BufferAttribute(rand, 1));
    const mat = new T.ShaderMaterial({
      transparent: true, depthWrite: false, blending: T.AdditiveBlending,
      uniforms: { uMix: { value: 0 }, uTime: { value: 0 }, uSize: { value: innerWidth < 760 ? 22 : 26 }, uPR: { value: PR } },
      vertexShader: `
        attribute vec3 aFrom; attribute vec3 aTo; attribute vec3 cFrom; attribute vec3 cTo; attribute float aRand;
        uniform float uMix; uniform float uTime; uniform float uSize; uniform float uPR;
        varying vec3 vColor; varying float vAlpha;
        void main() {
          float m = clamp((uMix - aRand * 0.3) / 0.7, 0.0, 1.0);
          m = m * m * (3.0 - 2.0 * m);
          vec3 p = mix(aFrom, aTo, m);
          float burst = sin(m * 3.14159) * 0.9;
          p += normalize(p + vec3(0.001)) * burst * (aRand - 0.35);
          p += 0.035 * vec3(sin(uTime * 0.9 + aRand * 40.0), cos(uTime * 0.7 + aRand * 30.0), sin(uTime * 0.8 + aRand * 20.0));
          vColor = mix(cFrom, cTo, m);
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          gl_PointSize = uSize * uPR * (0.45 + aRand * 0.75) / -mv.z;
          gl_Position = projectionMatrix * mv;
          vAlpha = 0.6 + 0.4 * aRand;
        }`,
      fragmentShader: `
        varying vec3 vColor; varying float vAlpha;
        void main() {
          vec2 c = gl_PointCoord - 0.5; float d = length(c);
          if (d > 0.5) discard;
          float a = smoothstep(0.5, 0.0, d);
          gl_FragColor = vec4(vColor * (0.85 + a * 0.9), a * vAlpha);
        }`
    });
    const points = new T.Points(geo, mat);
    points.frustumCulled = false;
    group.add(points);

    let pair = [0, 1];
    function setPair(a, b) {
      pair = [a, b];
      geo.attributes.aFrom.array.set(shapes[a].pos); geo.attributes.cFrom.array.set(shapes[a].col);
      geo.attributes.aTo.array.set(shapes[b].pos); geo.attributes.cTo.array.set(shapes[b].col);
      ["aFrom", "aTo", "cFrom", "cTo"].forEach((k) => { geo.attributes[k].needsUpdate = true; });
    }
    function rebuild(k) { shapes[k] = builders[k](); if (pair.includes(k)) setPair(pair[0], pair[1]); }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => rebuild(1)).catch(() => {});

    function size() {
      const w = innerWidth, h = innerHeight;
      renderer.setSize(w, h, false);
      camera.aspect = w / h; camera.updateProjectionMatrix();
      const wide = w / h > 1.05;
      group.position.set(wide ? 1.95 : 0, wide ? 0 : 0.6, 0);
      group.scale.setScalar(wide ? 1.12 : Math.min(0.85, w / 460));
      points.material.opacity = 1;
      document.body.classList.toggle("narrow", !wide);
    }
    size();
    return { renderer, camera, world, group, points, mat, setPair, rebuild, size, pair: () => pair, POSE };
  }

  // ---------- scroll: forma, textos, contadores ----------
  let tops = [], heights = [], vh = innerHeight;
  function measure() {
    vh = innerHeight;
    tops = chapters.map((c) => c.offsetTop); heights = chapters.map((c) => c.offsetHeight);
  }
  const items = chapters.map((c) => [...c.querySelectorAll("[data-in]")]);
  const panels = chapters.map((c) => c.querySelector(".panel"));
  let mx = 0, my = 0, tmx = 0, tmy = 0;
  addEventListener("pointermove", (e) => { tmx = e.clientX / innerWidth * 2 - 1; tmy = e.clientY / innerHeight * 2 - 1; }, { passive: true });

  let cur = -1, t0 = performance.now(), countShown = -1;
  function frame(now) {
    const y = scrollY;
    let i = 0;
    for (let j = 0; j < chapters.length; j++) if (tops[j] <= y + 1) i = j;
    const lp = (j) => Math.min(1, Math.max(0, (y - tops[j]) / Math.max(1, heights[j] - vh)));
    const enter = (j) => Math.min(1, Math.max(0, (y - (tops[j] - vh)) / vh));
    // Textos
    if (!reduced) chapters.forEach((c, j) => {
      if (Math.abs(j - i) > 1) return;
      const p = lp(j), e = enter(j), last = j === chapters.length - 1;
      const out = last ? 0 : smooth(0.8, 0.98, p);
      panels[j].style.opacity = String(1 - out);
      panels[j].style.transform = `translateY(${(-out * 60).toFixed(1)}px)`;
      items[j].forEach((el) => {
        const a = parseFloat(el.dataset.in) || 0;
        const r = j === 0 ? 1 : a === 0 ? smooth(0.3, 0.85, e) : smooth(a, a + 0.14, p);
        el.style.opacity = r.toFixed(3);
        el.style.transform = `translateY(${((1 - r) * 28).toFixed(1)}px)`;
        el.style.filter = r < 0.99 ? `blur(${((1 - r) * 6).toFixed(1)}px)` : "";
      });
    });
    // Contador del IMSS que avanza con el scroll
    const cnt = $("count-imss"), to = +cnt.dataset.to;
    const v = reduced ? to : Math.round(to * smooth(0.18, 0.48, lp(1)));
    if (v !== countShown) { countShown = v; cnt.textContent = v.toLocaleString("es-MX"); }
    // Avatar que envejece
    avatarAt(reduced ? 65 : 28 + Math.round(37 * smooth(0.05, 0.72, lp(6))));
    // Riel
    const mixNow = i < chapters.length - 1 ? smooth(0.62, 1, lp(i)) : 0;
    const active = mixNow > 0.5 ? i + 1 : i;
    if (active !== cur) { cur = active; rail.forEach((a, k) => a.classList.toggle("on", k === active)); }
    // Escena
    if (scene) {
      const next = Math.min(i + 1, chapters.length - 1);
      const pr = scene.pair();
      if (pr[0] !== i || pr[1] !== next) scene.setPair(i, next);
      scene.mat.uniforms.uMix.value = reduced ? (mixNow > 0.5 ? 1 : 0) : mixNow;
      const t = (now - t0) / 1000;
      scene.mat.uniforms.uTime.value = reduced ? 0 : t;
      mx += (tmx - mx) * 0.05; my += (tmy - my) * 0.05;
      const A = scene.POSE[i], B = scene.POSE[next], k = mixNow;
      const spin = A.spin + (B.spin - A.spin) * k, tilt = A.tilt + (B.tilt - A.tilt) * k;
      scene.group.rotation.y = (reduced ? 0 : Math.sin(t * 0.22) * 0.45 * spin) + mx * 0.3;
      scene.group.rotation.x = tilt + (reduced ? 0 : Math.sin(t * 0.17) * 0.08) + my * 0.15;
      scene.camera.position.z = 7.2 - (reduced ? 0 : 0.7 * Math.sin(Math.PI * lp(i)));
      scene.renderer.render(scene.world, scene.camera);
    }
    if (!document.hidden) requestAnimationFrame(frame); else running = false;
  }
  let running = false;
  function start() { if (!running) { running = true; requestAnimationFrame(frame); } }
  document.addEventListener("visibilitychange", () => { if (!document.hidden) start(); });
  addEventListener("resize", () => { measure(); if (scene) scene.size(); });
  addEventListener("load", measure);

  // ---------- arranque ----------
  demoHoy(); demoLey(); demoTanda(); dates();
  items[4] = [...chapters[4].querySelectorAll("[data-in]")];
  try { scene = initScene(); } catch (e) { document.body.classList.add("no-webgl"); scene = null; }
  demoLey();
  measure(); start();
})(window.FY);
