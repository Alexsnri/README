# 03 — Evidencia sobre estrategias de scalping/intradía para CFDs en Capital.com

Alcance: bot automático, barras de 1m–15m, holding de minutos a horas, CFDs de Capital.com (costo = spread, sin comisión), instrumentos BTC/USD, ETH/USD, XAU/USD, US100, US500, EUR/USD, GBP/USD, cuenta demo de $100. Las afirmaciones que no pude verificar en una fuente primaria van marcadas **(NO VERIFICADO)**. Los cálculos propios van marcados como "estimación propia".

---

## 0. Resumen ejecutivo (lo honesto primero)

1. **La evidencia general va en contra del day trading minorista.** El 74–89% de las cuentas minoristas de CFD pierden dinero ([ESMA, 2018](https://www.esma.europa.eu/node/84933)). Las advertencias propias de Capital.com van de ~65% a ~85% según la entidad y el periodo ([Investing.com](https://www.investing.com/brokers/capital.com), [Capital.com EU](https://capital.com/en-eu/help)). De los day traders brasileños que persistieron más de 300 días, el 97% perdió dinero ([Chague, De-Losso y Giovannetti, 2019](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101)). En Taiwán, menos del 1% gana de forma predecible después de comisiones ([Barber, Lee, Liu y Odean, 2014](https://ideas.repec.org/a/eee/finmar/v18y2014icp1-24.html)).
2. **A 1–5 minutos, el spread de Capital.com se come casi cualquier ventaja publicada.** La predictibilidad intradía que reporta la academia ronda un R² de 1–2%, es decir, una correlación señal-retorno de ~0.10–0.14. Con eso solo se cubre el spread en **índices (US100/US500) con holdings de ≥15 minutos** y, como mucho, en oro o FX con holdings de ~1 hora. En BTC/ETH, el scalping de 1–5 minutos es aritméticamente inviable (sección 2).
3. **Las estrategias con mejor evidencia no son "scalping"**: son de momentum intradía con holdings de 30 minutos a varias horas (Noise Area/VWAP, ORB y momentum de la última media hora). Por eso recomiendo que el bot use barras de 1–5m para *ejecutar y gestionar*, pero que las señales vivan en el horizonte de 15m a horas.
4. **Las cifras de los papers están infladas**, por minería de datos y por el decaimiento que sigue a la publicación (sección 4). Conviene descontarles **al menos 50%** antes de comparar contra costos.

---

## 1. Evidencia general: el day trading minorista después de costos

| Fuente | Muestra | Resultado |
|---|---|---|
| [ESMA, intervención de producto 2018](https://www.esma.europa.eu/node/84933) | Análisis de NCAs en la UE | El 74–89% de las cuentas minoristas de CFD pierden. Pérdida media de €1,600 a €29,000 por cliente. Límites de apalancamiento minorista: 30:1 en FX mayores; 20:1 en oro e índices mayores; 2:1 en cripto ([ESMA Q&A](https://www.consob.it/documents/1912911/1970971/esma35_43_1000.pdf/6dc9bc30-c528-09dc-9430-398c8df4c3af)) |
| Advertencia de Capital.com | Varía por entidad | 73% (EU help), 84.01% (página global de Investing.com), 70–83.5% (UK) ([Investing.com](https://www.investing.com/brokers/capital.com), [Capital.com EU](https://capital.com/en-eu/help)). La cifra exacta de la entidad que usaría la cuenta está **(NO VERIFICADO)** |
| [Chague, De-Losso y Giovannetti, "Day Trading for a Living?"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101) | 19,646 personas que hicieron day trading de mini-índice en Brasil, 2013–2015 | De quienes operaron más de 300 días, el 97% perdió y solo el 1.1% ganó más que el salario mínimo. La proporción de rentables **cae** con más días de práctica (29.8% con 1 día y 3.0% con más de 300). No hay evidencia de aprendizaje ([resumen en Quantpedia](https://quantpedia.com/retail-day-trading-is-an-uphill-battle/)) |
| [Barber, Lee, Liu y Odean, "The cross-section of speculator skill" (JFM 2014)](https://ideas.repec.org/a/eee/finmar/v18y2014icp1-24.html) | Todos los day traders de Taiwán, 1992–2006 | Menos del 1% obtiene retornos anormales positivos de forma predecible, netos de comisiones |
| [Barber et al., "Learning, fast or slow" (RAPS 2020)](https://econpapers.repec.org/RePEc:oup:rasset:v:10:y:2020:i:1:p:61-93.) (antes "Do day traders rationally learn…", [WP](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/day%20trading%20and%20learning%20110217.pdf)) | Taiwán | El desempeño agregado es negativo y la mayor parte del volumen viene de traders con historial de pérdidas. Los resultados apuntan a sobreconfianza, no a aprendizaje racional |
| [Neely y Weller (JIMF 2003), "Intraday technical trading in the FX market"](https://gpbib.cs.ucl.ac.uk/gp-html/neely_2003_JIMF.html) | Reglas intradía optimizadas en FX (programación genética y modelos lineales) | **Sin retornos en exceso** con costos y horarios realistas, aunque las reglas detectan patrones estables |
| [Marshall, Cahan y Cahan (JEF 2008)](https://ideas.repec.org/a/eee/empfin/v15y2008i2p199-210.html) | Análisis técnico intradía en acciones de EE.UU. | Concluye que no aporta valor (lo cita así [CXO](https://cxoadvisory.com/technical-trading/technical-analysis-anathema-to-the-academic-world)). No leí el texto completo **(NO VERIFICADO en el texto)** |

**Lectura:** un bot no tiene los sesgos conductuales de un humano, pero sí enfrenta la misma barrera de costos. La razón dominante de las pérdidas a horizontes cortos es la fricción: el market maker cobra el spread en cada viaje redondo.

---

## 2. Aritmética de costos: qué ventaja bruta hace falta

### 2.1 Spreads típicos de Capital.com, convertidos a puntos base (round-trip = 1 spread)

Los spreads son variables y estos datos son snapshots de terceros: [Economies.com, oct-2026](https://www.economies.com/investing/forex/lowest-spread-cfd-broker-2026-commission-free-low-deposit-and-guaranteed-stops-188), [DailyForex](https://www.dailyforex.com/forex-brokers/capital-com-review) y [WikiFX, dic-2024](https://www.wikifx.com/en/newsdetail/202412137044876051.html). Los precios de referencia para pasar a bps son supuestos **(NO VERIFICADO)**, y el agente de costos debe sustituirlos por los spreads reales que entregue la API.

| Instrumento | Spread reportado | Precio supuesto | Costo round-trip en bps (c) |
|---|---|---|---|
| BTC/USD | 50–106 USD | ~100,000 | ~5–10.6 (uso 7.5) |
| ETH/USD | **(NO VERIFICADO)** ~2–4 USD | ~3,500 | ~6–11 (uso 8) |
| XAU/USD | 0.3–0.5 | ~4,000 | ~0.8–1.3 (uso 1.0) |
| US100 | ~1.8 pts | ~25,000 | ~0.7 |
| US500 | 0.5–0.6 pts | ~6,700 | ~0.8–0.9 |
| EUR/USD | 0.6–0.7 pips | ~1.16 | ~0.55 |
| GBP/USD | 1.3 pips | ~1.33 | ~1.0 |

A esto hay que sumarle el slippage en órdenes stop/market y el ensanchamiento del spread en aperturas, noticias, rollover diario (~22:00 UTC) y fines de semana en cripto. Para el backtest sugiero usar, como mínimo, **costo = 1.25× el spread medio** y estresar con 2×.

### 2.2 Volatilidad por horizonte frente a costo (estimación propia)

Uso volatilidades anuales típicas **(NO VERIFICADO; recalcular con datos)**: BTC 50%, ETH 65%, XAU 16%, US100 22%, US500 17%, EUR/USD 7% y GBP/USD 8%. Para escalar a σ por minuto tomo 525,600 min/año en cripto y ~358,800 en el resto. La realidad es peor fuera de sesión, porque la volatilidad se concentra en las aperturas ([Ito y Hashimoto, 2006](https://www.nber.org/papers/w12413.pdf)) mientras el spread se mantiene igual o se ensancha.

Defino tres cantidades:
- **c/σₕ**: costo como fracción de la desviación estándar del retorno a horizonte h.
- **p\***: tasa de acierto direccional de equilibrio, si se apuesta el signo de un retorno ~Normal. Sale de (2p−1)·0.798·σₕ = c, así que p\* = 0.5 + 0.627·c/σₕ.
- **ρ\***: correlación mínima señal-retorno necesaria, con ρ\* ≈ c/(0.798·σₕ). Como referencia, un R² publicado de 1–2% equivale a ρ ≈ 0.10–0.14.

| Instr. | σ 1m (bps) | 1m: c/σ · p\* · ρ\* | 5m: c/σ · p\* · ρ\* | 15m: c/σ · p\* · ρ\* | 60m: c/σ · p\* · ρ\* |
|---|---|---|---|---|---|
| BTC | 6.9 | 1.09 · imposible · 1.36 | 0.49 · 0.80 · 0.61 | 0.28 · 0.68 · 0.35 | 0.14 · 0.59 · 0.18 |
| ETH | 9.0 | 0.89 · imposible · 1.12 | 0.40 · 0.75 · 0.50 | 0.23 · 0.64 · 0.29 | 0.12 · 0.57 · 0.14 |
| XAU | 2.7 | 0.37 · 0.73 · 0.47 | 0.17 · 0.61 · 0.21 | 0.10 · 0.56 · 0.12 | 0.05 · 0.53 · 0.06 |
| US100 | 3.7 | 0.19 · 0.62 · 0.24 | 0.09 · 0.55 · 0.11 | 0.05 · 0.53 · 0.06 | 0.03 · 0.52 · 0.03 |
| US500 | 2.8 | 0.32 · 0.70 · 0.40 | 0.14 · 0.59 · 0.18 | 0.08 · 0.55 · 0.10 | 0.04 · 0.53 · 0.05 |
| EUR/USD | 1.2 | 0.47 · 0.80 · 0.59 | 0.21 · 0.63 · 0.26 | 0.12 · 0.58 · 0.15 | 0.06 · 0.54 · 0.08 |
| GBP/USD | 1.3 | 0.75 · 0.97 · 0.94 | 0.33 · 0.71 · 0.42 | 0.19 · 0.62 · 0.24 | 0.10 · 0.56 · 0.12 |

**Conclusión cuantitativa:** con ρ ≈ 0.12, que ya es optimista porque es el nivel de los mejores papers *antes* de descontar decaimiento, el spread solo se cubre en:
- US100 desde ~5m y US500 desde ~15m, idealmente en sesión NY.
- XAU desde ~15m.
- EUR/USD y GBP/USD desde ~60m.
- BTC y ETH no se cubren ni a 60m: harían falta ρ ≈ 0.15–0.18, algo que no aparece en la literatura neta de costos.

Un scalper de 1–5 minutos necesita aciertos de 60–80% sostenidos. No encontré ninguna fuente creíble que documente algo así para minoristas. La misma regla vale para estrategias con stop/target asimétricos: **la ganancia bruta media por operación debe superar a c**. Cambiar la forma del payoff no cambia esa condición.

---

## 3. Familias de estrategias

### 3.1 Momentum intradía (time-series)

**Evidencia publicada**
- [Gao, Han, Li y Zhou, "Market intraday momentum" (JFE 2018)](https://econpapers.repec.org/RePEc:eee:jfinec:v:129:y:2018:i:2:p:394-414). Con SPY 1993–2013, el retorno de la primera media hora (del cierre previo a las 10:00 ET) predice el de la última media hora (15:30–16:00). El R² fuera de muestra es ~1.2–1.8%. Es más fuerte en días de alta volatilidad y volumen y en días de noticias macro.
  - Regla: comprar a las 15:30 si r₁ > 0 (y estar en cash si no), cerrar a las 16:00. Rinde 6.3% anual bruto, contra −0.5% de mantener todas las últimas medias horas ([CXO](https://cxoadvisory.com/calendar-effects/first-and-last-half-hours-of-trading-linked)).
  - Ganancia bruta por operación ≈ 6.3% / ~140 operaciones ≈ **~4.5 bps** (estimación propia). Frente a ~0.9 bps de US500 queda un margen de ~3.5 bps, en papel.
- [Baltussen, Da, Lammers y Martens (JFE 2021)](https://www3.nd.edu/~zda/intramom.pdf). Con más de 60 futuros (acciones, bonos, materias primas y divisas), 1974–2020, el retorno del cierre previo hasta las 15:30 predice la última media hora. Lo explican por la cobertura de gamma negativa de dealers y ETFs apalancados: el efecto es fuerte con gamma neta negativa y nulo con gamma positiva, y revierte en los días siguientes.
- [Li, Sakkas y Urquhart (JFM 2022)](https://centaur.reading.ac.uk/95566). Encuentran el efecto en 12 de 16 mercados desarrollados, dentro y fuera de muestra. Es más fuerte con baja liquidez, alta volatilidad e información discreta.
- FX: [Elaut, Frömmel y Lampaert (JFM 2018)](https://ideas.repec.org:443/a/eee/finmar/v37y2018icp35-51.html) lo documentan en RUB/USD, ligado a proveedores de liquidez que no quieren quedarse con posición overnight. **No hay evidencia equivalente para EUR/USD o GBP/USD**: en FX 24h, la "apertura" y el "cierre" son ambiguos, lo que Gao et al. reconocen.
- Cripto: [Shen, Urquhart y Wang (Financial Review 2022)](https://research.birmingham.ac.uk/en/publications/bitcoin-intraday-time-series-momentum/) encuentran momentum intradía en BTC, explicado por provisión de liquidez y con mejores resultados en caídas. [Wen, Bouri, Xu y Zhao (NAJEF 2022)](https://ideas.repec.org:443/a/eee/ecofin/v62y2022ics1062940822000833.html) encuentran **momentum y también reversión** en BTC 2013–2020 según saltos, FOMC y liquidez. No pude confirmar en el texto completo cómo trataron los costos **(NO VERIFICADO)**.

**Por qué falla.** Hay pocos trades (uno por día), así que el poder estadístico es bajo. Depende del régimen de gamma, del que no hay datos gratis. [Rosa (J. Futures Markets 2022)](https://ideas.repec.org/a/wly/jfutmk/v42y2022i12p2218-2234.html) muestra que la variante "overnight → última media hora" **desaparece fuera de muestra**. Durante el COVID tampoco fue significativo ([estudio S&P500/CSI300](https://dspace5old.zcu.cz/handle/11025/46501?locale=en)). Además, el CFD de Capital.com cotiza fuera de horario, pero hay que medir si el spread se ensancha en 15:30–16:00 ET **(NO VERIFICADO)**.

**Credibilidad: media-alta.** Tiene dos papers en JFE y replicación internacional. El tamaño del efecto es pequeño y no hay pruebas limpias después de 2014.

### 3.2 Opening Range Breakout y rupturas de volatilidad

**ORB de 5 minutos en QQQ** ([Zarattini y Aziz, SSRN 4416622](https://papers.ssrn.com/abstract=4416622); reglas según [CXO](https://www.cxoadvisory.com/technical-trading/day-trading-with-an-opening-range-breakout-strategy))
- Reglas:
  - Dirección = signo de la primera vela de 5m (9:30–9:35 ET); entrada a las 9:35.
  - Stop en el extremo opuesto de esa vela.
  - Target de 10R o cierre a las 16:00.
  - Riesgo de 1% del capital por trade, con apalancamiento máximo de 4x.
- Resultado: CAGR de 33% en 2016–feb 2023, con 1,795 trades. El backtest supone **cero spread y cero slippage**.
- Replicación independiente en CFDs (NQ, SPX, Dow, DAX, FTSE), 2015–2026, con costos de 2.5 pts en NQ y 0.8 en SPX ([MQL5, blog no revisado por pares](https://www.mql5.com/en/blogs/post/776235)):
  - El resultado bruto se replica: +0.13R por trade y 23% de acierto en NQ.
  - Neto, es **≈0 en NQ (+0.002R) y negativo en los otros 4**.
  - La ventaja sobre una dirección aleatoria es ~0.10–0.13R, "del tamaño del costo de ida y vuelta".
  - Fuera de muestra (2021–2026), NQ da como máximo +0.06R bruto.
- Sensibilidad (estimación propia): en esa replicación el costo equivale a 6–12% del riesgo inicial, así que R ≈ 25–30 pts NQ ≈ 0.11% y la ganancia bruta ≈ 0.13R ≈ **~1.5 bps** por trade. El spread de US100 en Capital.com (~0.7 bps) es menor que los 2.5 pts supuestos, lo que dejaría un neto marginalmente positivo *si* el slippage del stop es bajo. Es frágil.
- La versión "Stocks in Play" ([Zarattini, Barbon y Aziz, SSRN 4729284](https://alexandria.unisg.ch/handle/20.500.14171/122125)) reporta un Sharpe de 2.81, pero opera **acciones individuales** filtradas por volumen relativo. No es transferible a nuestros instrumentos.
- En crudo, [Holmberg, Lönnbark y Lundström (FRL 2013)](https://ideas.repec.org/a/eee/finlet/v10y2013i1p27-33.html) encuentran un ORB con retornos significativamente positivos, aunque el texto completo no revisado no deja claro si son netos de costos **(NO VERIFICADO)**.

**"Noise Area" + VWAP en SPY** ([Zarattini, Aziz y Barbon, "Beat the Market", SSRN 4824172 / SFI 24-97](https://alexandria.unisg.ch/server/api/core/bitstreams/a99aba00-f967-49b3-aceb-f544dc386e0b/content); reglas extraídas del PDF)
- Reglas:
  1. Para cada hora del día HH:MM se calcula σ = promedio de 14 días de |Close(HH:MM)/Open(9:30) − 1|.
  2. Banda superior = max(Open, Close previo)·(1 + VM·σ); banda inferior = min(Open, Close previo)·(1 − VM·σ). La base es VM = 1.
  3. Solo se evalúa en HH:00 y HH:30. Arriba de la banda se va largo y debajo, corto.
  4. Trailing stop = max(banda, VWAP) para largos y min(banda, VWAP) para cortos. Todo se cierra al final del día.
  5. Tamaño por objetivo de volatilidad diaria de 2%, con un máximo de 4x.
- Resultados 2007–2024: 19.6% anual, Sharpe 1.33, neto de $0.0035/acción de comisión y $0.001 de slippage medido en real (1,000 órdenes).
- Por operación: 7,668 trades, 37% de acierto y **PnL medio de $0.09 por acción**. Con un precio medio de SPY ~$230 eso es **~4 bps por operación** (estimación propia). Frente a ~0.9 bps del US500 en Capital.com, la relación ventaja/costo es **~4:1, la mejor de todo lo revisado**.
- Régimen: el Sharpe sube con el VIX (~1.5 con VIX bajo, ~3.5 con VIX > 40) y es mayor con gamma de dealers negativa.
- Riesgos: los autores son también vendedores de cursos de trading (Bear Bull Traders). No es un paper revisado por pares. Hay varios parámetros elegidos in-sample (14 días, HH:00/HH:30, VM). La propia [réplica de QuantConnect del paper VWAP](https://www.quantconnect.com/research/15348/intraday-etf-momentum/) reporta cifras "muy inferiores" para su trabajo previo sobre VWAP ([Concretum](https://concretumgroup.com/volume-weighted-average-price-vwap-the-holy-grail-for-day-trading-systems/)).

**London breakout y Asian range en FX.** No encontré evidencia académica. Un backtest de proveedor en GBP/USD 15m (2016–2026, stop de 20 pips y target de 40) da **−60%** de retorno total; la versión EUR/USD sale "casi neutral" ([Backtrex](https://backtrex.com/en/backtests/london-breakout-gbp-usd), no revisado). Lo que sí está documentado es que la volatilidad y la actividad se concentran en las aperturas de Tokio y Londres ([Ito y Hashimoto, 2006](https://www.nber.org/papers/w12413.pdf)). Eso justifica *probar* el ORB en la apertura de Londres, pero no es evidencia de que funcione.

**Bollinger squeeze / Donchian intradía.** Tampoco hay evidencia rigurosa intradía. [Lento, Gradojevic y Wright (2007)](https://ideas.repec.org/a/taf/raflxx/v3y2007i4p263-267.html) estudian las Bollinger en datos diarios, y no pude verificar su conclusión **(NO VERIFICADO)**. Los trabajos de Neely y Weller y de Marshall et al. (sección 1) sugieren que las reglas técnicas intradía genéricas no sobreviven a los costos.

### 3.3 Reversión a la media (VWAP, Bollinger, z-score, RSI(2))

- **La micro-reversión que se ve en los datos es en buena parte rebote bid-ask.** [Heston, Korajczyk y Sadka (JF 2010)](https://arxiv.org/pdf/1005.3535.pdf) atribuyen la reversión de menos de una hora a desequilibrios temporales de liquidez y al rebote bid-ask. En FX, [Cheng (2006)](https://northampton.academia.edu/MelodyCheng) y Lo y Hsieh hallan autocorrelación negativa en DEM/USD a menos de 1 minuto, pero **no explotable**: la estructura es inestable y la ganancia es menor que el tick. [Wiśniewska (2014)](https://econpapers.repec.org/RePEc:vrs:foeste:v:14:y:2014:i:2:p:152-162:n:14) estudia la reversión a la media móvil en EUR/USD de 1 minuto.
  - **Trampa de backtest:** si se prueba sobre precio medio o "last", la reversión parece rentable. En la realidad, cada entrada paga medio spread *contra* la reversión que se quiere capturar. Hay que backtestear siempre con bid/ask.
- **Cripto.** [De Nicola (Ledger 2021)](https://epub.ub.uni-muenchen.de/97651/) encuentra autocorrelación negativa significativa en BTC a 1, 2 y 4 horas, y los movimientos más grandes revierten más (lo atribuye a sobrerreacción y liquidaciones apalancadas). [Wen et al. (2022)](https://ideas.repec.org:443/a/eee/ecofin/v62y2022ics1062940822000833.html) encuentran reversión intradía "única de cripto". En contra, [Caporale, Plastun y Oliinyk (2019)](https://bura.brunel.ac.uk/bitstream/2438/18238/5/FullText.pdf) concluyen que **operar contra sobrerreacciones en BTC no es rentable** en simulación con robot. Para el horizonte de 1–5 minutos no hay evidencia directa.
- **Overnight vs. intradía.** [Lou, Polk y Skouras (JFE 2019)](https://personal.lse.ac.uk/polk/research/TugOfWar.pdf) muestran que en acciones el momentum gana overnight y la reversión intradía, con signos opuestos. Es evidencia de corte transversal, no de índices, pero sugiere que la reversión de *acciones individuales* durante el día es real. Para índices, en cambio, la evidencia de la última media hora (3.1) apunta a **momentum**, no a reversión.
- **RSI(2).** El de Connors y Alvarez es una regla **diaria** con filtro de tendencia (SMA 200) y nació en un libro sin pruebas fuera de muestra ni corrección por minería de datos ([crítica en CXO](https://cxoadvisory.com/technical-trading/a-few-notes-on-short-term-trading-strategies-that-work)). No hay evidencia de que funcione a escala intradía.
- **Sensibilidad al spread: máxima.** La reversión tiene ganancias pequeñas y alto acierto, y su ganancia bruta típica por trade intradía es de ~1–3 bps **(NO VERIFICADO)**. Eso solo podría funcionar en EUR/USD y US100, donde c < 1 bp, y con holdings de ≥15m.

### 3.4 Filtros de régimen y de sesión

- **Volatilidad.** La predictibilidad intradía de momentum crece con la volatilidad: Gao et al.; Li et al.; Beat the Market por niveles de VIX. Un filtro "operar solo si la volatilidad realizada o el ATR de 1 día está por encima de su mediana de 60 días" tiene respaldo indirecto. A la vez, el spread en bps se vuelve relativamente más barato cuando σ sube (tabla 2.2).
- **Sesión.** La actividad y la volatilidad tienen forma de U por sesión ([Ito y Hashimoto](https://www.nber.org/papers/w12413.pdf)), con una relación negativa entre volatilidad y spread. Operar en las aperturas de Londres (07:00–09:00 UTC) y NY (13:30–15:30 UTC) mejora c/σ. Las horas de comida y el cierre de NY en FX son las peores.
- **Tendencia vs. rango (ADX, Hurst, variance ratio).** No encontré evidencia académica de que ADX o Hurst intradía mejoren las reglas netas de costos. El variance ratio de Lo y MacKinlay es un diagnóstico estadístico válido (VR > 1 indica momentum, VR < 1 reversión), pero como filtro operativo agrega parámetros y, por lo tanto, multiple testing. Recomiendo **como máximo un filtro de régimen por estrategia**, con su umbral fijado a priori (mediana o percentil 50 móvil), no optimizado.
- **Gamma de dealers.** Es el mejor filtro documentado (Baltussen et al.; Beat the Market), pero requiere datos de opciones (SqueezeMetrics y similares) que probablemente no tendremos **(NO VERIFICADO)**.

### 3.5 Ventajas específicas de cripto

- **Funding y carry.** [Schmeling, Schrimpf y Todorov, "Crypto carry" (BIS WP 1087)](https://www.bis.org/publ/work1087.htm) encuentran que el carry futuros-spot llega a ~60% anual y que un **carry alto predice crashes** y liquidaciones de posiciones vendidas. Según [VoxEU](https://cepr.org/voxeu/columns/crypto-carry-market-segmentation-and-price-distortions-digital-asset-markets), +10% de carry estandarizado lleva a +22% de liquidaciones en el mes siguiente. El horizonte es de **días a un mes**, no de minutos. [He, Manela, Ross y von Wachter](https://arxiv.org/html/2212.06888v5) documentan desviaciones grandes respecto al precio de no-arbitraje, pero eso es arbitraje spot-perp, que no se puede replicar con CFDs. La relación "funding extremo → reversión" a corto plazo es **floja y mixta** ([Brave New Coin, industria](https://bravenewcoin.com/insights/testing-theory-is-perpetual-swap-funding-rate-predictive)). Capital.com no publica funding: habría que leerlo de Binance o Bybit **(NO VERIFICADO acceso desde el bot)**.
- **Cascadas de liquidación.** El 10-oct-2025 se liquidaron ~$9.9 mil millones en 14 horas, el 70% en 40 minutos ([Amberdata, industria](https://blog.amberdata.io/how-3.21b-vanished-in-60-seconds-october-2025-crypto-crash-explained-through-7-charts)). Suelen terminar con una "mecha" de rebote ([CoinShares](https://coinshares.com/insights/knowledge/billions-in-liquidations-what-happened/)). No hay papers revisados que midan la rentabilidad de operar el rebote. El riesgo es entrar antes de que termine la cascada, y además el spread de CFD se dispara justo en esos minutos **(NO VERIFICADO para Capital.com)**.
- **Fin de semana y día de la semana.** [Caporale y Plastun (2017)](https://cesifo.org/DocDL/cesifo1_wp6716.pdf) encuentran retornos más altos los lunes en BTC, pero advierten que la mayoría de los resultados no son distinguibles de lo aleatorio. La liquidez de fin de semana es menor, lo que significa spreads más anchos.
- **Estacionalidad horaria.** Quantpedia reporta que las horas 22:00 y 23:00 UTC dominan en BTC: largo de 21:00 a 23:00 UTC, con 33–40% anual y drawdown de −22% ([Quantpedia](https://quantpedia.com/are-there-seasonal-intraday-or-overnight-anomalies-in-bitcoin/), [actualización](https://quantpedia.com/the-seasonality-of-bitcoin/)). Los costos **no están reportados**. ln(1.33)/365 ≈ **7.8 bps por operación bruta**, prácticamente igual al spread de BTC en Capital.com, así que el neto esperado es ≈ 0 (estimación propia). [Baur et al.](https://quantpedia.com/strategies/intraday-seasonality-in-bitcoin) no encuentran efectos horarios robustos. Es candidata a ser un falso positivo.

---

## 4. Minería de datos y decaimiento: cuánto descontar

- [McLean y Pontiff (JF 2016)](https://doi.org/10.1111/jofi.12365), verificado en el abstract: en 97 anomalías, los retornos son **26% menores fuera de muestra y 58% menores tras la publicación**. El decaimiento es mayor en las anomalías con mayor retorno in-sample y menor costo de arbitraje. Los índices de EE.UU. son los mercados más baratos de arbitrar, así que el decaimiento esperado es alto.
- [Harvey, Liu y Zhu (RFS 2016)](https://econpapers.repec.org/RePEc:oup:rfinst:v:29:y:2016:i:1:p:5-68.): con tanta minería, un factor nuevo necesita **t > 3.0**, no 2.0.
- [Bailey y López de Prado, Deflated Sharpe Ratio](https://papers.ssrn.com/abstract=2460551) y [Probability of Backtest Overfitting](https://papers.ssrn.com/abstract=2326253): hay que ajustar el Sharpe por el número de pruebas y por la no-normalidad, y estimar el PBO con CSCV.
- Aplicado aquí: la ganancia bruta publicada de ~4 bps de Beat the Market o Gao, descontada 50–60%, queda en ~1.6–2 bps frente a ~0.9 bps de costo en US500. Sigue siendo positiva, pero con un colchón mínimo. El ORB, después del descuento, cae por debajo del costo.

---

## 5. Lista corta para la Etapa 2 (backtest)

**Protocolo común (obligatorio)**
- Datos con bid/ask o spread histórico de Capital.com; si no hay, usar spread medio × 1.25 y estresar con 2×. Slippage adicional de 0.5 spread en salidas por stop.
- Partición: entrenamiento 2019–2022 y prueba 2023–2026, sin tocar la prueba hasta congelar parámetros. Además, walk-forward anual.
- **Presupuesto total de pruebas ≈ 40 configuraciones** (suma de las rejillas de abajo). Reportar todas, con DSR y PBO. Criterio de aprobación: Sharpe neto fuera de muestra > 0, t > 3 combinando el periodo completo, ganancia neta por trade > 0.5× costo, y estabilidad en vecinos de la rejilla (que no aprueba solo una celda aislada).
- Con $100 en la cuenta, el tamaño mínimo de contrato y el apalancamiento (2:1 en cripto, 20:1 en índices y oro, 30:1 en FX mayores según ESMA) pueden impedir dimensionar al 1% de riesgo. Hay que verificar los mínimos por instrumento **(NO VERIFICADO)**.

| # | Estrategia | Reglas base (según la publicación) | Rejilla (pequeña) | Instrumentos / sesión | Riesgo principal |
|---|---|---|---|---|---|
| **S1** | **Noise Area + VWAP** (Zarattini, Aziz y Barbon 2024) | Bandas σ(HH:MM) de N días desde max/min(Open, Close previo); evaluar cada K min; largo arriba / corto abajo; trailing = max(banda, VWAP de sesión); cierre al fin de sesión; tamaño por volatilidad objetivo, máximo 4x (reducir por la cuenta de $100) | N ∈ {14, 21} × VM ∈ {1.0, 1.5} × K ∈ {15, 30} min = **8** | US500 y US100, sesión NY 13:30–20:00 UTC (horario EE.UU.). Prueba de transferencia sin re-optimizar: XAU con la misma ventana | Sobreajuste del paper (autores vendedores de cursos); holding de horas, no scalping; muchos trades perdedores (37% de acierto); spread del CFD en la apertura de NY |
| **S2** | **ORB** (Zarattini y Aziz 2023) | Dirección = vela del rango inicial; entrada al cierre del rango; stop en el extremo opuesto; target nR o cierre de sesión; riesgo fijo por trade; filtro de rango mínimo | Duración del rango ∈ {5, 15} min × target ∈ {3R, 10R/fin de sesión} × filtro ∈ {ninguno, rango ≥ 4× spread} = **8** | US100 y US500 (apertura NY 13:30 UTC); EUR/USD y GBP/USD (apertura de Londres 07:00 UTC, sin fijar un horario "óptimo") | La replicación neta ≈ 0 ([MQL5](https://www.mql5.com/en/blogs/post/776235)); acierto de ~23% con rachas largas de pérdidas; slippage de stops en la apertura |
| **S3** | **Momentum de la última media hora** (Gao et al. 2018; Baltussen et al. 2021) | Señal = retorno del cierre previo de NY (20:00 UTC; ojo con el horario de verano) hasta T−30m; si es positiva, largo en T−30m→T; si es negativa, corto (Baltussen) o cash (Gao) | Señal ∈ {primera media hora, cierre previo→15:30 ET} × umbral ∈ {0, \|r\| > 0.5·σ de 20 días} = **4** | US500 y US100 (última media hora del cash de NY) | Pocos trades (~250 al año), bajo poder estadístico; decaimiento documentado ([Rosa 2022](https://ideas.repec.org/a/wly/jfutmk/v42y2022i12p2218-2234.html)); depende de la gamma de dealers, que no observamos |
| **S4** | **Reversión a VWAP con filtro de régimen** | z = (P − VWAP de sesión)/σ móvil de (P − VWAP); fade si \|z\| > k; salida en VWAP o tras T barras de 15m; stop en \|z\| > k+1.5; solo con régimen "rango" | k ∈ {2.0, 2.5} × T ∈ {4, 8} barras × filtro ∈ {ninguno, VR(15m, q=4) < 1 sobre los últimos 5 días} = **8** | EUR/USD y XAU (sesiones Londres y NY); control en US100. Con el GBP/USD a 1 bp, no vale la pena | Rebote bid-ask ilusorio (backtestear con bid/ask); días de tendencia o noticias (excluir ±15 min de datos macro de alto impacto); ganancia por trade cercana al costo |
| **S5** | **Fade de shocks horarios en cripto** (De Nicola 2021; Wen et al. 2022) | Si el retorno de 1h es mayor que k·σ de 1h (ventana de 30 días), operar en contra al cierre de la hora; salida tras H horas o con stop de 1·σ de 1h | k ∈ {2, 3} × H ∈ {1, 4} h × filtro de funding ∈ {apagado, funding de Binance en el decil extremo de 90 días} = **8** | BTC/USD y ETH/USD, 24/7 (comparar fin de semana contra días hábiles como diagnóstico, no como parámetro) | Spread de 5–10 bps; continuación en cascadas de liquidación (momentum tras saltos según Wen et al.); colas gordas; [Caporale et al.](https://bura.brunel.ac.uk/bitstream/2438/18238/5/FullText.pdf) lo encontraron no rentable |
| **S6** | **Control: estacionalidad 21–23 UTC en BTC** (Quantpedia) | Largo de 21:00 a 23:00 UTC todos los días | 1–2 configuraciones (todos los días / solo jueves y viernes) = **2** | BTC/USD | Casi con seguridad es un falso positivo por minería de datos y su ganancia bruta (~8 bps) es igual al costo. Sirve como **prueba de falsificación** del pipeline: si "aprueba" con costos realistas, hay que sospechar del backtest |

**Prioridad sugerida:** S1 > S3 > S2 > S4 > S5 > S6. Las tres primeras se concentran en US500 y US100, que son los instrumentos con mejor relación c/σ, y tienen respaldo académico. **Ninguna estrategia de 1–5 minutos pura entra en la lista**, porque la aritmética de la sección 2 y la evidencia de las secciones 1 y 4 indican que su valor esperado neto es negativo para una cuenta minorista que paga spread.
