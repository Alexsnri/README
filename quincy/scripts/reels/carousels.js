const { chromium } = require('playwright');
const fs = require('fs');
const OUT = process.env.OUT || require('path').join(__dirname, '..', '..', 'marketing', 'carruseles');
const CSS = `
:root{--night:#07121a;--deep:#0c1d28;--line:#2c5468;--fg:#eaf3f4;--mut:#a9c0c8;--sun:#ffb547;--tide:#5ad6c8;--ok:#86e3a8;--bad:#ff8574}
html,body{margin:0;width:1080px;height:1350px;overflow:hidden}
body{background:radial-gradient(110% 80% at 25% 15%,#16465a 0%,#0b2230 45%,#05101a 100%);font-family:Figtree,sans-serif;color:var(--fg);position:relative}
.orbit{position:absolute;right:-260px;bottom:-200px;width:1000px;height:360px;border:4px solid rgba(255,181,71,.18);border-radius:50%;transform:rotate(-18deg)}
.orbit.b{right:-180px;bottom:-120px;width:820px;height:280px;border-color:rgba(90,214,200,.18)}
.wrap{position:absolute;inset:90px 84px 110px;display:flex;flex-direction:column;gap:36px;justify-content:center}
.top{position:absolute;left:84px;right:84px;top:64px;display:flex;justify-content:space-between;align-items:center}
.brand{display:flex;align-items:center;gap:14px;font:800 38px Unbounded;color:#fff}.brand i{width:40px;height:40px;border-radius:50%;background:radial-gradient(circle at 38% 34%,#ffd27a,#ffb547 55%,#d9672b)}.brand b{color:var(--sun)}
.pg{font:700 28px 'JetBrains Mono';color:var(--mut)}
.chip{align-self:flex-start;font:700 30px/1 'JetBrains Mono';letter-spacing:.14em;text-transform:uppercase;color:var(--night);background:var(--tide);padding:14px 20px;border-radius:12px}
.chip.sun{background:var(--sun)}
.h1{font:800 96px/1.04 Unbounded;letter-spacing:-.02em;color:#fff}.h2{font:800 70px/1.08 Unbounded;color:#fff}.h3{font:800 54px/1.15 Unbounded;color:#fff}
.h1 b,.h2 b,.h3 b{color:var(--sun)}
.n{font:800 140px/1 Unbounded;color:var(--sun)}
.t{font:600 42px/1.35 Figtree;color:var(--mut)}.t b{color:#fff}
.small{font:600 30px/1.4 Figtree;color:var(--mut)}
.card{background:rgba(12,29,40,.88);border:3px solid var(--line);border-radius:36px;padding:38px 44px;display:flex;flex-direction:column;gap:18px}
.eq{display:flex;justify-content:space-between;font:700 46px/1.2 Figtree;color:#fff}.eq span:last-child{font-family:'JetBrains Mono';color:var(--tide)}
.eq.hi span:last-child{color:var(--sun)}
.li{display:flex;gap:22px;align-items:flex-start;font:700 44px/1.25 Figtree;color:#fff}.li i{flex:none;width:60px;height:60px;border-radius:50%;background:var(--ok);display:grid;place-items:center;font:800 34px Figtree;color:var(--night);font-style:normal;margin-top:2px}
.li.x i{background:var(--bad)}
.swipe{position:absolute;right:84px;bottom:70px;font:800 36px Figtree;color:var(--night);background:var(--sun);border-radius:999px;padding:20px 34px}
.foot{position:absolute;left:84px;bottom:76px;font:600 28px Figtree;color:var(--mut)}
.btn{align-self:flex-start;font:800 46px Figtree;color:#1a1206;background:var(--sun);border-radius:999px;padding:30px 50px}`;
const chart = () => { const V = [115, 89, 64, 38, 12, -13, -38, -64, -89, -114]; return `<div style="position:relative;height:520px;display:grid;grid-template-columns:repeat(10,1fr);gap:14px">
  <div style="position:absolute;left:0;right:0;top:250px;height:4px;background:#2c5468"></div>${V.map((v, i) => `<div style="position:relative"><div style="position:absolute;left:0;right:0;${v > 0 ? 'bottom:270px' : 'top:254px'};height:${Math.abs(v) / 115 * 220}px;border-radius:10px;background:${v > 0 ? '#86e3a8' : '#ff8574'}"></div><div style="position:absolute;left:-8px;right:-8px;top:490px;text-align:center;font:700 28px JetBrains Mono;color:#a9c0c8">${i + 1}</div></div>`).join('')}</div>`; };
const C = {
  'c1-aguinaldo': [
    `<span class="chip">Aguinaldo 2026</span><div class="h1"><b>5 cosas</b> que tienes que saber de tu aguinaldo</div><div class="t">Guárdalo para diciembre.</div>`,
    `<span class="chip sun">1</span><div class="h2">Son mínimo <b>15 días</b> de salario</div><div class="card"><div class="eq"><span>Salario mínimo</span><span>$4,726</span></div><div class="eq"><span>$12,000 al mes</span><span>$6,000</span></div><div class="eq hi"><span>$15,000 al mes</span><span>$7,500</span></div><div class="eq"><span>$20,000 al mes</span><span>$10,000</span></div></div><div class="small">Art. 87 de la Ley Federal del Trabajo.</div>`,
    `<span class="chip sun">2</span><div class="h2">Te lo pagan <b>antes del 20 de diciembre</b></div><div class="t">O sea, a más tardar el <b>19 de diciembre</b>. Si no llega, PROFEDET te asesora gratis.</div>`,
    `<span class="chip sun">3</span><div class="h2">¿Entraste este año? Te toca <b>la parte proporcional</b></div><div class="card"><div class="eq"><span>Fórmula</span><span>15 × días ÷ 365</span></div><div class="eq hi"><span>7 meses trabajados</span><span>8.75 días</span></div></div>`,
    `<span class="chip sun">4</span><div class="h2">Hasta <b>$3,519.30</b> no paga ISR</div><div class="t">Son 30 veces la UMA de 2026 ($117.31). Solo lo que pase de esa cantidad paga impuesto.</div>`,
    `<span class="chip sun">5</span><div class="h2">Si renuncias o te despiden, <b>también te toca</b></div><div class="t">Va dentro de tu finiquito, proporcional a lo que trabajaste.</div><div class="btn">Calcula el tuyo · link en bio</div><div class="small">Mándaselo a quien todavía no sabe cuánto le toca.</div>`,
  ],
  'c2-tanda': [
    `<span class="chip">Tandas</span><div class="h1">¿Qué número de la tanda <b>te conviene</b>?</div><div class="t">Hicimos la cuenta.</div>`,
    `<div class="h2">Así funciona</div><div class="card"><div class="eq"><span>Personas</span><span>10</span></div><div class="eq"><span>Cada quien pone</span><span>$1,000</span></div><div class="eq"><span>Cada</span><span>quincena</span></div><div class="eq hi"><span>Cada turno recibe</span><span>$10,000</span></div></div>`,
    `<div class="h3">Ganancia o pérdida de cada número frente a <b>CETES</b></div>${chart()}<div class="small">Comparado con invertir cada aportación en CETES al 6.23% anual.</div>`,
    `<div class="h2" style="color:#86e3a8">Los primeros</div><div class="t">Reciben un <b>préstamo sin intereses</b>. Te conviene si tienes una deuda cara o una urgencia.</div><div class="h2" style="color:#ff8574">Los últimos</div><div class="t">Ahorran <b>sin rendimiento</b>. Te conviene si te cuesta trabajo ahorrar.</div>`,
    `<div class="h2">Una tanda depende de la <b>confianza</b></div><div class="t">Si alguien deja de pagar, nadie lo cubre. Arma tu tanda con gente que conoces.</div>`,
    `<div class="h2">Sortea los turnos <b>con ruleta</b></div><div class="t">Y manda el calendario al grupo de WhatsApp. Gratis, sin que nadie maneje el dinero.</div><div class="btn">Arma la tuya · link en bio</div><div class="small">Etiqueta a quien organiza tu tanda.</div>`,
  ],
  'c3-finiquito-liquidacion': [
    `<span class="chip">Derechos laborales</span><div class="h1">¿Finiquito o liquidación? <b>No es lo mismo</b></div><div class="t">Guárdalo por si acaso.</div>`,
    `<span class="chip sun">Finiquito</span><div class="h2">Te toca <b>siempre</b></div><div class="t">Renuncies o te despidan:</div><div class="li"><i>✓</i>Días trabajados no pagados</div><div class="li"><i>✓</i>Aguinaldo proporcional</div><div class="li"><i>✓</i>Vacaciones no tomadas</div><div class="li"><i>✓</i>Prima vacacional</div>`,
    `<span class="chip sun">Liquidación</span><div class="h2">Solo si te despiden <b>sin causa</b></div><div class="li"><i>✓</i>3 meses de salario integrado</div><div class="li"><i>✓</i>12 días por año de prima de antigüedad</div><div class="li"><i>✓</i>Tu finiquito completo</div><div class="small">En algunos casos también 20 días por año (art. 50).</div>`,
    `<div class="n">2 meses</div><div class="h2">para reclamar un <b>despido</b></div><div class="t">Después pierdes el derecho (art. 518 LFT).</div>`,
    `<div class="li x"><i>✕</i>No firmes una renuncia que no escribiste</div><div class="li x"><i>✕</i>No firmes papeles en blanco</div><div class="li"><i>✓</i>PROFEDET te asesora gratis</div>`,
    `<div class="h2">Calcula tu finiquito o tu liquidación <b>en 1 minuto</b></div><div class="btn">Gratis · link en bio</div><div class="small">Mándaselo a quien lo necesite.</div>`,
  ],
  'c4-aguinaldo-wrapped': [
    `<span class="chip">Tu Aguinaldo Wrapped</span><div class="h1">Tu aguinaldo también tiene <b>su Wrapped</b></div><div class="t">Así se ve con un sueldo de <b>$12,000</b> al mes.</div>`,
    `<div class="card" style="gap:26px;padding:56px 54px"><span class="chip">Tu aguinaldo 2026</span><div class="n">$6,000</div><div class="t">15 días de salario, <b>por ley.</b></div><div class="small">Artículo 87 de la Ley Federal del Trabajo.</div></div>`,
    `<div class="card" style="gap:26px;padding:56px 54px;background:#5ad6c8;border-color:#5ad6c8"><span class="chip" style="background:#07121a;color:#5ad6c8">Cuenta regresiva</span><div class="n" style="color:#07121a">41</div><div class="h3" style="color:#07121a">días para cobrarlo</div><div class="small" style="color:#0c1d28">Contados desde el 8 de noviembre. Fecha límite: 19 de diciembre.</div></div>`,
    `<div class="card" style="gap:26px;padding:56px 54px"><span class="chip">Libre de ISR</span><div class="n" style="font-size:118px">$3,519.30</div><div class="t">Solo sobre <b>$2,480.70</b> te retienen ISR.</div><div class="small">Exento hasta 30 UMA (UMA 2026: $117.31).</div></div>`,
    `<div class="card" style="gap:26px;padding:56px 54px;background:#ffb547;border-color:#ffb547"><span class="chip" style="background:#07121a;color:#ffb547">Si lo pones en CETES un año</span><div class="n" style="color:#1a1206">+$373</div><div class="h3" style="color:#1a1206">antes de impuestos</div><div class="small" style="color:#3a2a10">CETES a 28 días al 6.22% anual (Banxico, octubre de 2026), si la tasa se mantiene.</div></div>`,
    `<div class="h1">¿Y <b>tú</b>?</div><div class="h3">Haz tu Wrapped en 10 segundos y súbelo a tus historias</div><div class="btn">Tu Wrapped · link en bio</div><div class="small">Gratis y sin registro. Mándaselo a quien todavía no sabe cuánto le toca.</div>`,
  ],
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  const only = process.argv.slice(2);
  for (const [id, slides] of Object.entries(C)) {
    if (only.length && !only.includes(id)) continue;
    fs.mkdirSync(`${OUT}/${id}`, { recursive: true });
    for (let i = 0; i < slides.length; i++) {
      const first = i === 0, last = i === slides.length - 1;
      await p.setContent(`<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@800&family=Figtree:wght@600;700;800&family=JetBrains+Mono:wght@700&display=swap"><style>${CSS}</style>
        <div class="orbit"></div><div class="orbit b"></div>
        <div class="top"><div class="brand"><i></i><span>quincy<b>.</b></span></div><div class="pg">${i + 1}/${slides.length}</div></div>
        <div class="wrap">${slides[i]}</div>${first ? '<div class="swipe">Desliza →</div>' : last ? '' : '<div class="foot">Gratis y sin registro</div><div class="swipe" style="background:transparent;color:#a9c0c8;border:3px solid #2c5468">→</div>'}`);
      await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
      const ov = await p.evaluate(() => { const w = document.querySelector('.wrap'); return w.scrollHeight > w.clientHeight + 2 || [...w.querySelectorAll('*')].some((e) => e.getBoundingClientRect().right > 1000); });
      await p.screenshot({ path: `${OUT}/${id}/${String(i + 1).padStart(2, '0')}.jpg`, type: 'jpeg', quality: 92 });
      if (ov) console.log('OVERFLOW', id, i + 1);
    }
  }
  await b.close(); console.log('carousels ok');
})();
