// Vigía de marca: busca "Quincy" en MARCia (IMPI) y lista las marcas parecidas en las clases que importan.
// No cambia nada. Uso:  node quincy/scripts/agentes/vigia_marca.js [marca] [clases separadas por coma]
// Por defecto: Quincy en 9, 35, 36, 41 y 42. Imprime JSON con cada expediente parecido, su estatus y sus productos.
// Necesita Playwright (ya viene en el contenedor de Claude Code). MARCia a veces responde 500: se reintenta.
const { chromium } = require('playwright');

const MARCA = process.argv[2] || 'Quincy';
const CLASES = (process.argv[3] || '9,35,36,41,42').split(',');
const PARECIDO = new RegExp('QU?[IY]N[CSZ][IY]|' + MARCA.toUpperCase().replace(/[^A-Z]/g, ''), 'i');

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('https://marcia.impi.gob.mx/marcas/search/quick', { waitUntil: 'networkidle', timeout: 90000 });
  const req = (m, path, body) => p.evaluate(async ([m, path, body]) => {
    const t = document.querySelector('meta[name=_csrf]').content;
    const r = await fetch(path, { method: m, headers: { 'content-type': 'application/json', 'X-XSRF-TOKEN': t }, body: body ? JSON.stringify(body) : undefined });
    return [r.status, await r.text()];
  }, [m, path, body]);
  const retry = async (fn) => { for (let i = 0; i < 5; i++) { const [s, t] = await fn(); if (s === 200) return JSON.parse(t); await p.waitForTimeout(3000 * (i + 1)); } return null; };

  const rec = await retry(() => req('POST', '/marcas/search/internal/record', { _type: 'Search$Quick', images: [], query: MARCA }));
  if (!rec) { console.log(JSON.stringify({ error: 'MARCia no respondió; intenta más tarde' })); await b.close(); process.exit(2); }
  const out = { marca: MARCA, fecha: new Date().toISOString().slice(0, 10), total: rec.count, clases: {} };
  for (const c of CLASES) {
    const res = await retry(() => req('POST', '/marcas/search/internal/result', { searchId: rec.id, pageSize: 100, pageNumber: 0, statusFilter: [], viennaCodeFilter: [], niceClassFilter: [c] }));
    const hits = (res ? res.resultPage : []).filter((x) => PARECIDO.test(x.title || ''));
    out.clases[c] = [];
    for (const x of hits) {
      const v = await retry(() => req('GET', `/marcas/search/internal/view/${x.id}?s=${rec.id}&m=l&sort=&pageSize=100`));
      const det = v ? v.details : {};
      out.clases[c].push({
        expediente: x.applicationNumber, registro: x.registrationNumber || null, marca: x.title, estatus: x.status,
        titular: (x.owners || []).join(', '), fechas: x.dates,
        vence: det.generalInformation ? det.generalInformation.expiryDate || null : null,
        productos: (det.productsAndServices || []).map((ps) => `clase ${ps.classes}: ${ps.goodsAndServices}`).join(' | ').slice(0, 700),
        avisos: det.avisos || [],
        historial: ((v && v.historyData && v.historyData.historyRecords) || []).map((h) => `${h.description} ${h.startDate}`),
      });
    }
  }
  console.log(JSON.stringify(out, null, 1));
  await b.close();
})();
