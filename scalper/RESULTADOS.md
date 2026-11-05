# RESULTADOS — Etapa 2: laboratorio de backtesting

Todo se puede reproducir con `python -I lab/run_wf.py`, `lab/info_agents.py`, `lab/expectativa.py` y
`lab/export_backtest.py`. Los resultados quedan en `lab/results/`.

## Datos

| Instrumento | Fuente | Periodo | Velas de 1 min |
|---|---|---|---|
| US100, US500, GOLD, EURUSD, GBPUSD | HistData.com (NSXUSD, SPXUSD, XAUUSD…) | ene-2021 → oct-2026 (5.8 años) | ~1.9–2.1 millones c/u |
| BTCUSD, ETHUSD | data.binance.vision (spot BTCUSDT/ETHUSDT) | nov-2021 → oct-2026 (5.0 años) | ~2.6 millones c/u |

**Error que encontré y corregí:** HistData dice que sus horas vienen en "EST sin horario de verano", pero
comparándolas minuto a minuto contra Dukascopy (que usa UTC) en enero, julio y octubre de 2026, los precios
**solo coinciden exactos (99.6% de los minutos) si se leen como hora de Nueva York con horario de verano**.
Si no se corrige, cada estrategia que depende de la apertura de las 9:30 queda una hora corrida durante
medio año. La corrección está en `lab/data.py`.

## Costos modelados (pesimistas a propósito)

- **Spread:** el publicado por Capital.com × la ampliación por franja (Asia ×1.5–2, fuera del contado ×1.5,
  rollover ×2) **× 1.25**. La prueba de estrés usa **× 2.0**.
- **Entradas:** al abrir la vela de 1 min siguiente a la señal, pagando medio spread.
- **Stops:** se revisan contra el bid (largos) o el ask (cortos) de cada minuto. Si el stop y el objetivo caen
  en el mismo minuto, cuenta como stop. Cada stop paga además **0.5× spread de deslizamiento**, y un gap se
  llena en la apertura.
- **Funding nocturno:** el bot cierra todo antes del rollover (16:40 NY), así que no lo paga. Ningún trade del
  backtest cruza esa hora.
- **Comisión:** Capital.com no cobra; todo el costo es spread.

## Validación

- **Walk-forward anclado:** se entrena con todo lo anterior (mínimo 12 meses) y se prueba en los 6 meses
  siguientes. En cada tramo se elige la mejor configuración del entrenamiento, y si ninguna gana ahí, el tramo
  no opera. Los números "OOS" son la suma de los tramos de prueba que el modelo no vio: 2022-01 → 2026-10.
- **Más filtros:**
  - Deflated Sharpe Ratio (DSR) con todas las variantes probadas.
  - "Meseta": fracción de configuraciones con expectativa positiva.
  - Estrés con 2× spread.
  - Evaluación con la skill **backtest-expert** (`decision`), con R expresado como % de la cuenta a 1% de
    riesgo por trade.
- Pasan al bot solo las estrategias con **Deploy o Refine** que además siguen positivas con 2× spread.

## Ranking (E = expectativa por trade en R, neta de costos)

| Estrategia | Instrumento | Variantes | E en muestra (mejor) | Costo/trade | Trades OOS | Win % OOS | **E OOS** | t | PF | Sharpe | DD a 1% | E con 2× spread | DSR | Meseta | backtest-expert | **Veredicto** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **S1 Noise Area + VWAP** | **US100** | 64 | +0.136 | 0.035R | **834** | 38% | **+0.103** | 2.18 | 1.24 | 1.53 | 21% | **+0.084** | 0.69 | 98% | REFINE (67/100) | **✅ Pasa (Refine)** |
| S1 Noise Area + VWAP | US500 | 64 | +0.039 | 0.066R | 1115 | 35% | +0.008 | 0.19 | 1.02 | 0.12 | 46% | −0.027 | 0.05 | 23% | REFINE | ❌ no aguanta 2× spread |
| S2 Opening Range Breakout | US100 | 24 | +0.040 | 0.040R | 908 | 31% | +0.017 | 0.26 | 1.03 | 0.14 | 40% | −0.004 | 0.18 | 12% | REFINE | ❌ no aguanta 2× spread |
| S2 Opening Range Breakout | US500 | 24 | +0.048 | 0.081R | 1062 | 31% | +0.015 | 0.24 | 1.02 | 0.12 | 54% | −0.027 | 0.20 | 17% | REJECT | ❌ |
| S2 ORB Londres | EURUSD | 24 | −0.074 | 0.101R | 0 | — | — | — | — | — | — | — | — | 0% | — | ❌ nunca positiva |
| S3 Media hora final | US100 / US500 | 16 c/u | −0.043 / −0.082 | 0.06–0.11R | 0 | — | — | — | — | — | — | — | — | 0% | — | ❌ |
| S4 Reversión a VWAP | EURUSD / GOLD / US100 | 32 c/u | −0.13 / −0.19 / −0.17 | 0.16–0.19R | 0 | — | — | — | — | — | — | — | — | 0% | — | ❌ |
| S5 Contra-movimiento cripto | BTC / ETH | 32 c/u | −0.096 / −0.092 | 0.06–0.08R | 0 | — | — | — | — | — | — | — | — | 0% | — | ❌ |
| S6 Control estacionalidad BTC | BTC | 4 | −0.154 | 0.18R | 0 | — | — | — | — | — | — | — | — | — | — | ✅ pierde (como debe un control) |
| **S0 Scalping puro (breakout 5 min)** | los 7 | 8 c/u | **−0.15 a −0.22** | **0.15–0.25R** | 0 | — | — | — | — | — | — | — | — | 0% | — | ❌ **el spread se lo come todo** |

GBPUSD no opera porque la investigación lo dejó fuera de la rotación por su spread.

### Cómo leerlo

1. **El scalping clásico de 5 minutos pierde en los 7 instrumentos.** El costo por trade (0.15–0.25R) es casi
   igual a la pérdida (−0.15 a −0.22R): el spread se come todo el movimiento. Eso confirma lo que encontró la
   investigación.
2. **Sobrevive una sola estrategia: S1 en US100.**
   - Es la de la literatura con mejor relación ganancia/spread.
   - El walk-forward **eligió la misma configuración en los 10 tramos** (m = 1.25, revisión cada 30 min, stop de
     2 ATR, salida publicada). Es señal de estabilidad, no de casualidad.
   - **63 de 64 variantes** ganan en el periodo completo: es una meseta, no un pico.
3. **Por qué es "Refine" y no "Deploy":**
   - El DSR de 0.69 no llega al 0.95 que pide la investigación. Con 64 variantes probadas, hay ~31% de
     probabilidad de que la ventaja real sea cero.
   - **La ventaja se está achicando.** Expectativa OOS por año: 2022 +0.17R · 2023 +0.13R · 2024 +0.15R ·
     **2025 +0.03R · 2026 +0.04R**. El paper se publicó en 2024, y esa caída encaja con lo que McLean y Pontiff
     documentan sobre estrategias publicadas.
   - Por eso el bot la corre a riesgo de arranque, el Learner la vigila y el reporte compara siempre contra la
     cifra de 2025–26, no solo contra la de todo el periodo.

## "Mover pronto" contra "dejar respirar" (S1-US100, promedio de las 32 variantes)

| Salida | E por trade | Trades que terminan en ganancia o en cero |
|---|---|---|
| **Salida publicada sin mover el stop ("fijo")** | **+0.088R** | 38% |
| Break-even a +1.5 ATR | +0.076R | 49% |
| Break-even a +1.0 ATR | +0.064R | 56% |
| Break-even a +1.0 ATR + trailing de 2 ATR | +0.036R | 57% |
| Stop de servidor que sigue max(banda, VWAP) cada 5 min | +0.038R | 31% |
| … + break-even a 1.0 | +0.030R | 43% |

**Conclusión:** mover pronto sí aumenta los trades que terminan en cero o en ganancia (de 38% a 56–57%),
pero **baja la ganancia total entre 14% y 60%**: el ruido normal saca trades que iban a ganar. Siguiendo tu
regla ("prioriza el resultado total"), el Stop Manager usa la política **"fijo"** en S1. Sigue vigilando
cada minuto y confirma que el stop esté en el servidor, pero no lo mueve. Si algún día prefieres más trades
en cero a cambio de menos ganancia, en `config.yaml` puedes cambiar `politica_stop: be1.5`; con eso pierdes
~14% de la expectativa.

El cierre parcial queda apagado por dos razones: la API de Capital.com no lo permite (`DELETE /positions`
no acepta tamaño) y matemáticamente nunca supera a la mejor de sus dos mitades (investigación, cap. 05).

## Agentes de información (filtros declarados antes de ver el resultado, sin ajustar nada)

Sobre los 834 trades OOS de S1-US100. Criterio para quedarse ON: más crecimiento total (suma de log(1 + 1%·R))
y mejor en al menos 2 de cada 3 años.

| Agente | Regla | Trades que deja | E sin filtro → con filtro | Cambio en crecimiento | Años mejores | Decisión |
|---|---|---|---|---|---|---|
| Trend | operar a favor de EMA20 vs EMA50 de 1 h | 525 de 834 | +0.103 → +0.084 | −0.39 | 2/5 | **OFF** |
| Correlation | US500 confirma la dirección desde la apertura | 802 | +0.103 → +0.096 | −0.09 | 1/5 | **OFF** (solo se usa para riesgo) |
| News | sin entradas en días FOMC de 13:55 a 14:45 NY | 832 | +0.103 → +0.102 | −0.01 | 0/5 | **Se queda como guardia** (ver nota) |
| Big Money | a favor del cambio semanal de los *asset managers* (COT, NASDAQ MINI) | 407 | +0.103 → +0.095 | −0.44 | 1/5 | **OFF** |
| Retail | sentimiento de clientes de Capital.com | — | sin historial | — | — | **OFF** (se graba para evaluarlo después) |

Nota sobre News: el filtro solo quitó 2 trades en 5 años, que casualmente ganaron. El backtest no puede
medir su beneficio real porque no modela cómo se abre el spread en una noticia. Por eso queda como **guardia
de seguridad** (no abrir posiciones entre T−5 y T+15 min de eventos de alto impacto, y en FOMC de T−10 a
T+45). Su peso en el score es 0.

## Expectativa realista (bootstrap de días del walk-forward, S1-US100, partiendo de $100)

S1 opera ~0.66 veces por día hábil (unas 3–4 por semana). **No es un bot de muchos trades por noche**:
casi todo el tiempo está esperando.

| Riesgo por trade | Escenario | 1 mes: mediana [p10–p90] | 1 año: mediana [p10–p90] | P(perder ≥50%) en 1 año | P($10,000) |
|---|---|---|---|---|---|
| 0.5% (arranque) | OOS 2022–26 | $100.5 [97.7–104.0] | $108 [97–121] | 0% | 0% |
| **1% (normal)** | OOS 2022–26 | $101.0 [95.5–108.0] | **$117 [94–146]** | 0% | 0% |
| 1% (normal) | solo 2025–26 | $100.0 [94.4–107.2] | $104 [84–132] | 0% | 0% |
| **2% (agresivo)** | OOS 2022–26 | $101.9 [90.9–115.9] | **$131 [87–204]** | 0.1% | 0% |
| 2% (agresivo) | solo 2025–26 | $99.8 [88.8–114.7] | $106 [69–167] | 1.2% | 0% |
| 5% (no permitido) | solo 2025–26 | $98.1 [73.9–135.2] | $93 [33–276] | 23% | 0% |

**Respuesta directa a $100 → $10,000:** con la única ventaja que sobrevivió a una validación honesta, la
probabilidad es 0% en una noche, 0% en un mes y 0% en un año, con cualquier nivel de riesgo que no
garantice la quiebra. Lo realista es entre **+4% y +17% al año** a riesgo normal, y entre **+6% y +31%** en
agresivo, con meses negativos frecuentes. Subir el riesgo a 5% no acelera la mediana: solo agranda la
probabilidad de perder la mitad.
