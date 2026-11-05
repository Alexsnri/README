# RESEARCH — Bot de scalping para Capital.com DEMO ($100)

Fecha: 5 de noviembre de 2026. Seis subagentes investigaron en paralelo, uno por tema. Cada capítulo completo,
con todas sus fuentes enlazadas, está en `research/` y los scripts que calcularon los números están en
`research/scripts/`. Este archivo es el resumen ejecutivo y las decisiones que salen de ahí. Lo que no se
pudo verificar lleva la marca **(NO VERIFICADO)** en el capítulo correspondiente.

| Capítulo | Tema |
|---|---|
| [01-capital-api.md](research/01-capital-api.md) | API de Capital.com: sesión, precios, streaming, órdenes, límites, tamaños mínimos, apalancamiento, costos |
| [02-instrumentos-horarios.md](research/02-instrumentos-horarios.md) | Qué operar en cada hora: spreads, volatilidad medida por hora, razón costo/movimiento, calendario de rotación |
| [03-estrategias.md](research/03-estrategias.md) | Evidencia sobre scalping, momentum intradía, breakout, reversión a la media y filtros |
| [04-aprendizaje-y-capital.md](research/04-aprendizaje-y-capital.md) | Walk-forward, bandits, tamaños de muestra, Kelly, riesgo de quiebra y Monte Carlo con $100 |
| [05-stops.md](research/05-stops.md) | Break-even, trailing y cierres parciales: literatura y mini-estudio con datos reales |
| [06-fuentes-informacion.md](research/06-fuentes-informacion.md) | Tendencia, grandes jugadores, retail, noticias, correlaciones y microestructura: qué sirve y a qué horizonte |

---

## 1. La respuesta honesta a "$100 → $10,000 en una noche"

Multiplicar por 100 en una noche **no es un objetivo de trading, es una lotería**. Estos números salen de los
Monte Carlo de `research/scripts/mc_scalp.py` (40 trades por noche, riesgo fijo sobre el capital actual;
"ruina" quiere decir bajar de $20):

| Cómo se juega | P(tocar $10,000 esa noche) | P(ruina esa noche) |
|---|---|---|
| Riesgo ≤10% por trade, incluso con una ventaja muy buena (+0.10R) | **0%** | ≤1.2% |
| 20% por trade, +0.10R | 0.03% | 28% |
| 50% por trade, +0.10R | 2.2% | 92% |
| Todo en cada trade ("all-in") | ~2% (como ganar 6 volados seguidos) | ~100% |

- Para que la **mediana** llegue a 100x en una noche hace falta un Sharpe *diario* de ~3, más o menos 48
  anualizado. Con 40 trades serían +0.48R netos por trade. Ningún fondo del mundo tiene eso. Los mejores
  sistemas publicados de momentum intradía ganan unos 4 puntos base por trade.
- Si no hay ventaja (E ≤ 0), ningún esquema de apuestas da más de ~1% de probabilidad de llegar alguna vez a
  $10k (teorema de muestreo opcional).
- Contexto: **80.96% de las cuentas retail de CFD de Capital.com pierden dinero**, según su propio aviso.
  ESMA reporta entre 74% y 89% para todo el sector. En Brasil, 97% de los day traders que duraron más de 300
  días perdió (Chague, De-Losso y Giovannetti, 2019).

**El objetivo más agresivo que todavía tiene sentido:** con una ventaja confirmada de +0.10R por trade y 2%
de riesgo, la mediana tarda unos **3 a 4 meses** en ir de $100 a $10,000 y nunca baja de −50%. Eso supone
que la ventaja existe y se mantiene. Lo más probable es que la ventaja real sea cero o negativa hasta que se
demuestre lo contrario, y para medirlo está la demo.

### Tabla de expectativa realista (40 trades/día, con frenos, partiendo de $100)

Mediana del capital y rango p10–p90:

| Perfil / ventaja neta por trade | 1 día | 1 semana | 1 mes | P(perder ≥50%) en 1 mes |
|---|---|---|---|---|
| Arranque 0.5%, E = 0 | $99.6 [97–104] | $99.6 [90–110] | $98.5 [81–122] | 0% |
| Arranque 0.5%, E = +0.05R | $100.6 | $105.6 [95–119] | $127 [102–162] | 0% |
| Normal 1%, E = 0 | $99.1 | $98.3 [81–121] | $94 [63–144] | 2% |
| Normal 1%, E = +0.05R | $101.0 | $110.8 [89–140] | $158 [100–252] | 0.1% |
| Normal 1%, E = +0.10R | $103.6 | $126 [99–161] | $269 [163–443] | 0% |
| Agresivo 2%, E = −0.05R (sin ventaja real) | $94.2 | $75 [54–109] | $31 [20–66] | **80%** |
| Agresivo 2%, E = 0 | $98.6 | $93.9 [65–142] | $80 [36–184] | 22% |
| Agresivo 2%, E = +0.10R | $106.8 | $154 [96–251] | $639 [237–1,761] | 0% |

Crecimiento mediano por día en el mejor caso honesto (agresivo con +0.10R): alrededor de **+6–7% diario
compuesto** en días de 40 trades. En el caso más probable (E ≈ 0) el crecimiento es ~0% y solo se paga spread.

---

## 2. Lo que la investigación cambió del plan

1. **El scalping de 1 minuto no cubre el spread en casi nada.** Con la predictibilidad intradía publicada
   (R² ≈ 1–2%) el spread de Capital.com se cubre en US100 a partir de ~5 min de holding, en US500 y oro a
   partir de ~15 min, y en FX con holdings cercanos a 60 min. **En BTC y ETH no se cubre ni a 60 min**
   (cap. 03). Medido en R con un stop de 1 ATR de 5 minutos, el spread cuesta: US100 0.07R, oro 0.13–0.2R,
   US500 0.15R, EURUSD 0.31R, ETH 0.49R, GBPUSD 0.49R y BTC 0.61R (cap. 04).
   → **El bot opera velas de 5 minutos, con holdings de 5 a 90 minutos**: es "scalping intradía", no de
   segundos. US100, US500 y oro son el núcleo, EURUSD entra en Londres y en el solapamiento, y cripto queda
   en prueba solo para la ventana de 07:40–11:00. GBPUSD queda fuera.
2. **El tamaño mínimo no es el problema con $100; el spread sí.** Mínimos según la web: BTC 0.0001, ETH
   0.001, oro 0.01, US100 0.001, US500 0.01 y EURUSD/GBPUSD 100 unidades. Con ellos, un stop de 1 ATR arriesga
   centavos, así que el riesgo de 0.5–2% sí se puede dimensionar. El bot lee `dealingRules.minDealSize` de la
   API al arrancar en vez de confiar en estos valores.
3. **La API no permite cierres parciales** (`DELETE /positions` no acepta `size`), y la investigación
   muestra que el cierre parcial nunca mejora la expectativa: solo baja la varianza (cap. 05). → **Cierre
   parcial apagado.**
4. **Break-even pronto destruye ganadoras.** El MAE (excursión adversa máxima) de las ganadoras llega a ~0.85
   ATR en el percentil 75. Con BE a +0.5 ATR, ~60% de los trades que llegan ahí terminan en cero y el
   porcentaje de trades ≥0 *baja* de 49% a 23% si no se deja colchón para el deslizamiento. → **BE a partir
   de +1.0 ATR(5m)**, con el umbral exacto por instrumento definido en el backtest.
5. **El trailing en índices perjudicó** de forma significativa (−0.08 a −0.17R por trade en NQ) y en cripto
   no hizo diferencia. Además, un backtest con velas OHLC que llena el stop exactamente en su nivel le regala
   al trailing +0.04 a +0.13R → **el backtest siempre modela deslizamiento en stops**.
6. **Demo de Capital.com:** máximo 1,000 aperturas de posición por hora, ejecución "at touch" (sale
   optimista contra la cuenta real), la cuenta empieza con $1,000 y se puede ajustar con `topUp`, y **la
   cuenta demo se cierra tras 2 semanas sin operar**. No existen API keys de solo lectura y **la misma key
   sirve en real**, así que el bot fija la URL demo en el código y se niega a arrancar con otra.
7. **Fines de semana: no operar.** Solo abre cripto, su rango de 5 minutos baja a la mitad y el spread se
   come el 80–100% del movimiento.

---

## 3. Agentes de información: veredicto previo (se confirma en backtest fuera de muestra)

| Agente | Qué usa | Horizonte con evidencia | Decisión inicial |
|---|---|---|---|
| **News** | Calendario ForexFactory (JSON gratis) y fechas de Fed, BLS y BCE | Minutos: el spread se abre 5–15 min y la volatilidad sigue alta ~15 min (Andersen et al. 2003, Fleming-Remolona) | **ON** como bloqueo: sin entradas de T−5 a T+15 min (FOMC hasta T+45) |
| **Trend** | Alineación 5m/15m/1h/4h, VWAP, niveles redondos | Intradía (Osler, NY Fed: soportes/resistencias frenan tendencias) | **Probar** en backtest como filtro |
| **Big Money** | COT de la CFTC (semanal) y funding/OI de cripto (OKX, Hyperliquid, data.binance.vision) | Días o semanas, no minutos (Sanders 2004/2009; BIS "Crypto carry") | **COT OFF** para scalping; funding solo como filtro de régimen en cripto (probar) |
| **Retail** | `/api/v1/clientsentiment` de Capital.com | Contrario a días (IG/DailyFX); sin historial para backtest | **Solo grabar**: se evalúa cuando junte semanas de datos propios |
| **Correlation** | DXY, US100↔US500, BTC↔Nasdaq | Correlación variable; sin lead-lag aprovechable a minutos | **Solo riesgo**: posiciones correlacionadas cuentan como una sola |
| Microestructura | Spread en vivo y estacionalidad por hora | Inmediato | **ON** dentro del Filter |

---

## 4. Estrategias candidatas para la Etapa 2 (≈38 configuraciones en total, para limitar el multiple testing)

| # | Estrategia | Evidencia | Instrumentos / sesión |
|---|---|---|---|
| S1 | **Noise Area + VWAP** (Zarattini, Aziz y Barbon 2024): momentum que entra cuando el precio sale de la "zona de ruido" del día | ~4 pb por trade neto contra ~0.9 pb de spread en SPY (relación 4:1). Sin revisión de pares | US500, US100 en horario del contado |
| S2 | **Opening Range Breakout** (apertura de NY y de Londres) | El paper original da positivo sin costos; una réplica con costos da ~0 neto | Índices a las 08:30; EURUSD a las 02:00 |
| S3 | **Momentum de la última media hora** (Gao, Han, Li y Zhou 2018; Baltussen et al. 2021) | ~4.5 pb brutos por trade | US500, US100 |
| S4 | **Reversión a VWAP con filtro de régimen** (solo en rango, ADX bajo) | Débil; buena parte es rebote bid-ask | EURUSD, oro |
| S5 | **Contra movimientos extremos de 1 h en cripto**, con filtro de funding | Reversión de 1–4 h en BTC (De Nicola 2021); no rentable en simulación (Caporale 2019) | BTC, ETH |
| S6 | Estacionalidad de BTC 21–23 UTC (**control**: si "gana", el backtest está mal) | ~8 pb brutos ≈ spread | BTC |

Protocolo: costo = 1.25× el spread publicado por hora del día (estresado a 2×), deslizamiento de 0.5× el
spread en los stops, funding nocturno si se cruza las 16:00, walk-forward de entrenamiento 2021–2024 y
prueba 2025–2026, Deflated Sharpe y PBO, y evaluación con `backtest-expert`. Pasan solo "Deploy" o "Refine".

---

## 5. Recomendación inicial

### Instrumentos y horario (hora de CDMX, UTC−6 fijo; EE. UU. en horario de invierno desde el 1-nov-2026)

| Franja CDMX | Qué opera | Notas |
|---|---|---|
| Dom 16:00 – Lun 17:30 y cada día 15:45–17:30 | **Nada** | Reapertura, rollover, funding a las 16:00 y spreads máximos |
| 18:00–02:00 (Asia) | US100, GOLD con riesgo reducido | Solo si el spread en vivo ≤ 1.5× su mediana |
| 02:00–07:25 (Londres) | US100, GOLD, EURUSD, US500 | Pausa por BoE y datos de Europa |
| 07:25–07:40 | Nada en días de dato (NFP, CPI) | Ventana de noticias |
| **07:40–11:00 (solapamiento + apertura de EE. UU.)** | **Todo el universo**, cripto incluida si pasa el backtest | Ventana principal; pausa de 08:28 a 08:35 por la apertura del contado |
| 11:00–14:45 (NY tarde) | US100, US500, GOLD | FOMC 13:00: pausa de 12:50 a 13:45 |
| 14:45–15:45 | Solo gestionar salidas | Cripto cerrada antes de las 14:55 |
| Viernes 15:45 → domingo | **Nada; cerrar todo** | Gap medio de fin de semana: 42 pb en US100 y 22 pb en oro |

En verano de EE. UU. (desde el 14-mar-2027) todo lo ligado a NY y Londres se recorre 1 hora antes. El bot no
fija horas: las calcula con zonas horarias reales (America/New_York y Europe/London) y además consulta
`openingHours` de la API.

### Perfiles de riesgo

| Perfil | Riesgo/trade | Riesgo abierto máx. | Stop diario | Breaker | P(ruina) 30 días | P(−50%) 30 días |
|---|---|---|---|---|---|---|
| **Arranque** (primeros ~300 trades) | 0.5% | 1.5% | −6R | 7 pérdidas seguidas → pausa 2 h a medio tamaño; 10 → alto del día | 0% en todos los escenarios simulados | ≤0.1% |
| **Normal** | 1% (≈¼ de Kelly) | 3% | −6R | igual | ≈0% si E ≥ 0 | 2% si E = 0; 28% si E = −0.05 |
| **Agresivo** (con ≥500 trades y E ≥ +0.08R confirmada) | 2% | 5% | −6R | igual | 2% si E = 0; **25% si E = −0.05** | 22% si E = 0; 80% si E = −0.05 |
| ~~Lotería~~ (≥20% o all-in) | — | — | — | — | 90–100% en una noche | — |

Reglas de aprendizaje: para distinguir una ventaja de +0.10R de cero hacen falta ~271 trades; para +0.05R,
~1,082. Por eso el Learner solo reasigna peso entre estrategias ya validadas (Thompson sampling gaussiano
sobre R-múltiplos con descuento γ ≈ 0.995) y solo cambia parámetros en walk-forward, nunca por una racha. Un
breaker de 5–6 pérdidas seguidas saltaría por puro azar en 21–41% de las noches, por eso queda en 7 y 10.

---

## 6. Etapa 0: qué se instaló y qué no

| Herramienta | Estado | Para qué | Revisión de seguridad |
|---|---|---|---|
| `trading-skills@agiprolabs-claude-trading-skills` (68 skills, MIT) | **Instalado** (plugin, ámbito de usuario) | walk-forward, régimen, volatilidad, Kelly, sizing, salidas, journal, visualización | Sin hooks ni MCP; solo Markdown y scripts que llaman APIs públicas conocidas |
| `backtest-expert` (tradermonty, MIT) | **Instalado** en `.claude/skills/` | Veredicto Deploy/Refine/Abandon de cada backtest | Script local sin red; `subprocess` solo en sus tests |
| `capital-com-sv/capital-mcp` (MCP oficial, MIT) | **No instalado** | Pensado para un LLM con confirmación manual, no para un bot 24/7; trae `CAP_ALLOW_TRADING=true` por defecto | Lo usé como referencia para el cliente propio |
| Otras skills de tradermonty (COT, calendario, régimen cripto) | No instaladas | Piden clave de FMP Premium o dependen de fapi.binance.com, que está bloqueado aquí | — |
| MCP de ForexFactory / Coinglass | No instalados | Uno scrapea el sitio; el otro pide clave. El JSON público de ForexFactory basta | — |

Decisión: **cliente propio y delgado de Capital.com** (httpx + websockets), sin dependencias de terceros
para órdenes.
