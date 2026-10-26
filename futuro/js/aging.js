// Futuro Yo · envejecimiento de fotos dentro del teléfono.
// MediaPipe (Google) encuentra 478 puntos del rostro y separa el cabello del fondo.
// Con eso pintamos canas, arrugas, ojeras, flacidez y manchas en su lugar real.
// La foto nunca sale del dispositivo.
(function (FY) {
  const MP = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.35";
  const N = 640; // tamaño del retrato recortado
  let loading = null;

  // Índices de la malla facial de MediaPipe.
  const OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109];
  const LIPS = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146];
  const BROW_A = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46];
  const BROW_B = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276];
  const LOW_A = [133, 155, 154, 153, 145, 144, 163, 7, 33]; // párpado inferior, ojo a la izquierda de la imagen
  const LOW_B = [362, 382, 381, 380, 374, 373, 390, 249, 263];
  const UP_A = [33, 246, 161, 160, 159, 158, 157, 173, 133];
  const UP_B = [263, 466, 388, 387, 386, 385, 384, 398, 362];

  async function create(vision, files, Kind, opts) {
    try { return await Kind.createFromOptions(files, { ...opts, baseOptions: { ...opts.baseOptions, delegate: "GPU" } }); }
    catch (e) { return await Kind.createFromOptions(files, { ...opts, baseOptions: { ...opts.baseOptions, delegate: "CPU" } }); }
  }
  function load(onStep) {
    if (!loading) {
      loading = (async () => {
        onStep && onStep("Descargando la IA (solo la primera vez)…");
        const vision = await import(MP + "/vision_bundle.mjs");
        let files = await vision.FilesetResolver.forVisionTasks(FY.CONFIG.MP_WASM || MP + "/wasm");
        if (FY.CONFIG.MP_WASM_BINARY) files = { ...files, wasmBinaryPath: FY.CONFIG.MP_WASM_BINARY };
        const MODELS = FY.CONFIG.MODELS;
        onStep && onStep("Preparando el detector de rostro…");
        const face = await create(vision, files, vision.FaceLandmarker, { baseOptions: { modelAssetPath: MODELS + FY.CONFIG.FACE_MODEL }, runningMode: "IMAGE", numFaces: 3 });
        onStep && onStep("Preparando el detector de cabello…");
        const hair = await create(vision, files, vision.ImageSegmenter, { baseOptions: { modelAssetPath: MODELS + FY.CONFIG.HAIR_MODEL }, runningMode: "IMAGE", outputConfidenceMasks: true, outputCategoryMask: false });
        return { face, hair };
      })().catch((e) => { loading = null; throw e; });
    }
    return loading;
  }

  function fileToCanvas(file) {
    return new Promise((res, rej) => {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        const k = Math.min(1, 1400 / Math.max(img.naturalWidth, img.naturalHeight));
        const c = document.createElement("canvas");
        c.width = Math.max(1, Math.round(img.naturalWidth * k)); c.height = Math.max(1, Math.round(img.naturalHeight * k));
        c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url); res(c);
      };
      img.onerror = () => { URL.revokeObjectURL(url); rej(new Error("img")); };
      img.src = url;
    });
  }

  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
  const avg = (ps) => ({ x: ps.reduce((s, p) => s + p.x, 0) / ps.length, y: ps.reduce((s, p) => s + p.y, 0) / ps.length });
  const lerp = (a, b, t) => ({ x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t });
  const sm = (e0, e1, v) => { const t = Math.min(1, Math.max(0, (v - e0) / (e1 - e0))); return t * t * (3 - 2 * t); };

  // Encuentra la cara más grande, recorta un retrato N×N y calcula la máscara de cabello.
  async function detect(src, onStep) {
    const ai = await load(onStep);
    onStep && onStep("Buscando tu rostro…");
    const res = ai.face.detect(src);
    if (!res.faceLandmarks || !res.faceLandmarks.length) return null;
    const faces = res.faceLandmarks.map((lm) => lm.map((p) => ({ x: p.x * src.width, y: p.y * src.height })));
    faces.sort((a, b) => dist(b[234], b[454]) - dist(a[234], a[454]));
    const pts = faces[0];
    const s = dist(pts[9], pts[152]);
    if (s < 30) return null;
    let size = Math.max(s * 2.3, Math.min(s * 3.1, src.width, src.height));
    const c0 = lerp(avg(pts), pts[10], 0.45);
    let sx = c0.x - size / 2, sy = c0.y - size / 2;
    if (size <= src.width) sx = Math.min(Math.max(0, sx), src.width - size);
    if (size <= src.height) sy = Math.min(Math.max(0, sy), src.height - size);
    const c = document.createElement("canvas");
    c.width = c.height = N;
    const x = c.getContext("2d");
    x.fillStyle = "#0b1f2a"; x.fillRect(0, 0, N, N);
    x.drawImage(src, sx, sy, size, size, 0, 0, N, N);
    const k = N / size;
    const portrait = { canvas: c, pts: pts.map((p) => ({ x: (p.x - sx) * k, y: (p.y - sy) * k })) };
    onStep && onStep("Separando tu cabello…");
    portrait.hair = segmentHair(ai.hair, c);
    return portrait;
  }

  function segmentHair(segmenter, canvas) {
    const out = new Float32Array(N * N);
    const r = segmenter.segment(canvas);
    try {
      const masks = r.confidenceMasks || [];
      const m = masks[masks.length > 1 ? 1 : 0];
      if (!m) return out;
      const w = m.width, h = m.height, d = m.getAsFloat32Array();
      for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
        out[y * N + x] = d[Math.min(h - 1, Math.floor(y * h / N)) * w + Math.min(w - 1, Math.floor(x * w / N))];
      }
    } finally { if (r.close) r.close(); }
    return out;
  }

  function valueNoise(g, r) {
    const grid = new Float32Array((g + 1) * (g + 1)).map(() => r() * 2 - 1);
    const out = new Float32Array(N * N);
    for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
      const gx = (x / N) * g, gy = (y / N) * g, x0 = gx | 0, y0 = gy | 0, fx = gx - x0, fy = gy - y0;
      const a = grid[y0 * (g + 1) + x0], b = grid[y0 * (g + 1) + x0 + 1], c = grid[(y0 + 1) * (g + 1) + x0], e = grid[(y0 + 1) * (g + 1) + x0 + 1];
      out[y * N + x] = (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + e * fx) * fy;
    }
    return out;
  }

  // Dibuja una figura en baja resolución y la escala: bordes suaves sin depender de ctx.filter.
  function softMask(draw, down) {
    const s = Math.round(N / down);
    const c = document.createElement("canvas"); c.width = c.height = s;
    const x = c.getContext("2d"); x.fillStyle = "#fff"; x.strokeStyle = "#fff"; x.scale(s / N, s / N); draw(x);
    const big = document.createElement("canvas"); big.width = big.height = N;
    const b = big.getContext("2d", { willReadFrequently: true }); b.imageSmoothingEnabled = true; b.imageSmoothingQuality = "high";
    b.drawImage(c, 0, 0, N, N);
    const d = b.getImageData(0, 0, N, N).data, out = new Float32Array(N * N);
    for (let j = 0; j < out.length; j++) out[j] = d[j * 4 + 3] / 255;
    return out;
  }
  const path = (x, ps) => { x.beginPath(); ps.forEach((p, i) => i ? x.lineTo(p.x, p.y) : x.moveTo(p.x, p.y)); x.closePath(); };

  // Precalcula geometría, máscaras y colores; una sola vez por foto.
  function prepare(portrait) {
    const { canvas, pts } = portrait;
    const base = canvas.getContext("2d", { willReadFrequently: true }).getImageData(0, 0, N, N);
    const d = base.data;
    const L = avg([pts[33], pts[133]]), R = avg([pts[263], pts[362]]);
    const exLen = dist(L, R) || 1;
    const ex = { x: (R.x - L.x) / exLen, y: (R.y - L.y) / exLen };
    const up = { x: ex.y, y: -ex.x };
    const faceH = dist(pts[9], pts[152]);
    const faceW = dist(pts[234], pts[454]);
    const hairP = portrait.hair || new Float32Array(N * N);

    const oval = softMask((x) => { path(x, OVAL.map((i) => pts[i])); x.fill(); }, 8);
    const neck = softMask((x) => {
      const a = pts[172], b = pts[397], c = pts[152];
      const dn = (p, k) => ({ x: p.x - up.x * faceH * k, y: p.y - up.y * faceH * k });
      path(x, [a, c, b, dn(b, 0.55), dn(c, 0.6), dn(a, 0.55)]); x.fill();
    }, 8);
    const brows = softMask((x) => { [BROW_A, BROW_B].forEach((ids) => { path(x, ids.map((i) => pts[i])); x.fill(); x.lineWidth = faceW * 0.012; x.stroke(); }); }, 3);
    const lips = softMask((x) => { path(x, LIPS.map((i) => pts[i])); x.fill(); }, 4);

    const sample = (p, r) => {
      let n = 0; const s = [0, 0, 0];
      for (let y = Math.round(p.y - r); y <= p.y + r; y++) for (let x = Math.round(p.x - r); x <= p.x + r; x++) {
        if (x < 0 || y < 0 || x >= N || y >= N) continue;
        const i = (y * N + x) * 4; s[0] += d[i]; s[1] += d[i + 1]; s[2] += d[i + 2]; n++;
      }
      return n ? s.map((v) => v / n) : null;
    };
    const skinS = [pts[50], pts[280], pts[151], pts[5]].map((p) => sample(p, faceW * 0.03)).filter(Boolean);
    const skin = [0, 1, 2].map((k) => skinS.reduce((s, c) => s + c[k], 0) / skinS.length);
    const cd = (i, c) => Math.hypot(d[i] - c[0], d[i + 1] - c[1], d[i + 2] - c[2]);
    const lumAt = (i) => 0.3 * d[i] + 0.59 * d[i + 1] + 0.11 * d[i + 2];
    const skinLum = 0.3 * skin[0] + 0.59 * skin[1] + 0.11 * skin[2];
    let hs = 0, hn = 0;
    for (let j = 0; j < N * N; j += 3) if (hairP[j] > 0.6) { hs += lumAt(j * 4); hn++; }
    const hairLum = hn ? hs / hn : 60;

    // Máscaras finales por pixel.
    const skinM = new Float32Array(N * N), hairW = new Float32Array(N * N);
    for (let j = 0, i = 0; j < N * N; j++, i += 4) {
      const hp = sm(0.35, 0.8, hairP[j]);
      const like = sm(95, 40, cd(i, skin));
      skinM[j] = Math.max(oval[j], neck[j] * like) * (1 - hp) * (0.35 + 0.65 * like);
      let w = hp;
      if (brows[j] > 0.05) w = Math.max(w, brows[j] * sm(8, 50, skinLum - lumAt(i)) * 0.45);
      hairW[j] = w;
    }

    // Ruido suave (manchas de pigmento) y fino (textura de piel madura).
    const r = FY.rng(97);
    const noise = valueNoise(18, r), fine = valueNoise(150, r);
    const spots = Array.from({ length: 18 }, () => {
      const anchor = [pts[50], pts[280], pts[151], pts[127], pts[356], pts[205], pts[425]][(r() * 7) | 0];
      return { p: { x: anchor.x + (r() - 0.5) * faceW * 0.16, y: anchor.y + (r() - 0.5) * faceH * 0.16 }, s: faceW * (0.006 + r() * 0.01), k: r() };
    });
    return { canvas, pts, base, skinM, hairW, lips, noise, fine, skin, skinLum, hairLum, ex, up, faceH, faceW, spots };
  }

  // t: envejecimiento (0 = hoy, 1 = muy mayor). gray: cuánta cana (0–1).
  function render(f, t, gray, out) {
    out = out || document.createElement("canvas");
    out.width = out.height = N;
    const ctx = out.getContext("2d");
    if (t <= 0.001 && gray <= 0.001) { ctx.putImageData(f.base, 0, 0); return out; }
    const src = f.base.data;
    const img = new ImageData(new Uint8ClampedArray(src), N, N);
    const d = img.data;
    const { pts, up, ex, faceH: H, faceW: W } = f;

    // 1. Flacidez: cachetes y papada bajan un poco.
    const sag = H * 0.05 * t;
    if (sag > 0.3) {
      const J = [lerp(pts[172], pts[61], 0.35), lerp(pts[397], pts[291], 0.35), lerp(pts[152], pts[17], 0.2)];
      const sig = W * 0.13, rad = sig * 3;
      J.forEach((c, n) => {
        const amt = n === 2 ? sag * 0.5 : sag;
        for (let y = Math.max(0, Math.floor(c.y - rad)); y < Math.min(N, c.y + rad); y++) for (let x = Math.max(0, Math.floor(c.x - rad)); x < Math.min(N, c.x + rad); x++) {
          const w = Math.exp(-((x - c.x) ** 2 + (y - c.y) ** 2) / (2 * sig * sig)) * f.skinM[y * N + x];
          if (w < 0.02) continue;
          const sx = x + up.x * amt * w, sy = y + up.y * amt * w;
          const x0 = Math.floor(sx), y0 = Math.floor(sy), fx = sx - x0, fy = sy - y0;
          if (x0 < 0 || y0 < 0 || x0 >= N - 1 || y0 >= N - 1) continue;
          const i = (y * N + x) * 4, a = (y0 * N + x0) * 4, b = a + 4, c2 = a + N * 4, e = c2 + 4;
          for (let k = 0; k < 3; k++) d[i + k] = (src[a + k] * (1 - fx) + src[b + k] * fx) * (1 - fy) + (src[c2 + k] * (1 - fx) + src[e + k] * fx) * fy;
        }
      });
    }

    // 2. Canas. 3. Piel con menos brillo y color, pigmentación irregular. 4. Labios más pálidos.
    for (let j = 0, i = 0; j < N * N; j++, i += 4) {
      const hw = f.hairW[j] * gray;
      const m = f.skinM[j] * t;
      const lp = f.lips[j] * t;
      if (hw < 0.01 && m < 0.01 && lp < 0.01) continue;
      let r = d[i], g = d[i + 1], b = d[i + 2];
      if (hw >= 0.01) {
        const lum = 0.3 * r + 0.59 * g + 0.11 * b;
        const sv = Math.min(232, Math.max(55, f.skinLum * (0.8 + 0.18 * gray) + (lum - f.hairLum) * 1.35));
        const k = hw * 0.9;
        r += (sv - 2 + (r - lum) * 0.12 - r) * k; g += (sv + (g - lum) * 0.12 - g) * k; b += (sv + 4 + (b - lum) * 0.12 - b) * k;
      }
      if (m >= 0.01) {
        const l2 = 0.3 * r + 0.59 * g + 0.11 * b;
        const de = 0.22 * m;
        r += (l2 - r) * de + 5 * m; g += (l2 - g) * de; b += (l2 - b) * de - 7 * m;
        const k = 1 - 0.05 * m + 0.06 * m * f.noise[j] + 0.04 * m * f.fine[j];
        r *= k; g *= k; b *= k;
        // La piel madura pierde brillo: bajan los puntos de luz.
        const hi = (0.3 * r + 0.59 * g + 0.11 * b) - 185;
        if (hi > 0) { const c = 1 - (hi / 70) * 0.35 * m; r = 185 + (r - 185) * c; g = 185 + (g - 185) * c; b = 185 + (b - 185) * c; }
      }
      if (lp >= 0.01) {
        const l3 = 0.3 * r + 0.59 * g + 0.11 * b;
        r += (l3 - r) * lp * 0.35; g += (l3 - g) * lp * 0.35; b += (l3 - b) * lp * 0.35;
      }
      d[i] = r; d[i + 1] = g; d[i + 2] = b;
    }
    ctx.putImageData(img, 0, 0);

    // 5. Arrugas en capas aparte, que solo caen sobre piel.
    const darkL = layer(), lightL = layer();
    const dx = darkL.getContext("2d"), lx = lightL.getContext("2d");
    const dark = `rgb(${f.skin.map((v) => Math.round(v * 0.42)).join(",")})`;
    const ramp = (a, b) => FY.clamp((t - a) / (b - a), 0, 1);
    const at = (p, u, v) => ({ x: p.x + ex.x * u + up.x * v, y: p.y + ex.y * u + up.y * v });
    const q = (a, c, b, n = 14) => Array.from({ length: n + 1 }, (_, s) => { const k = s / n; return { x: (1 - k) ** 2 * a.x + 2 * (1 - k) * k * c.x + k * k * b.x, y: (1 - k) ** 2 * a.y + 2 * (1 - k) * k * c.y + k * k * b.y }; });
    // Un pliegue: línea oscura que se adelgaza en las puntas y un brillo fino arriba.
    const crease = (ps, width, alpha) => {
      if (alpha <= 0.01) return;
      for (let s = 1; s < ps.length; s++) {
        const k = Math.sin(Math.PI * ((s - 0.5) / (ps.length - 1))) * (0.55 + 0.45 * Math.abs(Math.sin(s * 1.9 + ps[0].x * 0.07)));
        [[2.4, 0.16], [1.3, 0.38], [0.6, 0.7]].forEach(([wk, ak]) => {
          dx.strokeStyle = dark; dx.lineCap = "round"; dx.globalAlpha = alpha * ak * k; dx.lineWidth = width * wk * (0.5 + 0.5 * k);
          dx.beginPath(); dx.moveTo(ps[s - 1].x, ps[s - 1].y); dx.lineTo(ps[s].x, ps[s].y); dx.stroke();
        });
        const o = width * 1.25;
        lx.strokeStyle = "#fff"; lx.lineCap = "round"; lx.globalAlpha = alpha * 0.2 * k; lx.lineWidth = width * 0.9;
        lx.beginPath(); lx.moveTo(ps[s - 1].x + up.x * o, ps[s - 1].y + up.y * o); lx.lineTo(ps[s].x + up.x * o, ps[s].y + up.y * o); lx.stroke();
      }
    };
    const shade = (c, rx, ry, alpha) => {
      if (alpha <= 0.01) return;
      dx.save(); dx.translate(c.x, c.y); dx.rotate(Math.atan2(ex.y, ex.x)); dx.scale(1, ry / rx);
      const gr = dx.createRadialGradient(0, 0, 0, 0, 0, rx);
      gr.addColorStop(0, dark); gr.addColorStop(1, "rgba(0,0,0,0)");
      dx.globalAlpha = alpha; dx.fillStyle = gr;
      dx.beginPath(); dx.arc(0, 0, rx, 0, Math.PI * 2); dx.fill(); dx.restore();
    };

    // Frente
    const browTop = avg([pts[105], pts[334]]), top = pts[10];
    const span = dist(pts[105], pts[334]) * 0.62;
    [0.28, 0.48, 0.68].forEach((v, k) => {
      const base = lerp(browTop, top, v), ps = [];
      for (let s = 0; s <= 16; s++) {
        const u = -span + (2 * span * s) / 16, qq = u / span;
        ps.push(at(base, u, -H * 0.028 * qq * qq + H * 0.006 * Math.sin(qq * 5 + k * 2.1)));
      }
      crease(ps, W * 0.0058, ramp(0.15, 0.7) * (0.36 - k * 0.07));
    });
    // Entrecejo
    [[pts[107], 1], [pts[336], -1]].forEach(([p, s]) => crease(q(at(p, s * W * 0.012, H * 0.0), at(p, s * W * 0.02, H * 0.05), at(p, s * W * 0.03, H * 0.1), 8), W * 0.0058, ramp(0.35, 0.85) * 0.45));
    // Patas de gallo
    [[pts[33], -1], [pts[263], 1]].forEach(([c, s]) => {
      [-0.45, -0.12, 0.22].forEach((ang, n) => {
        const a = at(c, s * W * 0.028, 0);
        const len = W * (0.055 + n * 0.007);
        const b = { x: a.x + (ex.x * s * Math.cos(ang) + up.x * Math.sin(ang)) * len, y: a.y + (ex.y * s * Math.cos(ang) + up.y * Math.sin(ang)) * len };
        crease(q(a, at(lerp(a, b, 0.5), 0, H * 0.006), b, 8), W * 0.0048, ramp(0.15, 0.6) * 0.5);
      });
    });
    // Ojeras, bolsas y párpado caído
    [[LOW_A, UP_A], [LOW_B, UP_B]].forEach(([low, upper]) => {
      const lid = low.map((i) => pts[i]);
      const eyeW = dist(lid[0], lid[lid.length - 1]);
      shade(at(avg(lid), 0, -H * 0.06), eyeW * 0.62, eyeW * 0.26, 0.2 * ramp(0.05, 0.7));
      crease(lid.map((p) => at(p, 0, -H * 0.05)), W * 0.0045, ramp(0.1, 0.55) * 0.42);
      crease(lid.slice(0, 7).map((p) => at(p, 0, -H * 0.095)), W * 0.0045, ramp(0.35, 0.85) * 0.32);
      crease(upper.map((i) => at(pts[i], 0, H * 0.028)), W * 0.0045, ramp(0.3, 0.85) * 0.32);
    });
    // Surcos nasogenianos
    [[129, 61, -1], [358, 291, 1]].forEach(([n, m, s]) => {
      const a = at(pts[n], s * W * 0.012, H * 0.02), b = at(pts[m], s * W * 0.03, -H * 0.06);
      crease(q(a, at(lerp(a, b, 0.5), s * W * 0.035, 0), b), W * 0.0085, 0.12 + 0.5 * ramp(0, 0.75));
      shade(at(lerp(a, b, 0.55), s * W * 0.03, 0), W * 0.06, W * 0.025, 0.08 * ramp(0.2, 0.9));
    });
    // Mejillas hundidas
    [[205, -1], [425, 1]].forEach(([c, s]) => shade(at(pts[c], s * W * 0.03, -H * 0.06), W * 0.09, W * 0.045, 0.12 * ramp(0.25, 0.95)));
    // Líneas de marioneta
    [[61, -1], [291, 1]].forEach(([m, s]) => {
      const a = at(pts[m], s * W * 0.006, -H * 0.02), b = at(pts[m], s * W * 0.022, -H * 0.15);
      crease(q(a, at(lerp(a, b, 0.5), s * W * 0.01, 0), b, 8), W * 0.0065, ramp(0.4, 0.95) * 0.45);
    });
    // Labio superior
    [37, 39, 267, 269].forEach((i) => crease([at(pts[i], 0, H * 0.008), at(pts[i], 0, H * 0.026), at(pts[i], 0, H * 0.045)], W * 0.0032, ramp(0.6, 1) * 0.35));
    // Cuello
    [0.24, 0.34].forEach((v, k) => {
      const c = pts[152];
      crease(q(at(c, -W * 0.2, -H * v), at(c, 0, -H * (v + 0.035)), at(c, W * 0.2, -H * v)), W * 0.0055, ramp(0.3, 0.85) * (0.32 - k * 0.08));
    });
    // Manchas
    const sp = ramp(0.45, 1);
    f.spots.forEach((s) => {
      if (sp <= 0 || s.k > sp + 0.1) return;
      const gr = dx.createRadialGradient(s.p.x, s.p.y, 0, s.p.x, s.p.y, s.s);
      gr.addColorStop(0, `rgb(${Math.round(f.skin[0] * 0.66)},${Math.round(f.skin[1] * 0.5)},${Math.round(f.skin[2] * 0.4)})`);
      gr.addColorStop(1, "rgba(0,0,0,0)");
      dx.globalAlpha = 0.3 * sp; dx.fillStyle = gr;
      dx.beginPath(); dx.arc(s.p.x, s.p.y, s.s, 0, Math.PI * 2); dx.fill();
    });

    maskLayer(darkL, f.skinM); maskLayer(lightL, f.skinM);
    ctx.save();
    ctx.globalCompositeOperation = "multiply"; ctx.drawImage(darkL, 0, 0);
    ctx.globalCompositeOperation = "screen"; ctx.drawImage(lightL, 0, 0);
    ctx.restore();
    return out;
  }
  function layer() {
    const c = document.createElement("canvas"); c.width = c.height = N; return c;
  }
  function maskLayer(c, m) {
    const x = c.getContext("2d", { willReadFrequently: true });
    const im = x.getImageData(0, 0, N, N), d = im.data;
    for (let j = 0, i = 3; j < N * N; j++, i += 4) if (d[i]) d[i] = d[i] * m[j];
    x.putImageData(im, 0, 0);
  }

  // Guarda el retrato recortado y su máscara de cabello en este navegador.
  function serialize(p) {
    const s = 160, c = document.createElement("canvas"); c.width = c.height = s;
    const x = c.getContext("2d"), im = x.createImageData(s, s);
    for (let y = 0; y < s; y++) for (let xx = 0; xx < s; xx++) {
      const v = Math.round((p.hair ? p.hair[Math.floor(y * N / s) * N + Math.floor(xx * N / s)] : 0) * 255);
      const i = (y * s + xx) * 4; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255;
    }
    x.putImageData(im, 0, 0);
    return { v: 2, img: p.canvas.toDataURL("image/jpeg", 0.86), hair: c.toDataURL("image/png"), pts: p.pts.map((q) => [Math.round(q.x * 10) / 10, Math.round(q.y * 10) / 10]) };
  }
  const loadImg = (src) => new Promise((res) => { const i = new Image(); i.onload = () => res(i); i.onerror = () => res(null); i.src = src; });
  async function deserialize(saved) {
    if (!saved || saved.v !== 2 || !saved.img || !Array.isArray(saved.pts) || saved.pts.length < 468) return null;
    const [img, hm] = await Promise.all([loadImg(saved.img), loadImg(saved.hair)]);
    if (!img) return null;
    const c = document.createElement("canvas"); c.width = c.height = N;
    c.getContext("2d").drawImage(img, 0, 0, N, N);
    const hair = new Float32Array(N * N);
    if (hm) {
      const h = document.createElement("canvas"); h.width = h.height = N;
      const hx = h.getContext("2d", { willReadFrequently: true }); hx.imageSmoothingEnabled = true; hx.drawImage(hm, 0, 0, N, N);
      const d = hx.getImageData(0, 0, N, N).data;
      for (let j = 0; j < N * N; j++) hair[j] = d[j * 4] / 255;
    }
    return { canvas: c, pts: saved.pts.map(([x, y]) => ({ x, y })), hair };
  }

  // Intensidad según tu edad de hoy y la edad a la que viajas.
  function amounts(nowAge, targetAge) {
    const t = FY.clamp((targetAge - nowAge) / 40, 0, 1) * FY.clamp(0.6 + (targetAge - 30) / 60, 0, 1);
    const gray = FY.clamp((targetAge - Math.max(nowAge, 30)) / 38, 0, 1);
    return { t, gray };
  }

  FY.aging = { load, fileToCanvas, detect, prepare, render, serialize, deserialize, amounts, N };
})(window.FY);
