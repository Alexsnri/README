# 02 — Instrumentos y horarios para scalping en Capital.com (cuenta demo de $100, CDMX)

Fecha del análisis: 2026-11-05. Las afirmaciones sin fuente directa o inferidas llevan la marca **(NO VERIFICADO)**.
Datos y scripts: `/tmp/claude-0/-home-user-README/82cdbbb4-ddee-5e71-af10-eeafa19fca7d/scratchpad/scripts/` (`hourly_vol.py`, `daily_calib.py`, `ratio_table.py`, `weekend_gaps.py`, `capital_pages.py` y sus `*_output.txt`).

---

## 1. Husos horarios: lo que el bot debe codificar

- **CDMX está fija en UTC−6 todo el año.** La Ley de los Husos Horarios (DOF, 28-oct-2022, vigente desde el 30-oct-2022) eliminó el horario de verano. Solo lo conservan algunos municipios de la frontera norte ([Expansión](https://politica.expansion.mx/congreso/2022/10/26/senado-aprueba-eliminacion-del-horario-de-verano), [Bloomberg Línea](https://www.bloomberglinea.com/2022/10/29/cambio-de-horario-el-domingo-30-de-octubre-mexico-dice-adios-al-horario-de-verano-tras-26-anos/)).
- **EE. UU.:** el horario de verano (EDT, UTC−4) corrió del 8-mar-2026 al **1-nov-2026**. Ahora rige EST (UTC−5) hasta el 14-mar-2027 (segundo domingo de marzo). **Reino Unido/UE:** el verano terminó el 25-oct-2026 y vuelve el 28-mar-2027. (Fechas calculadas con las reglas vigentes de EE. UU. y la UE.)
- Consecuencia: **Nueva York = CDMX + 1 h en invierno (nov–mar) y CDMX + 2 h en verano (mar–nov).** Todo lo que depende de EE. UU. o de Europa ocurre **una hora antes en CDMX** durante el verano. Lo que depende de Asia (Tokio, China) no se mueve en CDMX, porque ni Asia ni México cambian de horario.

| Evento (hora local) | UTC invierno | **CDMX invierno (desde 1-nov-2026)** | CDMX verano (8-mar a 1-nov) |
|---|---|---|---|
| Apertura de Tokio 09:00 JST | 00:00 | 18:00 | 18:00 |
| Apertura de Shanghái/HK 09:30 | 01:30 | 19:30 | 19:30 |
| Apertura de Xetra/Londres 08:00 GMT (09:00 CET) | 08:00 | 02:00 | 01:00 |
| Datos de EE. UU. 08:30 ET (CPI, NFP, PPI, ventas minoristas, solicitudes de desempleo) | 13:30 | **07:30** | 06:30 |
| **Apertura del contado de EE. UU. 09:30 ET** | 14:30 | **08:30** | 07:30 |
| ISM, confianza del consumidor 10:00 ET | 15:00 | 09:00 | 08:00 |
| Fixing PM de oro LBMA 15:00 Londres | 15:00 | 09:00 | 08:00 |
| Cierre de Londres ~16:30 | 16:30 | 10:30 | 09:30 |
| FOMC 14:00 ET (conferencia 14:30) | 19:00 | **13:00** (13:30) | 12:00 |
| Cierre del contado de EE. UU. 16:00 ET | 21:00 | 15:00 | 14:00 |
| Cierre/rollover 17:00 ET | 22:00 | **16:00** | 15:00 |

Respuesta a la pregunta: la apertura del contado es a las **08:30 CDMX desde el 1-nov-2026 hasta el 13-mar-2027** y a las **07:30 CDMX entre marzo y noviembre**. Entre el 8 y el 28 de marzo, y entre el 25-oct y el 1-nov, Londres y NY quedan a solo 4 h de distancia. El bot debe calcular estas horas con `zoneinfo` (`America/New_York`, `Europe/London`, `America/Mexico_City`) y nunca dejarlas fijas.

---

## 2. Horarios de Capital.com (oficiales, en UTC)

Extraje el campo `openHours` del HTML de cada página de mercado de capital.com/en-int, descargadas el 2026-11-05 ~04:45 UTC, es decir, en horario de invierno (script `capital_pages.py`). Fuentes: [EUR/USD](https://capital.com/en-int/markets/forex/euro-us-dollar-rate-2), [GBP/USD](https://capital.com/en-int/markets/forex/british-pound-us-dollar-rate-2), [Gold](https://capital.com/en-int/markets/commodities/gold-spot-commodity), [US100](https://capital.com/en-int/markets/indices/us-tech-100-index-1), [US500](https://capital.com/en-int/markets/indices/us-500-index-1), [BTC/USD](https://capital.com/en-int/markets/cryptocurrencies/bitcoin-to-us-dollar-chart), [ETH/USD](https://capital.com/en-int/markets/cryptocurrencies/ethereum-to-us-dollar-chart).

| Instrumento | Pausa diaria (UTC) | **Pausa diaria (CDMX)** | Apertura semanal | Cierre semanal |
|---|---|---|---|---|
| EUR/USD, GBP/USD | 21:59:50–22:05 | **15:59:50–16:05** | Dom 22:00 UTC = **Dom 16:00 CDMX** | Vie 21:59:50 UTC = **Vie 15:59 CDMX** |
| GOLD (spot) | 21:59–23:00 (1 h) | **15:59–17:00** | Dom 23:00 UTC = Dom 17:00 CDMX | Vie 21:59 UTC = Vie 15:59 CDMX |
| US100, US500 (CFD 24/5) | 22:00–22:05 | **16:00–16:05** | Dom 23:00 UTC = Dom 17:00 CDMX | Vie 22:00 UTC = Vie 16:00 CDMX |
| BTC/USD, ETH/USD | 21:00–21:05 (lun–sáb); dom 22:00–22:05 | **15:00–15:05** (dom 16:00–16:05) | **24/7** | Mantenimiento sáb 05:00–07:00 UTC = **vie 23:00 – sáb 01:00 CDMX** |

- El **cargo de financiamiento nocturno (overnight funding)** se aplica a las **22:00 UTC = 16:00 CDMX** en los siete instrumentos. Los cargos diarios publicados para largos y cortos (sobre el valor total de la posición) son: BTC/ETH −0.0616 % / +0.0137 %, GOLD −0.0154 % / +0.0072 %, US100/US500 −0.0225 % / +0.0002 %, EUR/USD −0.0080 % / −0.0002 %, GBP/USD −0.0041 % / −0.0042 %. El crypto largo cuesta ~22 % anualizado: el bot nunca debe mantener crypto a las 16:00 CDMX.
- Capital.com dice que el trading 24 h es "Sunday night to Friday night (UTC), with brief market pauses for maintenance" y que los índices 24/5 tienen "lower liquidity… wider spreads" fuera de horario ([24h trading](https://capital.com/en-int/ways-to-trade/24h-trading)).
- **En verano probablemente todo se recorre 1 h antes en UTC** (pausa a las 21:00 UTC, que también sería las 15:00 CDMX) **(NO VERIFICADO)**. Un resultado de búsqueda citaba "closes Friday 21:00 UTC / fee 21:00 UTC" en la página de BTC, posiblemente capturado en verano. **Recomendación firme:** que el bot lea `openingHours` (`{"mon":["00:00 - 21:59","23:05 - 00:00"],…,"zone":"UTC"}`) y `marketStatus` de `GET /api/v1/markets/{epic}` cada día en lugar de fijar horarios en el código ([Capital.com API](https://open-api.capital.com/)). Límites de la API: 10 solicitudes/s y 1 orden cada 0.1 s. Demo: `https://demo-api-capital.backend-capital.com/`.

---

## 3. Spreads publicados en Capital.com

Los tomé de las mismas páginas, con bid/ask del 2026-11-05 ~04:45 UTC (22:45 CDMX, sesión asiática):

| Instrumento | Spread (pts) | Precio | **Spread en bps** | Tamaño mínimo | Margen (en-int) |
|---|---|---|---|---|---|
| BTC/USD | 50 | 80 312 | **6.23** | 0.0001 BTC (~$8) | 5 % |
| ETH/USD | 1.75 | 2 417 | **7.24** | 0.001 ETH (~$2.4) | 5 % |
| GOLD | 0.50 | 4 134 | **1.21** | 0.01 oz (~$41) | 1 % |
| US100 | 1.8 | 28 223 | **0.64** | 0.001 (~$28) | 1 % |
| US500 | 0.6 | 7 679 | **0.78** | 0.01 (~$77) | 1 % |
| EUR/USD | 0.7 pips | 1.1259 | **0.62** | 100 unidades (~$113) | 1 % |
| GBP/USD | 1.3 pips | 1.3491 | **0.96** | 100 unidades | 1 % |

- Reseñas externas dan valores parecidos: EUR/USD ~0.6–0.7 pips, oro 0.3–0.5, US100 1.8, BTC entre 50 y más de 100 ([ForexBrokers](https://www.forexbrokers.com/reviews/capital-com/fees), [BrokerChooser](https://brokerchooser.com/ar/broker-reviews/capitalcom-review/capitalcom-eurusd-spread)).
- El spread publicado parece un valor "típico" casi fijo: el mismo 0.5/0.6/50 aparece en capturas de octubre. El spread real varía. **No encontré ninguna tabla oficial de cuánto se amplía** en el rollover, en Asia o fuera del horario del contado. La mecánica general es conocida: a las 17:00 ET los bancos cambian la fecha valor, reinician sistemas y retiran liquidez, y los brokers trasladan esa ampliación al cliente durante minutos (a veces más) ([BlackBull](https://blackbull.com/en/education-hub/understanding-roll-over-and-widening-spreads-2), [FXCM](https://www.fxcm.com/eu/help/rollover-when-is-rollover-booked/)).
- Mis multiplicadores supuestos **(NO VERIFICADO)**: FX y oro ×1.5 en Asia y ×3 o más en 15:45–17:30 CDMX. Índices ×2 fuera del contado (Asia) y ×3 o más en el cierre. Crypto ×1 entre semana (el spread de 50 parece fijo en $). Durante el fin de semana, en crypto, el spread nominal ya equivale a un rango de 5 m, aun sin ampliarse.
- **Acción para el bot:** registrar bid/ask de cada epic cada minuto en la demo durante 2–4 semanas y sustituir estos supuestos por medianas y percentiles reales de spread por hora y día de la semana.

---

## 4. Volatilidad intradía medida (datos reales)

**Método.** El rango de cada vela es (máximo − mínimo)/cierre, en puntos básicos (bps). Promedié por hora en días lunes a viernes.
- BTC, ETH y PAXG (proxy de oro 24/7): velas de 1 m de Binance, ago–oct 2026 ([data.binance.vision](https://data.binance.vision)), ~92 días.
- GC=F (oro), NQ=F (≈US100), ES=F (≈US500): velas de 5 m de 60 días y de 1 m de 7 días de la API de gráficos de Yahoo Finance.
- Agrupé por hora de **Nueva York** y etiqueté como **CDMX invierno = ET − 1** (UTC = ET + 5). Así los picos de EE. UU. y Europa caen en la hora de CDMX que tendrán desde el 1-nov. Los rasgos asiáticos (apertura de Tokio) caerán ~1 h **antes** de lo que marca la tabla, porque la muestra fue casi toda en EDT.
- Los datos de FX de Yahoo y de EURUSDT en Binance están cuantizados (tick ≈ 1 pip), así que no sirven para el rango de 5 m. Estimé el FX con la proporción **rango 5 m / rango diario**, que medí en GC/NQ/ES: k = 0.049–0.055, media 0.052. La apliqué al rango diario real de EUR/USD (42.6 bps ≈ 48 pips) y GBP/USD (41.2 bps), repartido por hora según la forma horaria de EURUSDT (`daily_calib.py`).

**Rango medio de 5 m (bps) por hora, lunes a viernes:**

| CDMX inv | UTC inv | BTC | ETH | Oro (GC) | US100 (NQ) | US500 (ES) |
|---|---|---|---|---|---|---|
| 17 | 23 | 10.7 | 16.1 | 6.3 | 6.6 | 3.7 |
| 18 | 00 | 9.6 | 13.3 | 6.9 | 6.1 | 3.3 |
| 19 | 01 | 12.4 | 16.5 | 11.8 | 9.9 | 4.9 |
| 20 | 02 | 14.0 | 18.8 | 14.0 | 8.6 | 4.3 |
| 21 | 03 | 12.5 | 17.4 | 10.9 | 6.8 | 3.4 |
| 22 | 04 | 10.5 | 14.1 | 8.7 | 6.2 | 3.0 |
| 23 | 05 | 10.5 | 14.3 | 7.3 | 5.4 | 2.7 |
| 00 | 06 | 11.4 | 15.6 | 10.8 | 7.1 | 3.6 |
| 01 | 07 | 10.6 | 14.6 | 9.9 | 7.4 | 4.1 |
| 02 | 08 | 11.4 | 15.4 | 10.2 | 8.0 | 4.8 |
| 03 | 09 | 14.9 | 19.1 | 10.4 | 8.7 | 5.1 |
| 04 | 10 | 13.1 | 17.7 | 8.7 | 7.0 | 4.2 |
| 05 | 11 | 11.8 | 16.3 | 8.4 | 6.7 | 4.2 |
| 06 | 12 | 12.3 | 16.9 | 9.7 | 8.4 | 5.1 |
| **07** | 13 | 17.2 | 23.1 | **16.9** | 10.1 | 6.6 |
| **08** | 14 | **24.2** | **30.7** | **17.2** | **16.2** | **9.0** |
| **09** | 15 | **26.9** | **33.5** | **17.3** | **16.6** | **10.2** |
| 10 | 16 | 22.4 | 29.7 | 12.9 | 12.5 | 8.5 |
| 11 | 17 | 17.4 | 24.4 | 10.7 | 10.7 | 7.4 |
| 12 | 18 | 15.0 | 20.6 | 9.2 | 9.2 | 6.5 |
| 13 | 19 | 14.9 | 21.1 | 10.2 | 9.4 | 6.9 |
| 14 | 20 | 12.7 | 17.7 | 9.1 | 10.9 | 7.7 |
| 15 | 21 | 11.4 | 18.0 | 6.0 | 6.6 | 4.0 |
| 16 | 22 | 10.5 | 17.1 | cerrado | cerrado | cerrado |

- **Rango medio de 1 m en el solapamiento (07–11 CDMX):** BTC 8.7, ETH 11.7, GC 6.5, NQ 8.0, ES 4.5 bps. En Asia: BTC 4.0, ETH 5.9 bps. El rango de 1 m es ~1/2.5 del de 5 m, así que con velas de 1 m el costo relativo del spread es ~2.5 veces mayor.
- **Volumen de BTC en Binance:** el pico es a las 09–10 CDMX inv, con $1.3–1.5 M/min frente a $0.55–0.65 M/min entre las 15–18 CDMX. Entre semana se negocia el doble que el fin de semana ($0.97 M frente a $0.46 M por minuto).
- Coincide con la literatura sobre la estacionalidad intradía en forma de "U" o de picos por sesión, y con los saltos en los anuncios macro ([Andersen & Bollerslev 1998, *J. Finance*](https://www.nber.org/papers/w5783)). En FX, Londres concentra el 38 % del volumen mundial y EE. UU. ~19 % ([BIS Triennial 2025](https://www.bis.org/press/p250930.htm)), de ahí que el solapamiento Londres–NY sea la ventana dominante. Un estudio de 14 años sitúa el rango medio de EUR/USD en el solapamiento en ~16 pips, antes ~20 ([Quanthedge](https://quanthedge.substack.com/p/eurusd-profile-a-statistical-view)) **(NO VERIFICADO, fuente secundaria)**.

---

## 5. La razón clave: spread ÷ rango típico de 5 m

Fórmula: razón = spread_bps / rango5m_bps. Ejemplo para BTC en el solapamiento: 50/80 312 = 6.23 bps, y 6.23/22.7 = **0.27**. El spread se come el 27 % del movimiento típico de una vela de 5 m.

Rangos de 5 m por bloque (bps, lunes a viernes): BTC 11.4 / 12.7 / 22.7 / 15.0 / 11.0; ETH 15.6 / 17.1 / 29.3 / 21.0 / 17.6; oro 10.0 / 9.5 / 16.1 / 9.8 / 3.0; US100 7.2 / 7.7 / 13.8 / 10.0 / 5.0; US500 3.7 / 4.7 / 8.6 / 7.2 / 3.7; EUR/USD (estimado) 1.8 / 2.9 / 3.0 / 1.9 / 1.6; GBP/USD (estimado) 1.8 / 2.8 / 2.9 / 1.9 / 1.6. El orden es Asia / Londres / Solape / NY tarde / Cierre.

**Tabla (`ratio_table.py`).** Cada celda da la razón con el spread nominal y, entre paréntesis, la razón con el spread multiplicado por los supuestos **(NO VERIFICADO)** de la sección 3. Menor es mejor. Por debajo de 0.10 es excelente, entre 0.10 y 0.20 es aceptable, entre 0.20 y 0.35 es difícil y por encima de 0.35 no conviene hacer scalping.

| Instrumento | Asia 18–02 (00–08 UTC) | Londres 02–07 (08–13) | **Solape 07–11 (13–17)** | NY tarde 11–15 (17–21) | Cierre 15–17 (21–23) | Sábado | Domingo |
|---|---|---|---|---|---|---|---|
| **US100** | 0.09 (0.18) | 0.08 (0.12) | **0.05** | **0.06** | 0.13 (0.38) | cerrado | cerrado |
| **GOLD** | 0.12 (0.18) | 0.13 (0.15) | **0.08** | 0.12 (0.15) | 0.40 (1.2) — pausa de 1 h | cerrado | cerrado |
| **US500** | 0.21 (0.43) | 0.17 (0.25) | **0.09** | 0.11 | 0.21 (0.64) | cerrado | cerrado |
| EUR/USD | 0.34 (0.51) | 0.22 | 0.21 | 0.32 (0.39) | 0.38 (1.1) | cerrado | cerrado |
| ETH/USD | 0.47 | 0.42 | 0.25 | 0.35 | 0.41 | 0.72 | 0.56 |
| BTC/USD | 0.54 | 0.49 | 0.27 | 0.41 | 0.57 | **1.02** | **0.82** |
| GBP/USD | 0.54 (0.82) | 0.34 | 0.33 | 0.52 (0.62) | 0.61 (1.8) | cerrado | cerrado |

Conclusiones:
1. **US100 y GOLD son por mucho los más baratos de operar** con relación al movimiento. US500 queda en tercer lugar, sobre todo con el contado de EE. UU. abierto.
2. **En Capital.com las crypto son caras para scalping.** El spread de BTC (~6 bps) es entre 5 y 10 veces el del US100 en términos relativos. Solo el solapamiento (07–11 CDMX) deja la razón por debajo de 0.3. **El fin de semana el spread iguala o supera el rango típico de 5 m**: no hay ventaja estadística para scalping.
3. En FX con una cuenta de solo spread, EUR/USD es aceptable solo de 02 a 11 CDMX. GBP/USD no compensa.
4. Hay que contar el costo de ida y vuelta: se paga 1 spread por operación, más el slippage. Con una razón de 0.27, una meta de +1 rango de 5 m deja ~0.73 rangos de margen bruto, y un stop de 1 rango cuesta 1.27 rangos.

---

## 6. Fines de semana

- **Solo las crypto están abiertas en Capital.com.** Hay mantenimiento de vie 23:00 a sáb 01:00 CDMX, una pausa diaria de 15:00–15:05 CDMX y el domingo de 16:00–16:05.
- **Volatilidad medida (Binance, rango de 5 m):** BTC 14.4 bps entre semana, 6.1 el sábado y 7.6 el domingo. ETH 19.7, 10.0 y 13.0. El volumen de BTC cae ~52 %. El rango del fin de semana repunta los domingos de 15–17 CDMX (8.9–10.6 bps en BTC), coincidiendo con la reapertura de los futuros y del FX.
- Kaiko: la parte del volumen de BTC que se negocia en fin de semana bajó de ~24 % (2018) a 13–17 % (2023–24), con cierta recuperación de la profundidad en 2025 ([Decrypt/Kaiko](https://decrypt.co/219288/bitcoin-crypto-weekend-trading-liquidity-kaiko)). Desde el 29-may-2026 los futuros de crypto de CME operan 24/7 (con mantenimiento de fin de semana), lo que debería reducir los "gaps de CME" ([The Block](https://theblock.co/post/390491/cme-group-launch-24-7-crypto-futures-options-trading-may-29)).
- **Riesgo de gap en los instrumentos que cierran** (`weekend_gaps.py`, Yahoo 5m, último cierre del viernes contra la primera apertura del domingo, 10–12 fines de semana):

| | EUR/USD | GBP/USD | Oro | US100 (NQ) | US500 (ES) |
|---|---|---|---|---|---|
| Gap medio (bps) | 7.2 | 4.0 | 21.7 | 41.6 | 22.8 |
| Máximo (bps) | 24.7 | 14.8 | 83.9 | 130.8 | 65.3 |

  Un gap medio del US100 equivale a ~3 rangos de 5 m del solapamiento, y el máximo a ~10. **Hay que cerrar todo antes del viernes 15:45 CDMX.** En crypto, el movimiento absoluto de vie 17:00 ET a dom 18:00 ET fue de 74 bps de media en BTC (máximo 182) y 125 en ETH (máximo 282). Como Capital.com sigue cotizando crypto, eso no es un gap, pero sí es un riesgo para cualquier posición abierta sin vigilancia.

---

## 7. Eventos programados de alto impacto (CDMX, invierno)

| Evento | Hora CDMX | Próximas fechas |
|---|---|---|
| NFP (empleo de EE. UU.) | 07:30 | **vie 6-nov-2026** (informe de octubre), vie 4-dic-2026 ([calendarx](https://www.calendarx.com/events/jobs-report-november-2026), [BLS](https://www.bls.gov/schedule/2026/)) **(NO VERIFICADO en bls.gov)** |
| CPI de EE. UU. | 07:30 | ~10-nov-2026 (octubre) **(NO VERIFICADO)**; 10-dic-2026 (noviembre) |
| Solicitudes de desempleo | 07:30 todos los jueves | — |
| BCE (decisión 14:15 CET, conferencia 14:45) | 07:15 / 07:45 | ~17-dic-2026 ([BCE](https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html)) **(NO VERIFICADO)** |
| Banco de Inglaterra 12:00 Londres | 06:00 | — |
| ISM, JOLTS 10:00 ET | 09:00 | — |
| Inventarios de crudo EIA (miércoles 10:30 ET) | 09:30 | — |
| FOMC 14:00 ET, conferencia 14:30 | 13:00 / 13:30 | **mié 9-dic-2026** ([Fed](https://www.federalreserve.gov/newsevents/2026-december.htm)) |
| Feriados de EE. UU. | Thanksgiving jue 26-nov (contado cerrado), vie 27-nov sesión corta; 25-dic | Liquidez mínima: no operar índices |

Regla: **no abrir operaciones de 2 min antes a 5 min después** de cada evento (de 10 a 15 min para FOMC/NFP/CPI). Cerrar o pausar las posiciones del instrumento afectado. En verano, todas las horas de EE. UU. y Europa se adelantan 1 h en CDMX.

---

## 8. Calendario de rotación (CDMX, horario de invierno vigente 1-nov-2026 → 13-mar-2027)

Cuenta de $100: usar los tamaños mínimos (sección 3) y como máximo 1–2 posiciones simultáneas. Las razones vienen de la sección 5.

| Franja CDMX (UTC) | Operar | Evitar | Acción |
|---|---|---|---|
| **Dom 16:00–17:30** (22:00–23:30) | — | Todo | FX reabre a las 16:05 y oro/índices a las 17:00, con gap y spreads amplios. Solo observar. |
| **Lun–jue 17:30–18:00** (23:30–00:00) | — | Todo (reapertura tras la pausa) | Esperar a que el spread vuelva a su mediana. |
| **18:00–02:00 Asia** (00:00–08:00) | **US100 y GOLD** con tamaño mínimo (0.09–0.18); el mejor tramo es 18:00–21:00, por la apertura de Tokio y China | BTC/ETH (0.5), GBP/USD, US500 (0.2–0.4), EUR/USD (0.34–0.5) | Exigir spread en vivo ≤ 1.5 × su mediana; si no, saltar. Ventana opcional de bajo riesgo. |
| **02:00–07:00 Londres** (08:00–13:00) | **US100, GOLD**, EUR/USD (0.22), US500 (0.17–0.25) | BTC/ETH (0.42–0.49), GBP/USD (0.34) | Apertura de Londres a las 02:00 y BoE a las 06:00 (pausar). |
| **07:00–07:40 noticias** | Solo si no hay dato a las 07:30 | Todo en días de NFP/CPI/BCE | Pausa de 07:25 a 07:40 (BCE: 07:10–07:55). |
| **07:40–11:00 solapamiento + apertura del contado** (13:40–17:00) | **Todo:** US100 (0.05), GOLD (0.08), US500 (0.09), EUR/USD (0.21), ETH (0.25), BTC (0.27) | GBP/USD (0.33) | **Ventana principal (prime time).** Pausa de 08:28 a 08:35 por la apertura del contado. Es la única ventana donde la crypto es razonable. |
| **11:00–14:45 NY tarde** (17:00–20:45) | **US100, US500, GOLD** | EUR/USD y GBP/USD (más de 0.3), crypto (0.35–0.41) | FOMC a las 13:00 CDMX: pausar de 12:50 a 13:45. |
| **14:45–15:10** (20:45–21:10) | Índices y oro (cerrar o reducir) | Crypto | **Cerrar crypto antes de las 14:55** (pausa de 15:00–15:05). Ocurre también el cierre del contado a las 15:00. |
| **15:10–15:45** (21:10–21:45) | Nada nuevo | Todo | Solo gestionar las salidas. |
| **15:45–17:30 rollover** (21:45–23:30) | — | **Todo** | **Quedar en flat a las 15:45**: el funding es a las 16:00, el oro hace pausa de 15:59 a 17:00, FX e índices de 16:00 a 16:05, y los spreads son máximos. |
| **Viernes 14:45 → domingo** | — | — | **Cerrar todo antes del viernes 15:45** (riesgo de gap, sección 6). |
| **Sáb–Dom (crypto)** | **No operar** (razón 0.56–1.02) | BTC/ETH | El mantenimiento de vie 23:00 a sáb 01:00 queda bloqueado. Si se quiere actividad, solo ETH el domingo 15–18 con filtro de spread estricto, como experimento en demo. |
| Feriados de EE. UU. | GOLD/FX con tamaño mínimo | Índices | Thanksgiving: 26-nov-2026. |

**En verano (desde el 14-mar-2027):** restar 1 h a todas las franjas ligadas a NY y Londres (solapamiento 06–10, apertura 07:30, rollover y flat a las 14:45–16:30). Asia no cambia: Tokio sigue a las 18:00 CDMX. Antes de aplicarlo, confirmar en `openingHours` si la pausa de Capital.com pasa a 21:00 UTC **(NO VERIFICADO)**.

---

## 9. Recomendaciones para el diseño (resumen)

1. **Universo principal: US100 y GOLD, luego US500.** EUR/USD solo de 02 a 11 CDMX. BTC y ETH solo de 07:40 a 11:00 CDMX entre semana. GBP/USD queda fuera.
2. **Usar velas de 5 m o más, no de 1 m**: con velas de 1 m la razón spread/rango sube ~2.5 veces. Con BTC en 1 m llega a 0.7, inviable.
3. **Filtro dinámico:** antes de cada entrada, operar solo si spread_actual / ATR(5m, 14) < umbral. Propuesta: 0.15 para índices y oro, 0.30 para crypto.
4. **Horarios desde la API** (`openingHours`, `marketStatus`) y husos con `zoneinfo`. No escribir offsets fijos.
5. **Quedar en flat todos los días a las 15:45 CDMX** (14:45 en verano) **y el viernes antes del cierre**. Así no se paga funding (crypto: −0.06 %/día) ni se queda expuesto a los gaps.
6. **Calendario económico integrado** con pausas alrededor de los eventos de la sección 7.
7. **Recalibrar con datos propios:** registrar el spread de la demo cada minuto durante 2–4 semanas y rehacer la tabla de la sección 5 con los spreads reales por hora, en lugar de los multiplicadores supuestos.

**Limitaciones:** los futuros (NQ/ES/GC) son un proxy de los CFD de Capital.com, que se cotizan sobre ellos o sobre el contado. La muestra cubre 2.5–3 meses (ago–nov 2026), mayormente en EDT. El rango de FX es una estimación indirecta. Los spreads publicados son una sola captura.
