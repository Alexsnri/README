// Posts de una imagen (1080×1350) para marketing/ig/. Uso: node posts.js [id…]
const { chromium } = require('playwright');
const path = require('path');
const OUT = process.env.OUT || path.join(__dirname, '..', '..', 'marketing', 'ig');
const CSS = `
html,body{margin:0;width:1080px;height:1350px;overflow:hidden}
body{background:radial-gradient(90% 60% at 80% 8%,#17475a 0%,#0b2230 50%,#05101a 100%);font-family:Figtree,sans-serif;color:#eaf3f4;position:relative}
.ring{position:absolute;right:-300px;top:-260px;width:1100px;height:1100px;border-radius:50%;border:2px solid rgba(90,214,200,.16)}
.ring.b{right:-200px;top:-160px;width:900px;height:900px;border-color:rgba(255,181,71,.14)}
.brand{position:absolute;left:90px;top:92px;display:flex;align-items:center;gap:16px;font:800 44px Unbounded;color:#fff}.brand i{width:42px;height:42px;border-radius:50%;background:radial-gradient(circle at 38% 34%,#ffd27a,#ffb547 55%,#d9672b);box-shadow:0 0 30px rgba(255,181,71,.5)}.brand b{color:#ffb547}
.wrap{position:absolute;left:90px;right:90px;top:200px;display:flex;flex-direction:column;gap:30px}
.kick{font:700 30px 'JetBrains Mono';letter-spacing:.16em;text-transform:uppercase;color:#5ad6c8}
.h1{font:800 76px/1.06 Unbounded;letter-spacing:-.02em;color:#eaf3f4}.h1 b{color:#ffb547}
.row{display:flex;justify-content:space-between;align-items:center;background:rgba(12,29,40,.85);border:3px solid #2c5468;border-radius:32px;padding:34px 40px}
.row .l{font:700 42px/1.2 Figtree;color:#fff}.row .l small{display:block;font:600 28px Figtree;color:#a9c0c8;margin-top:6px}
.row .v{font:800 64px Unbounded}
.t{font:500 32px/1.45 Figtree;color:#a9c0c8}
.foot{position:absolute;left:90px;right:90px;bottom:70px;display:flex;justify-content:space-between;align-items:center}
.foot span{font:600 32px Figtree;color:#5ad6c8}.btn{font:800 34px Figtree;color:#1a1206;background:#ffb547;border-radius:999px;padding:24px 34px}`;
const P = {
  // $10,000 un año. CETES 28 días 6.22% e inflación 3.45% (data/rates.json, Banxico oct 2026); ISR 0.90% del capital (LIF 2026).
  '13-aguinaldo-a-rendir': `<div class="kick">Aguinaldo a rendir</div>
    <div class="h1">$10,000 de aguinaldo, <b>un año después</b></div>
    <div class="row"><div class="l">En el colchón<small>la inflación le quita valor</small></div><div class="v" style="color:#ff8574">−$333</div></div>
    <div class="row"><div class="l">En CETES<small>ya con la retención de ISR</small></div><div class="v" style="color:#86e3a8">+$550</div></div>
    <div class="t">CETES a 28 días al 6.22% e inflación de 3.45% (Banxico, octubre de 2026). Las tasas cambian cada semana; no es una recomendación. Antes de invertir, paga tu tarjeta y aparta para emergencias.</div>`,
};
(async () => {
  const only = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  for (const [id, html] of Object.entries(P)) {
    if (only.length && !only.includes(id)) continue;
    await p.setContent(`<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@800&family=Figtree:wght@500;600;700;800&family=JetBrains+Mono:wght@700&display=swap"><style>${CSS}</style>
      <div class="ring"></div><div class="ring b"></div><div class="brand"><i></i><span>quincy<b>.</b></span></div>
      <div class="wrap">${html}</div><div class="foot"><span>Gratis · sin registro</span><div class="btn">Haz tu cuenta · link en bio</div></div>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
    const ov = await p.evaluate(() => document.querySelector('.wrap').getBoundingClientRect().bottom > 1220);
    if (ov) console.log('OVERFLOW', id);
    await p.screenshot({ path: `${OUT}/${id}.jpg`, type: 'jpeg', quality: 92 });
  }
  await b.close(); console.log('posts ok');
})();
