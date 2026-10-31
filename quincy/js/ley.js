// Quincy · lo que la ley te da. Cálculos puros con la Ley Federal del Trabajo (LFT) y valores de 2026.
// Actualiza LEY cada año: salario mínimo (CONASAMI, 1 de enero) y UMA (INEGI, 1 de febrero).
(function (root) {
  const LEY = {
    year: 2026,
    sm: { general: 315.04, frontera: 440.87 }, // salario mínimo diario 2026, CONASAMI
    uma: 117.31,                              // UMA diaria 2026, INEGI (vigente desde el 1 de febrero de 2026)
    aguinaldoDias: 15,                        // art. 87 LFT: mínimo 15 días
    primaVacacional: 0.25,                    // art. 80 LFT: mínimo 25%
    exentoAguinaldoUMA: 30,                   // art. 93 fr. XIV LISR
    exentoPrimaUMA: 15,                       // art. 93 fr. XIV LISR (prima vacacional y PTU)
    antiguedadDias: 12,                       // art. 162 LFT
    antiguedadTopeSM: 2,                      // arts. 162 y 486 LFT: tope de 2 salarios mínimos
    indemnizacionDias: 90,                    // art. 48 LFT: 3 meses
    veinteDias: 20                            // art. 50 fr. II LFT: cuando aplica
  };

  const DAY = 864e5;
  const atNoon = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate(), 12);
  const diffDays = (a, b) => Math.round((atNoon(b) - atNoon(a)) / DAY);
  const addYears = (d, n) => {
    const x = new Date(d.getFullYear() + n, d.getMonth(), d.getDate(), 12);
    if (x.getMonth() !== d.getMonth()) x.setDate(0); // 29 de febrero → 28
    return x;
  };
  function completedYears(start, at) {
    let n = at.getFullYear() - start.getFullYear();
    if (atNoon(addYears(start, n)) > atNoon(at)) n--;
    return Math.max(0, n);
  }
  // Art. 76 LFT (reforma "vacaciones dignas", 2023): 12, 14, 16, 18, 20 y luego +2 cada 5 años.
  function vacationDays(yearOfService) {
    const n = Math.floor(yearOfService);
    if (n <= 0) return 0;
    if (n <= 5) return 10 + 2 * n;
    return 22 + 2 * Math.floor((n - 6) / 5);
  }
  const dailyFromMonthly = (monthly) => monthly / 30;

  // Aguinaldo del año de `at`: proporcional si entraste ese año. Se paga antes del 20 de diciembre.
  function aguinaldo({ sd, start, at, dias = LEY.aguinaldoDias }) {
    const y = at.getFullYear();
    const from = start > new Date(y, 0, 1) ? start : new Date(y, 0, 1);
    const yearLen = diffDays(new Date(y, 0, 1), new Date(y + 1, 0, 1));
    const days = Math.max(0, Math.min(yearLen, diffDays(from, new Date(y, 11, 31)) + 1));
    const amount = sd * dias * days / yearLen;
    const exento = LEY.exentoAguinaldoUMA * LEY.uma;
    return { amount, days, yearLen, exento, gravado: Math.max(0, amount - exento), deadline: new Date(y, 11, 19), full: days === yearLen };
  }

  // Vacaciones del año de servicio que ya cumpliste y lo que viene en tu próximo aniversario.
  function vacaciones({ sd, start, at, prima = LEY.primaVacacional }) {
    const n = completedYears(start, at);
    const days = vacationDays(n);
    const next = addYears(start, n + 1);
    return { years: n, days, prima: days * sd * prima, pay: days * sd, nextDate: next, nextDays: vacationDays(n + 1), daysToNext: diffDays(at, next), exentoPrima: LEY.exentoPrimaUMA * LEY.uma };
  }

  // Tope de PTU (art. 127 fr. VIII): 3 meses de salario o el promedio de los últimos 3 años, lo que te convenga más.
  function ptu({ sd, at, promedio = 0 }) {
    const y = at.getFullYear();
    let empresas = new Date(y, 4, 30), personas = new Date(y, 5, 29);
    if (atNoon(at) > atNoon(personas)) { empresas = new Date(y + 1, 4, 30); personas = new Date(y + 1, 5, 29); }
    return { tope: Math.max(sd * 90, promedio), tresMeses: sd * 90, empresas, personas, exento: LEY.exentoPrimaUMA * LEY.uma };
  }

  // Salario diario integrado mínimo (art. 84): incluye aguinaldo y prima vacacional.
  function sdi({ sd, years, dias = LEY.aguinaldoDias, prima = LEY.primaVacacional }) {
    return sd * (1 + (dias + vacationDays(Math.max(1, years + 1)) * prima) / 365);
  }

  // Finiquito (siempre) y liquidación (si te despiden sin causa justificada).
  function salida({ sd, start, end, motivo = "renuncia", zona = "general", dias = LEY.aguinaldoDias, prima = LEY.primaVacacional, vacPendientes = 0, diasSinPago = 0 }) {
    const n = completedYears(start, end);
    const exactYears = Math.max(0, diffDays(start, end) / 365);
    const y = end.getFullYear();
    const agFrom = start > new Date(y, 0, 1) ? start : new Date(y, 0, 1);
    const yearLen = diffDays(new Date(y, 0, 1), new Date(y + 1, 0, 1));
    const agDays = Math.max(0, diffDays(agFrom, end) + 1);
    const lastAnniv = n > 0 ? addYears(start, n) : start;
    const sinceAnniv = Math.max(0, diffDays(lastAnniv, end));
    const vacProp = vacationDays(n + 1) * sinceAnniv / 365 + vacPendientes;
    const lines = [];
    const add = (key, label, amount, note) => lines.push({ key, label, amount, note });
    add("salario", "Días trabajados sin pagar", diasSinPago * sd, `${diasSinPago} días`);
    add("aguinaldo", "Aguinaldo proporcional", sd * dias * agDays / yearLen, `${agDays} días trabajados este año`);
    add("vacaciones", "Vacaciones no disfrutadas", vacProp * sd, `${vacProp.toFixed(1)} días`);
    add("prima", "Prima vacacional", vacProp * sd * prima, `${Math.round(prima * 100)}% de tus vacaciones`);
    const despido = motivo === "despido";
    const topeSM = LEY.antiguedadTopeSM * (LEY.sm[zona] || LEY.sm.general);
    const baseAnt = Math.min(sd, topeSM);
    if (despido || n >= 15) add("antiguedad", "Prima de antigüedad", LEY.antiguedadDias * baseAnt * exactYears, `12 días por año, con salario tope de ${topeSM.toFixed(2)} al día`);
    const finiquito = lines.reduce((s, l) => s + l.amount, 0);
    const integ = sdi({ sd, years: n, dias, prima });
    let liquidacion = 0, veinte = 0;
    if (despido) {
      liquidacion = LEY.indemnizacionDias * integ;
      add("tresmeses", "Indemnización de 3 meses", liquidacion, "Art. 48, con salario integrado");
      veinte = LEY.veinteDias * integ * exactYears;
    }
    return { lines, finiquito, liquidacion, veinte, total: finiquito + liquidacion, years: n, exactYears, sdi: integ, despido };
  }

  root.LEY = LEY;
  root.ley = { diffDays, addYears, completedYears, vacationDays, dailyFromMonthly, aguinaldo, vacaciones, ptu, sdi, salida };
})(typeof window !== "undefined" ? (window.FY = window.FY || {}) : module.exports);
