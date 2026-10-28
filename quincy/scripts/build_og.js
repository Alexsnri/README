// Genera las imágenes para vista previa en WhatsApp y redes (Open Graph, 1200×630) de cada página: quincy/img/og/<pagina>.jpg
// Uso: node quincy/scripts/build_og.js   (necesita Playwright, ya viene instalado). Corre de nuevo si cambias títulos o valores de ley.
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const font = (f) => "data:font/woff2;base64," + fs.readFileSync(path.join(ROOT, "fonts", f)).toString("base64");

// kicker · título (la pregunta que la gente hace) · dato grande · nota
const PAGES = {
  portada: ["Gratis y sin registro · 2026", "¿Cuánto te toca de <em>aguinaldo</em>?", "10 s", "Calcúlalo con la ley de 2026"],
  aguinaldo: ["Calculadora · Aguinaldo 2026", "¿Cuánto te toca de <em>aguinaldo</em>?", "15 días", "mínimo de ley · a más tardar el 19 de diciembre"],
  "aguinaldo-a-rendir": ["Calculadora · CETES, bancos y SOFIPOs", "¿Dónde pongo mi <em>aguinaldo</em> a rendir?", "CETES", "cuánto ganas de verdad, con ISR e inflación"],
  finiquito: ["Calculadora · Finiquito y liquidación 2026", "¿Cuánto te toca si <em>te vas</em>?", "3 meses", "de indemnización si te despiden sin causa"],
  vacaciones: ["Calculadora · Vacaciones dignas 2026", "¿Cuántos días de <em>vacaciones</em> te tocan?", "12 días", "desde tu primer año, más 25% de prima"],
  ptu: ["Calculadora · Reparto de utilidades", "¿Cuánto te toca de <em>PTU</em>?", "3 meses", "de salario es el tope, o tu promedio de 3 años"],
  tanda: ["Calculadora · Tandas", "¿Qué número de la <em>tanda</em> te conviene?", "Turno 1", "gana contra CETES; el último pierde"],
  quincena: ["Calculadora · Tu límite diario", "¿Cuánto puedes <em>gastar hoy</em>?", "$ / día", "para llegar completo a la quincena"],
};

const html = (k, t, n, s) => `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:U;src:url(${font("unbounded.woff2")})}
@font-face{font-family:F;src:url(${font("figtree.woff2")})}
@font-face{font-family:M;src:url(${font("jetbrains-mono.woff2")})}
*{margin:0;box-sizing:border-box}
body{width:1200px;height:630px;overflow:hidden;color:#eaf3f4;font-family:F;position:relative;
background:radial-gradient(60% 90% at 92% 0%,rgba(255,181,71,.38),rgba(255,181,71,0) 60%),radial-gradient(50% 70% at 0% 100%,rgba(90,214,200,.22),rgba(90,214,200,0) 65%),linear-gradient(140deg,#15404f,#0b1f2b 55%,#07121a)}
.rings{position:absolute;right:-160px;top:120px;width:760px;height:420px;transform:rotate(-12deg)}
.rings i{position:absolute;inset:0;border-radius:50%;border:2px solid rgba(255,181,71,.22)}
.rings i:nth-child(2){inset:50px 90px;border-color:rgba(90,214,200,.2)}
.rings i:nth-child(3){inset:100px 180px;border-color:rgba(255,181,71,.18)}
.logo{position:absolute;left:72px;top:60px;display:flex;align-items:center;gap:16px;font:800 40px U;letter-spacing:-1px}
.logo i{width:40px;height:40px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#ffd08a,#ffb547 45%,#e2702e 75%);box-shadow:0 0 30px rgba(255,181,71,.6)}
.logo b{color:#ffb547}
.k{position:absolute;left:72px;top:170px;font:600 22px M;letter-spacing:3px;text-transform:uppercase;color:#5ad6c8}
h1{position:absolute;left:72px;top:214px;width:740px;font:800 64px/1.02 U;letter-spacing:-2.5px}
h1 em{font-style:normal;color:#ffb547}
.stat{position:absolute;right:72px;bottom:66px;text-align:right;width:440px}
.stat b{display:block;white-space:nowrap;font:800 76px/1 U;color:#ffb547;letter-spacing:-2px;text-shadow:0 0 40px rgba(255,181,71,.4)}
.stat span{display:block;margin-top:10px;font:600 22px/1.3 F;color:#b9ced4}
.foot{position:absolute;left:72px;bottom:66px;font:700 24px F;color:#eaf3f4;background:rgba(7,18,26,.6);border:2px solid rgba(255,181,71,.5);padding:14px 24px;border-radius:999px}
</style></head><body><div class="rings"><i></i><i></i><i></i></div>
<div class="logo"><i></i><span>quincy<b>.</b></span></div><p class="k">${k}</p><h1>${t}</h1>
<div class="stat"><b>${n}</b><span>${s}</span></div><p class="foot">Gratis · sin registro</p></body></html>`;

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1200, height: 630 } });
  for (const [slug, v] of Object.entries(PAGES)) {
    await pg.setContent(html(...v)); await pg.evaluate(() => document.fonts.ready);
    const out = path.join(ROOT, "img", "og", slug + ".jpg");
    await pg.screenshot({ path: out, type: "jpeg", quality: 86 });
    console.log("ok", slug, Math.round(fs.statSync(out).size / 1024) + " KB");
  }
  await b.close();
})();
