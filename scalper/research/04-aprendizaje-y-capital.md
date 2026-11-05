# 04 — Aprender rápido sin sobreajustar, y manejo de capital agresivo pero vivo

Contexto: bot de scalping 24/7 en cuenta DEMO de Capital.com con $100 USD. Objetivo técnico: maximizar el crecimiento logarítmico **fuera de muestra** sin ruina. Todas las simulaciones son mías (numpy, scripts en `/tmp/claude-0/-home-user-README/82cdbbb4-ddee-5e71-af10-eeafa19fca7d/scratchpad/scripts/`: `mc_scalp.py`, `kelly_n.py`, `profiles.py`, `bandit.py`, `streaks.py`, `atr5.py`). Lo que no pude comprobar va marcado "(NO VERIFICADO)".

**Respuesta corta al sueño de $100 → $10,000 en una noche:** para que la *mediana* llegue a 100x en una noche hace falta un Sharpe diario de ≈3.0, es decir ≈48 anualizado si se repitiera. Ningún sistema publicado se acerca a eso. La única manera de tener alguna probabilidad es apostar todo, y entonces se convierte en una lotería: ~1–4% de tocar $10k contra ~95–100% de ruina. Por el teorema de muestreo opcional, con ventaja cero ninguna estrategia de apuestas puede tocar 100x antes de la ruina con probabilidad mayor a ~1%. Ver §B4.

---

## Parte A — Aprender rápido sin sobreajustar

### A1. Walk-forward (WF): anclado vs. móvil
- **Anclado (expanding):** el entrenamiento siempre empieza en t0 y va creciendo. Tiene más datos y menos varianza, pero se adapta lento a cambios de régimen.
- **Móvil (rolling):** ventana fija que se desliza. Se adapta mejor y tiene más varianza. La skill instalada `walk-forward-validation` sugiere para scalping de 1–5 min: train 3–7 días, test 1 día, embargo 2–4 h (`~/.claude/plugins/cache/agiprolabs-claude-trading-skills/trading-skills/1.0.0/skills/walk-forward-validation/SKILL.md`). Mi opinión es que 3–7 días es poco para estimar ventajas de 0.1R (ver A4). Prefiero entrenar en 4–8 semanas y probar en 1 semana, y comparar contra anclado como control.
- **Métrica de Pardo:** Walk-Forward Efficiency = rendimiento OOS anualizado / rendimiento IS anualizado. La skill `backtest-expert` (`/home/user/README/.claude/skills/backtest-expert/SKILL.md`) marca como alerta un OOS menor al 50% del IS, parámetros que cambian mucho entre ventanas o la necesidad de re-optimizar seguido. Pardo, *The Evaluation and Optimization of Trading Strategies*, Wiley 2008 (umbral exacto de WFE: NO VERIFICADO).
- **Regla de la skill backtest-expert que sí aplica:** busca mesetas, no picos. Prueba el stop al 50–150% del valor base, el slippage a 1.5–2x y los fills en el peor caso, y exige al menos 100 trades (200+ para tener confianza).

### A2. CV purgada y con embargo; CSCV/PBO; DSR; MinTRL; Reality Check/SPA
- **Purged k-fold + embargo** (López de Prado, *Advances in Financial Machine Learning*, Wiley 2018, cap. 7): se eliminan del train las observaciones cuya etiqueta se traslapa en el tiempo con el test, y se agrega un hueco (embargo) después del test. Para un scalper con salidas de hasta N velas, purga = N velas y embargo ≥ 2N. **CPCV** (cap. 12) genera C(N,k) caminos OOS.
- **PBO vía CSCV** ([Bailey, Borwein, López de Prado y Zhu, "The Probability of Backtest Overfitting", J. Computational Finance 2017, SSRN 2326253](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253)). Se parte la matriz de rendimientos (T×K configuraciones) en S bloques (p. ej. S=16) y se forman todas las mitades IS/OOS. En cada una se elige la mejor configuración IS y se registra su rango OOS. PBO = fracción de casos en que la mejor IS queda por debajo de la mediana OOS. **Criterio:** PBO > 0.5 se descarta; para operar quiero PBO < 0.2.
- **Deflated Sharpe Ratio** ([Bailey y López de Prado, J. Portfolio Mgmt 2014, SSRN 2460551](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551)). Corrige por el número de pruebas K, por la asimetría y la curtosis, y por la longitud T. DSR = Φ( (SR̂ − SR₀)·√(T−1) / √(1 − γ₃SR̂ + (γ₄−1)/4·SR̂²) ), con SR₀ = √Var(SR_k)·[(1−γ)Φ⁻¹(1−1/K) + γΦ⁻¹(1−1/(Ke))]. **Ojo:** el código de la skill instalada omite el factor √Var(SR_k) y mezcla SR anualizado con T en observaciones. Hay que usar SR por trade con T en trades y pasar curtosis *total* (3 = normal). **Criterio:** DSR ≥ 0.95, contando *todas* las variantes probadas en K, también las descartadas.
- **Minimum Track Record Length** ([Bailey y López de Prado, "The Sharpe Ratio Efficient Frontier", J. Risk 2012, SSRN 1821643](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1821643)): MinTRL = 1 + [1 − γ₃SR + (γ₄−1)/4·SR²]·(z_α/(SR − SR*))². Ejemplo: SR por trade = 0.10, γ₃ = −0.3 (el scalping suele tener sesgo negativo), γ₄ = 5, SR* = 0, z = 1.645 da **≈282 trades**. La relación con el número de pruebas está en [Bailey et al., "Pseudo-Mathematics and Financial Charlatanism", Notices AMS 2014](https://www.ams.org/notices/201405/rnoti-p458.pdf): con pocos años de datos basta probar unas cuantas decenas de variantes para "encontrar" un SR alto por puro azar.
- **White's Reality Check** ([White 2000, Econometrica 68(5)](https://doi.org/10.1111/1468-0262.00152)) y **Hansen SPA** ([Hansen 2005, JBES 23(4)](https://doi.org/10.1198/073500105000000063)) prueban con bootstrap estacionario si *la mejor* de K reglas supera al benchmark (aquí, no operar = 0R) una vez descontado el data-snooping. SPA es más potente porque estudentiza y no se diluye con reglas malas. Úsalo como prueba final del conjunto de candidatos. Para series de trades, usa bloques de un día de trades.
- **Vara de t-stat:** [Harvey, Liu y Zhu, RFS 2016](https://doi.org/10.1093/rfs/hhv059) piden t > 3 en hallazgos nuevos. [Harvey y Liu, "Backtesting", JPM 2015](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2345489) proponen recortar el Sharpe por pruebas múltiples, a menudo cerca de un 50%.

### A3. Bandits para asignar entre estrategias ya validadas
- **Thompson sampling** ([Russo et al., "A Tutorial on Thompson Sampling", 2018](https://arxiv.org/abs/1707.02038); garantías en [Agrawal y Goyal 2012](https://arxiv.org/abs/1111.1797)).
  - *Beta-Bernoulli* (gana/pierde): **no lo recomiendo**. Ignora el tamaño de la ganancia y castiga a una estrategia de 45% de acierto con pago 1.5R que en realidad es mejor.
  - *Gaussiano sobre R-múltiplos* (Normal con σ≈1.1R conocida, o Normal-Gamma si σ se desconoce) maximiza directamente la expectativa por trade, que es lo que importa.
- **No estacionariedad:** Discounted TS ([Raj y Kalyani 2017](https://arxiv.org/abs/1707.09727)), Sliding-Window TS ([Trovò, Paladino, Restelli y Gatti, JAIR 68, 2020](https://jair.org/index.php/jair/article/view/11407)), D-UCB/SW-UCB ([Garivier y Moulines 2011](https://arxiv.org/abs/0805.3415)). UCB1 clásico: [Auer, Cesa-Bianchi y Fischer 2002](https://doi.org/10.1023/A:1013689704352).
- **Aplicaciones a portafolios:** [Huo y Fu 2017, Royal Society Open Science](https://doi.org/10.1098/rsos.171377) (bandit con aversión al riesgo); Shen et al., "Portfolio Choices with Orthogonal Bandit Learning", IJCAI 2015 (NO VERIFICADO el enlace).
- **Mi simulación (`bandit.py`):** 4 estrategias con E = +0.10, +0.05, 0, −0.10 R y σ = 1.1. En t = 1500 el régimen se invierte (la mejor pasa a ser la peor). 300 réplicas.

| TS gaussiano | % jugadas en la mejor, t<200 | 200–1500 | 1500–1700 (tras el cambio) | 1700–3000 | R total (oráculo 300, uniforme 38) |
|---|---|---|---|---|---|
| sin descuento | 33% | 55% | **4%** | 18% | 90 |
| γ = 0.995 (memoria ≈200 trades) | 32% | 39% | 23% | 38% | **107** |
| γ = 0.98 (memoria ≈50) | 29% | 31% | 28% | 31% | 74 |

**Lectura:** con ventajas de 0.1R y ruido de 1R, el bandit aprende *despacio*. Después de 1,500 trades solo pone el 55% de las jugadas en la mejor. Sirve para **apagar lo que claramente se rompió y reasignar presupuesto de riesgo**, no para afinar. Un descuento de γ≈0.995 es el mejor compromiso.
- **Cómo combinarlos:**
  1. *Offline:* generar candidatos (registrando K) → WF + purga/embargo → PBO < 0.2, DSR ≥ 0.95, SPA p < 0.05, costos ×1.5–2.
  2. *Online:* solo entran al bandit las estrategias que pasan. Cada brazo es una (estrategia × instrumento) y recibe una fracción del **presupuesto de riesgo** (no una de cada trade), con piso de 10% por brazo para que siga aprendiendo y tope de 50%.
  3. Los parámetros **no se tocan online**. Se re-optimizan en el WF programado (p. ej. semanal) y cada set nuevo suma a K.

### A4. Tamaños de muestra mínimos
Para detectar que la ventaja μ es distinta de 0: n ≈ (z·σ/μ)². Con potencia 80%: n ≈ ((z_α + z_β)·σ/μ)². Para comparar dos variantes con diferencia Δ: n por brazo ≈ 2((z_α+z_β)σ/Δ)². σ = 1R, 40 trades por noche.

| Ventaja μ | n (2 colas, 95%) | n (1 cola, 95%) | n (1 cola + potencia 80%) | Noches a 40 tr/noche (1 cola) | n por brazo para comparar 2 variantes (Δ=μ) |
|---|---|---|---|---|---|
| 0.05R | 1,537 | 1,082 | 2,473 | 27 | 6,279 |
| 0.10R | 384 | 271 | 618 | 7 | 1,570 |
| 0.20R | 96 | 68 | 155 | 1.7 | 392 |
| 0.30R | 43 | 30 | 69 | 0.8 | 174 |

**Reglas operativas que propongo:**
- **Antes de cambiar un parámetro:** no hacerlo con datos en vivo. Distinguir dos variantes que difieren 0.1R toma ~1,570 trades por variante, así que eso se decide en backtest/WF con miles de trades. En vivo solo se cambia en la re-optimización programada.
- **Antes de cortar una estrategia:** corte secuencial contra lo que prometió el backtest. Se rechaza μ = μ_bt si la media observada cae por debajo de μ_bt − 1.645·σ/√n. Con μ_bt = 0.10R y σ = 1.1:

  | n | 30 | 50 | 100 | 200 | 400 |
  |---|---|---|---|---|---|
  | Media mínima (R) | −0.23 | −0.16 | −0.08 | −0.03 | +0.01 |
  | R acumulado mínimo | −6.9 | −7.8 | −8.1 | −5.6 | +3.8 |

  Si queda por debajo, se pasa a tamaño mínimo y a revisión. Además, corte duro si el drawdown supera 2x el máximo DD del WF.
- **Antes de subir el tamaño:** que el límite inferior de confianza de μ sea mayor que 0, o sea n ≥ (1.645σ/μ̂)² (~270 trades si μ̂ ≈ 0.1R), y dimensionar con ¼ de Kelly calculado sobre ese límite inferior, no sobre μ̂. La skill `kelly-criterion` pide lo mismo: 50 trades como mínimo para cualquier Kelly, 100+ para medio Kelly, 200+ para fracciones agresivas, y el límite inferior de Wilson para el win rate.

---

## Parte B — Manejo de capital agresivo pero vivo

### B1. Kelly, Kelly fraccional y error de estimación
- **Kelly** ([Kelly 1956](https://doi.org/10.1002/j.1538-7305.1956.tb03809.x)): forma binaria f* = p − q/b. Forma continua f* ≈ μ/σ², con crecimiento máximo g* ≈ μ²/(2σ²) por trade. [Thorp 2006](https://www.edwardothorp.com/wp-content/uploads/2016/11/TheKellyCriterionAndTheStockMarket.pdf) (enlace NO VERIFICADO) y [MacLean, Thorp y Ziemba, Quantitative Finance 2010](https://doi.org/10.1080/14697688.2010.506108) muestran lo siguiente:
  - Una fracción c·f* crece a (2c − c²)·g*: medio Kelly da 75% del crecimiento y ¼ Kelly da 44%.
  - La probabilidad de llegar a caer a una fracción x del capital es x^(2/c − 1). Con Kelly completo, P(caer a la mitad) = 50%; con medio Kelly, 12.5%.
  - Apostar 2·f* da crecimiento ≈ 0. Ver también [MacLean, Ziemba y Blazenko 1992](https://doi.org/10.1287/mnsc.38.11.1562) (crecimiento vs. seguridad).
- **Kelly exacto de mi modelo de trade** (p = 0.52; pérdida −1R el 97% de las veces y −2.5R el 3% por gaps/slippage):

| E neta | f* (Kelly) | ½ Kelly | ¼ Kelly | Multiplicador por noche (40 tr) a Kelly completo | a ½ Kelly |
|---|---|---|---|---|---|
| 0.02R | 1.9% | 1.0% | 0.5% | 1.007x | 1.006x |
| 0.05R | 4.4% | 2.2% | 1.1% | 1.045x | 1.033x |
| 0.10R | 8.0% | 4.0% | 2.0% | 1.17x | 1.13x |
| 0.15R | 11.0% | 5.5% | 2.8% | 1.39x | 1.28x |

- **Error de estimación:** [Chopra y Ziemba 1993](https://doi.org/10.3905/jpm.1993.409440) encuentran que los errores en las medias pesan ~10x más que los de las varianzas. [Baker y McHale 2013, Decision Analysis](https://doi.org/10.1287/deca.2013.0271) proponen encoger el Kelly por la incertidumbre. Mi simulación: μ real = 0.05R y se apuesta Kelly sobre el μ̂ estimado.

| Trades usados para estimar | Kelly completo: g medio | ½ K | ¼ K | Óptimo |
|---|---|---|---|---|
| 50 | **−0.0044** (pierde) | −0.0002 | +0.0004 | 0.0010 |
| 200 | −0.0006 | +0.0005 | +0.0005 | 0.0010 |
| 1000 | +0.0006 | +0.0007 | +0.0004 | 0.0010 |

**Conclusión:** con menos de ~500 trades, ¼ de Kelly le gana a Kelly completo y empata o le gana a medio Kelly. Con la ventaja típica sin confirmar, ¼ Kelly equivale a **≈1% por trade**.

### B2. Riesgo de ruina
Aproximación de difusión con horizonte infinito: P(tocar b·capital inicial) = b^(2m/s²), donde m y s² son la media y la varianza de log(1 + f·r). Con E = 0 o negativa, la ruina a largo plazo es prácticamente segura con cualquier f > 0.

| f por trade | E = 0.05R: P(−50%) | P(−80%, ≈$20) | E = 0.10R: P(−50%) | P(−80%) |
|---|---|---|---|---|
| 0.5% | ≈0 | ≈0 | ≈0 | ≈0 |
| 1% | 0.5% | 4e−6 | ≈0 | ≈0 |
| 2% | 9.6% | 0.4% | 0.8% | 1e−5 |
| 3% | 27% | 4.6% | 4.9% | 0.09% |
| 5% | 60% | 30% | 22% | 2.9% |
| 10% | ruina segura (g<0) | — | 66% | 39% |

### B3. Monte Carlo: $100, 40 trades/noche, riesgo fijo sobre el capital actual, ruina si < $20
Semana = 7 días (280 trades, cripto 24/7) y mes = 30 días (1,200 trades); sin frenos. 20k caminos (10k para horizontes largos). Completo en `scripts/mc_scalp.py` (salida `mc_main.txt`). Extracto con mediana [p10–p90], P(−50%) y P(ruina):

**E = 0R (lo realista sin ventaja demostrada):**

| Riesgo | 1 noche | 1 semana | 1 mes | P(−50%) al mes | P(ruina) al mes |
|---|---|---|---|---|---|
| 0.5% | 99.8 | 99.6 [89–111] | 98.4 [79–123] | 0% | 0% |
| 1% | 99.5 | 98.7 [79–123] | 93.7 [59–147] | 3.8% | 0% |
| 2% | 98.6 | 93.8 [60–145] | 78 [32–195] | 27% | 4.6% |
| 5% | 93.5 | 69 [20–210] | 19.8 | 74% | 67% |
| 10% | 78 | 19.6 | 19 | 97% | 97% |
| 20% | 37 | 18 | 18 | 100% | 100% |

**E = +0.05R:**

| Riesgo | 1 noche | 1 semana | 1 mes [p10–p90] | P(−50%) al mes | P(ruina) al mes | P(≥$10k) al mes |
|---|---|---|---|---|---|---|
| 0.5% | 100.8 | 107 | 133 [105–169] | 0% | 0% | 0 |
| 1% | 101.6 | 114 | 172 [106–273] | 0% | 0% | 0 |
| 2% | 102.6 | 125 | 252 [97–644] | 1.5% | 0.1% | 0 |
| 3% | 103.2 | 133 | 332 [80–1,389] | 4.8% | 1.9% | 0.1% |
| 5% | 102.9 | 133 | 319 [20–3,858] | 22% | 19% | 3.4% |
| 10% | 93.5 | 61 | 19 | 74% | 73% | 5.7% |
| 20% | 54 | 18 | 18 | 99.5% | 99.5% | 0.2% |

**E = +0.10R** (ya es una ventaja muy buena para scalping retail). Mes: 1% → 307 [186–501]; 2% → 808 [305–2,188]; 3% → 1,856 [426–8,451] con 7.6% de probabilidad de llegar a ≥$10k; 5% → 6,248 [456–73,176] con 40% de ≥$10k y 2.9% de ruina; 10% → mediana 3,784 con 33% de ruina. **E = −0.05R:** a 2% la ruina del mes es 47% y a 3%, 83%.

**P(tocar $10,000 en UNA noche)** (200k caminos, `mc_night.txt`):

| Riesgo | E=0.10, 20 tr | E=0.10, 40 tr | E=0.10, 60 tr | E=0.15, 60 tr | P(ruina) esa noche (E=0.10, 40 tr) |
|---|---|---|---|---|---|
| ≤10% | 0 | 0 | 0 | 0 | ≤1.2% |
| 20% | 0 | 0.03% | 0.4% | 1.1% | 28% |
| 50% | 0.7% | 2.2% | 2.7% | 4.4% | 92% |
| "All-in" 100% (una pérdida = cero) | 1.9% | 2.0% | 2.0% | 2.0% | 100% (si no se detiene en $10k) |

"All-in" equivale a ganar ~6 volados seguidos (0.52⁶ ≈ 2%). Con E = 0 el all-in da ~1%, que es el límite teórico.

### B4. Qué ventaja haría falta para una mediana de 100x en una noche
Con Kelly completo, g* ≈ μ²/(2σ²) por trade. Para ln(100) = 4.605 en n trades hace falta μ/σ ≥ √(2·4.605/n):

| Trades/noche | Ventaja necesaria por trade (σ=1R) | f* (riesgo por trade) |
|---|---|---|
| 20 | 0.68R | 68% |
| 40 | 0.48R (p. ej. ganar 74% a 1:1, neto de costos) | 48% |
| 60 | 0.39R | 39% |
| 200 | 0.21R | 21% |

Sin importar n, eso exige un **Sharpe diario ≈ √(2·ln100) = 3.03**, unas **48 veces al año** (×√252). Lo publicado va en sentido contrario:
- [Capital.com: "80.96% of retail investor accounts lose money when trading CFDs with this provider"](https://capital.com/en-int/markets/indices/us-500-index-1) (aviso en sus páginas, consultado 2026-11-05).
- [Chague, De-Losso y Giovannetti, "Day Trading for a Living?"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101): 97% de quienes persistieron más de 300 días perdieron y solo el 1.1% ganó más que el salario mínimo.
- [Barber, Lee, Liu y Odean, J. Financial Markets 2014](https://doi.org/10.1016/j.finmar.2013.05.006): menos del 1% de los day traders es predeciblemente rentable.
- Un Sharpe anual de 2–3 ya se considera excepcional en fondos cuantitativos (NO VERIFICADO como cifra general).

Además, con E ≤ 0 la riqueza es una supermartingala. Por el teorema de muestreo opcional, P(llegar a $10k antes que a $0) ≤ 100/10,000 = 1% *con cualquier esquema de apuestas*. Esa es la cota dura del sueño.

### B5. Restricción práctica en Capital.com: tamaños mínimos, spread y apalancamiento
Fuentes:
- Páginas de mercado de Capital.com (entidad internacional "en-int", consultadas 2026-11-05): ["Min traded quantity", spread y margen](https://capital.com/en-int/markets/indices/us-tech-100-index-1).
- [Especificación MT5 de Capital.com (PDF)](https://img.capital.com/docs/MT5-contract-specification-1-.pdf).
- ATR(14) de 5 min, calculado por mí:
  - BTC, ETH y oro: Binance 1m, ago–oct 2026. El oro va con PAXG como proxy.
  - US100, US500, oro y FX: Yahoo 5m, últimos 30 días. NQ=F, ES=F y GC=F son futuros y sirven de proxy del CFD.
- La API real expone `dealingRules.minDealSize` por epic (ver la documentación pública de la API). **El bot debe leerlo al arrancar**, porque puede diferir de la web (NO VERIFICADO que coincida).

| Instrumento | Mín. (web) | ATR 5m mediana (13–20 UTC) | $ en riesgo al mínimo con stop de 1 ATR | Spread publicado | **Spread en R (stop = 1 ATR)** | Margen en-int → riesgo máx. con stop de 1 ATR | Con apalancamiento ESMA |
|---|---|---|---|---|---|---|---|
| BTCUSD | 0.0001 BTC | $82 ($109) | $0.008 | 50 | **0.61R** (0.46) | 5% → 2.1% | 1:2 → 0.2% |
| ETHUSD | 0.001 ETH | $3.6 ($4.8) | $0.004 | 1.75 | **0.49R** (0.37) | 5% → 2.9% | 1:2 → 0.3% |
| GOLD (spot) | 0.01 oz | $2.5–3.7 | $0.03 | 0.5 | 0.13–0.20R | 1% → ~7% | 1:20 → 1.4% |
| US100 | 0.001 | 26 pts (37) | $0.026 | 1.8 | **0.07R** (0.05) | 1% → 8.7% | 1:20 → 1.7% |
| US500 | 0.01 | 3.9 pts (6.1) | $0.039 | 0.6 | 0.15R (0.10) | 1% → 5% | 1:20 → 1.0% |
| EURUSD | 100 unidades | 2.3 pips (2.7) | $0.023 | 0.7 pip | **0.31R** (0.26) | 1% → 2.0% | 1:30 → 0.6% |
| GBPUSD | 100 unidades | 2.6 pips (3.3) | $0.026 | 1.3 pip | **0.49R** (0.39) | 1% → 2.0% | 1:30 → 0.6% |

Cómo se calculan las dos últimas columnas: con riesgo r y stop de k·ATR, nocional/capital = r·Precio/(k·ATR), y el riesgo máximo es apalancamiento máx. × k·ATR/Precio. La tabla supone que una unidad de CFD equivale a $1 por punto o a una unidad del subyacente (NO VERIFICADO para cada instrumento). La entidad que aplique a una cuenta mexicana y su apalancamiento demo: NO VERIFICADO; en la página EU el margen de BTC es 50%.

**Qué implica:**
1. **El tamaño mínimo NO es la restricción** en la plataforma nativa o la API: con $100 se puede arriesgar 0.5% ($0.50) en todo. La excepción es **el oro en MT5**: el mínimo de 0.01 lote es 1 oz, unos $3 por ATR, o sea ~3% de $100. Ahí no es operable con riesgo correcto. BTC en MT5 cuesta ~0.8% por ATR.
2. **El verdadero asesino es el spread medido en R.** Un scalper de 5 min con stop de 1 ATR paga 0.3–0.6R por trade en BTC, ETH, EURUSD y GBPUSD. Eso es más que cualquier ventaja plausible (0–0.15R): **esos instrumentos no son operables a 5 min con stops de 1 ATR**. Se necesitan stops/targets de ≥3 ATR o velas de 15 min o más, para bajar el spread a menos de 0.1R. **US100** es el más barato (0.05–0.07R), seguido de US500 y oro (0.1–0.2R).
3. **El apalancamiento limita el riesgo con stops ajustados.** Con reglas tipo ESMA, el riesgo con stop de 1 ATR no puede pasar de 0.2–1.7%, y en cripto 1:2 el scalping es prácticamente imposible. Con márgenes "en-int" el límite es 2–9%. El "all-in con apalancamiento máximo" en US100 a 1:100 con stop de 1 ATR equivale a ~8.7% de riesgo por trade, y un gap de 10 ATR borra la cuenta. La protección contra saldo negativo existe en el retail regulado (NO VERIFICADO para la entidad de la cuenta).

### B6. Stop diario y breakers por rachas: justificación
- **Con trades independientes, un freno no cambia la expectativa por trade, solo reduce la cantidad de trades.** En mi MC (`profiles.py`) con un stop diario de −6R y breaker de 7 pérdidas, al 2%:
  - E = +0.10: la mediana mensual baja de 824 a 639.
  - E = −0.05: la ruina mensual baja de 47% a 25%.
  - **El freno protege justo cuando la ventaja es negativa**, que es el caso probable al inicio.
- **Su valor real está en lo que el MC iid no modela:** cambio de régimen, autocorrelación de pérdidas, bugs, desconexiones y datos malos. [Knight Capital perdió ~$460M en 45 minutos por un despliegue defectuoso (SEC 2013)](https://www.sec.gov/litigation/admin/2013/34-70694.pdf). En humanos, [Coval y Shumway 2005, J. Finance](https://doi.org/10.1111/j.1540-6261.2005.00721.x) muestran que los traders que pierden en la mañana toman más riesgo en la tarde. A un bot no le pasa, salvo que lo programes con martingala.
- **Calibrar el breaker contra el azar** (q = 0.48, `streaks.py`):

  | Racha de pérdidas | P en una noche de 40 trades | P en una semana de 280 trades |
  |---|---|---|
  | ≥5 | 41% | 98% |
  | ≥6 | 21% | 84% |
  | ≥7 | 10% | 58% |
  | ≥8 | 4.9% | 33% |
  | ≥10 | 1.1% | 8.8% |

  **Un breaker en 5–6 pérdidas se dispara solo por ruido.** Recomiendo: a 7 pérdidas, pausa de 1–2 h y tamaño a la mitad; a 10 pérdidas, alto del día y alerta de "posible rotura o bug".
- La skill `risk-management` sugiere un stop diario de −3/−4/−5% y −10% semanal. Con 40 trades al 1%, la σ diaria de la cuenta es ≈6.8%, así que un −4% se tocaría casi a diario. **Hay que expresar el stop en R**: −6R toca el 24–42% de los días en mi MC. Un **−8R** frenaría menos y seguiría cortando los días de cola (NO VERIFICADO por simulación con −8R; extrapolado).

---

## Perfiles recomendados

| Perfil | Riesgo/trade | Riesgo abierto máx. | Stop diario | Breaker | Stop semanal | P(ruina <$20) en 30 días | P(−50%) en 30 días |
|---|---|---|---|---|---|---|---|
| **Arranque** (primeros ~300 trades, ventaja sin medir) | 0.5% | 1.5% | −6R (−3%) | 7 pérdidas → pausa 2 h, ½ tamaño; 10 → alto del día | −15R | 0% en todos los E simulados (−0.05…+0.10) | 0.1% si E = −0.05 |
| **Normal** (tras pasar la regla de A4) | 1% (≈¼ Kelly con E≈0.05–0.10) | 3% (correlacionados cuentan como uno) | −6R (−6%) | igual | −15R → revisión | 0% (E ≥ 0); <0.1% (E = −0.05) | 28% si E = −0.05; 2% si E = 0; ≈0 si E ≥ 0.05 |
| **Agresivo** (solo con ≥500 trades y E confirmada ≥0.08R por límite inferior) | 2% (≈¼ Kelly con E = 0.10; ½ Kelly con E = 0.05) | 5% | −6R (−12%) | igual | −12R | 0% (E ≥ 0.05); 2.1% (E = 0); **25% (E = −0.05)** | 22% (E = 0); 80% (E = −0.05) |
| ~~Lotería~~ (all-in o ≥20%) | — | — | — | — | — | 90–100% en una noche | — |

**Tabla de expectativas** (40 trades/día, con frenos; mediana [p10–p90] del capital partiendo de $100):

| Perfil / ventaja | 1 día | 1 semana (7 d) | 1 mes (30 d) | P(−50%) en 1 mes |
|---|---|---|---|---|
| Arranque 0.5%, E = 0 | 99.6 [96.8–103.8] | 99.6 [90–110] | 98.5 [81–122] | 0% |
| Arranque 0.5%, E = +0.05 | 100.6 [96.7–105.1] | 105.6 [95–119] | 127 [102–162] | 0% |
| Normal 1%, E = 0 | 99.1 [93.6–108.2] | 98.3 [81–121] | 94 [63–144] | 2.0% |
| Normal 1%, E = +0.05 | 101.0 [93.5–112.0] | 110.8 [89–140] | 158 [100–252] | 0.1% |
| Normal 1%, E = +0.10 | 103.6 [93.7–114.7] | 126 [99–161] | 269 [163–443] | 0% |
| Agresivo 2%, E = 0 | 98.6 [87–115] | 93.9 [65–142] | 80 [36–184] | 22% |
| Agresivo 2%, E = +0.05 | 102.6 [87–125] | 120.5 [78–191] | 221 [91–565] | 1.6% |
| Agresivo 2%, E = +0.10 | 106.8 [88–131] | 154 [96–251] | 639 [237–1,761] | 0% |
| Agresivo 2%, E = −0.05 | 94.2 [87–110] | 75 [54–109] | 31 [20–66] | 80% |

En el mejor caso honesto (E = +0.10R confirmada, agresivo), la mediana necesita ~3–4 meses para $100 → $10k, no una noche. Eso además supone ventaja estable, sin degradación por capacidad y con spreads como los publicados. Lo más probable es que la ventaja real sea ≤0 hasta demostrar lo contrario, y para eso sirve la demo: **medirla con ≥300 trades al 0.5%** antes de pasar a "normal".
