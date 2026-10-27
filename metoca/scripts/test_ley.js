const L = require(require('path').join(__dirname, '..', 'js', 'ley.js'));
const { ley, LEY } = L;
const d = (s) => { const [y, m, dd] = s.split('-').map(Number); return new Date(y, m - 1, dd); };
let fail = 0;
const eq = (name, got, want, tol = 0.01) => { const ok = Math.abs(got - want) <= tol; if (!ok) fail++; console.log((ok ? 'ok  ' : 'FAIL') + ' ' + name + ': ' + (typeof got === 'number' ? got.toFixed(2) : got) + ' (esperado ' + want + ')'); };
// Vacaciones art. 76
[[1,12],[2,14],[3,16],[4,18],[5,20],[6,22],[10,22],[11,24],[15,24],[16,26],[21,28],[26,30],[31,32]].forEach(([y,v]) => eq('vacaciones año ' + y, ley.vacationDays(y), v, 0));
// Años cumplidos
eq('años 2020-03-15 → 2026-03-14', ley.completedYears(d('2020-03-15'), d('2026-03-14')), 5, 0);
eq('años 2020-03-15 → 2026-03-15', ley.completedYears(d('2020-03-15'), d('2026-03-15')), 6, 0);
eq('años bisiesto 2024-02-29 → 2025-02-28', ley.completedYears(d('2024-02-29'), d('2025-02-28')), 1, 0);
// Aguinaldo: $15,000 al mes → sd 500 → 15 días = 7,500 año completo
const sd = ley.dailyFromMonthly(15000);
eq('sd', sd, 500);
eq('aguinaldo año completo', ley.aguinaldo({ sd, start: d('2020-01-10'), at: d('2026-10-27') }).amount, 7500);
// Entró el 1 de julio de 2026: 184 días de 365
eq('aguinaldo proporcional (1 jul)', ley.aguinaldo({ sd, start: d('2026-07-01'), at: d('2026-10-27') }).amount, 7500 * 184 / 365);
eq('aguinaldo exento 30 UMA', ley.aguinaldo({ sd, start: d('2020-01-10'), at: d('2026-10-27') }).exento, 30 * 117.31);
// Vacaciones con 3 años cumplidos: 16 días, prima 25% = 16*500*.25 = 2000
const v = ley.vacaciones({ sd, start: d('2023-05-02'), at: d('2026-10-27') });
eq('vac años', v.years, 3, 0); eq('vac días', v.days, 16, 0); eq('prima vac', v.prima, 2000); eq('próximos días', v.nextDays, 18, 0);
// PTU tope 3 meses = 90 * 500
const p = ley.ptu({ sd, at: d('2026-10-27') });
eq('ptu tope', p.tope, 45000); eq('ptu fecha año siguiente', p.empresas.getFullYear(), 2027, 0);
// Renuncia con 2 años, sin pendientes: aguinaldo prop + vacaciones prop del 3er año
const r = ley.salida({ sd, start: d('2024-06-01'), end: d('2026-06-30'), motivo: 'renuncia' });
const agDays = 181; // 1 ene → 30 jun 2026
eq('renuncia aguinaldo', r.lines.find(l => l.key === 'aguinaldo').amount, 500 * 15 * agDays / 365);
eq('renuncia vacaciones (16 días * 29/365)', r.lines.find(l => l.key === 'vacaciones').amount, 16 * 29 / 365 * 500);
eq('renuncia sin prima antigüedad (<15 años)', r.lines.some(l => l.key === 'antiguedad') ? 1 : 0, 0, 0);
eq('renuncia sin liquidación', r.liquidacion, 0);
// Despido: 3 meses con SDI; prima de antigüedad topada a 2 SM (630.08) → sd 500 no se topa
const k = ley.salida({ sd, start: d('2021-10-27'), end: d('2026-10-27'), motivo: 'despido' });
const sdiExp = 500 * (1 + (15 + 22 * 0.25) / 365); // año 6 en curso → 22 días
eq('sdi', k.sdi, sdiExp); eq('3 meses', k.liquidacion, 90 * sdiExp);
eq('prima antigüedad 5 años', k.lines.find(l => l.key === 'antiguedad').amount, 12 * 500 * (1826 / 365));
// Sueldo alto se topa: $60,000/mes → sd 2000, tope 2*315.04
const hi = ley.salida({ sd: 2000, start: d('2016-10-27'), end: d('2026-10-27'), motivo: 'despido' });
eq('antigüedad topada', hi.lines.find(l => l.key === 'antiguedad').amount, 12 * 630.08 * (3652 / 365));
const fr = ley.salida({ sd: 2000, start: d('2016-10-27'), end: d('2026-10-27'), motivo: 'despido', zona: 'frontera' });
eq('antigüedad topada frontera', fr.lines.find(l => l.key === 'antiguedad').amount, 12 * 881.74 * (3652 / 365));
console.log(fail ? `\n${fail} FALLAS` : '\nTodas las pruebas pasan');
process.exit(fail ? 1 : 0);
