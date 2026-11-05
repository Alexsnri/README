# 06 · Fuentes de información para los "agentes" del bot de scalping

Fecha: 2026-11-05. Contexto: bot 24/7, barras de 1m a 15m, posiciones de minutos, CFDs en Capital.com (BTC/USD, ETH/USD, XAU/USD, US100, US500, EUR/USD, GBP/USD). Regla del proyecto: un agente se queda activo solo si mejora el backtest fuera de muestra (OOS).

Pruebas de alcance: hice `curl` desde esta máquina el 2026-11-05. "200" significa que la API respondió con datos. Lo que no pude comprobar va marcado **(NO VERIFICADO)**.

---

## Resumen ejecutivo

- **Casi nada de "Big Money" o "Retail" predice a horizonte de minutos.** El COT es semanal y, en general, las posiciones van detrás del precio. Las tasas de fondeo (funding) y el carry predicen riesgo de caída a días o semanas. El sentimiento retail tiene evidencia débil, sobre todo de brokers.
- **Lo que sí actúa a escala de minutos:**
  1. Calendario macro, para no operar o reducir tamaño. Hay evidencia fuerte de volatilidad y spread anómalos de 1 a 15 minutos alrededor de CPI, NFP y FOMC.
  2. Estacionalidad intradía de volatilidad y spread.
  3. Niveles de soporte y resistencia y números redondos (Osler, NY Fed).
  4. Microestructura (desbalance del libro de órdenes), pero su horizonte es de segundos y se come con el spread de un CFD.
- **Recomendación:** usar News y Microestructura como **filtros de riesgo y ejecución**, no como señales de dirección. Trend (multi-timeframe) y Correlación quedan como "probar". Big Money (COT) va OFF para scalping. Del lado cripto (funding, OI, liquidaciones), probar solo como filtro de régimen.

---

## 1. Tendencia multi-timeframe, soporte/resistencia y VWAP

**Evidencia**
- **Análisis técnico intradía en FX después de costos.** Neely y Weller (2003) probaron reglas intradía fuera de muestra, tanto con programación genética como con modelos lineales. Con costos realistas y horario de operación, **no hay rendimientos en exceso**, aunque las reglas sí detectan patrones estables ([JIMF 2003, ficha](https://gpbib.cs.ucl.ac.uk/gp-html/neely_2003_JIMF.html); [WP St. Louis Fed](https://econpapers.repec.org/RePEc:fip:fedlwp:1999-016)). Es la advertencia principal para cualquier agente Trend: el costo del spread domina.
- **Momentum intradía.**
  - Gao, Han, Li y Zhou (JFE 2018): el retorno de la primera media hora del SPY predice el de la última media hora. El R² es de 1.6%, y el efecto es más fuerte en días volátiles y en días de noticias macro ([EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:129:y:2018:i:2:p:394-414)).
  - Baltussen, Da, Lammers y Martens (JFE 2021) lo extienden a más de 60 futuros: índices, bonos, materias primas y FX. El mecanismo es la cobertura de gamma corta, y el efecto revierte en días posteriores ([EUR repository](https://repub.eur.nl/pub/131621)).
  - **Implicación:** el horizonte es de horas y hay una ventana concreta (el cierre de la sesión de EE. UU.). Aplica a US100 y US500 como filtro de sesgo, no como señal de 1 minuto.
- **Filtro de tendencia de marco mayor.** La evidencia académica de *time-series momentum* (Moskowitz, Ooi y Pedersen 2012) es mensual. No encontré estudios revisados por pares que validen el alineamiento 1m/5m/15m/1h/4h como filtro de scalping (**NO VERIFICADO**; casi todo es literatura de practicantes). Hay que tratarlo como hipótesis que el backtest OOS confirma o descarta.
- **Soporte y resistencia.** Osler (NY Fed EPR, 2000) usó datos de FX a 1 minuto y comparó los niveles que publicaban 6 firmas contra 10,000 conjuntos de niveles aleatorios. Encontró **evidencia fuerte de que los niveles publicados predicen interrupciones de tendencia intradía** ([NY Fed EPR](https://www.newyorkfed.org/medialibrary/media/research/epr/00v06n2/0007osle.html)). Osler (2001, SR125) explica el mecanismo: las órdenes stop-loss y take-profit se agrupan en números redondos ([SR125](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr125.html)). Es la pieza con mejor sustento para el horizonte de minutos en EUR/USD, GBP/USD y XAU/USD. Variables candidatas: distancia a números redondos (.00/.50), máximos y mínimos del día y de la sesión anterior.
- **VWAP.** Es el *benchmark* de ejecución institucional estándar (Berkowitz, Logue y Noser 1988; Madhavan 2002) (**NO VERIFICADO** en texto completo). No encontré evidencia de que "el precio regrese al VWAP" sea predictivo. Además, en CFDs de FX e índices no hay volumen centralizado. El `lastTradedVolume` de Capital.com probablemente es volumen de ticks (**NO VERIFICADO**). Para US100 y US500 un VWAP con volumen real exigiría datos de futuros de CME (no gratuitos). Para BTC y ETH sí se puede calcular con trades públicos (ver §6).

**Datos.** Todo sale de las propias velas. Capital.com `GET /api/v1/prices/{epic}` acepta las resoluciones MINUTE, MINUTE_5, MINUTE_15, MINUTE_30, HOUR, HOUR_4, DAY y WEEK, con `max` = 1000 por llamada, `from`/`to`, y bid/ask OHLC. El límite es de 10 peticiones por segundo por usuario, `POST /session` permite 1 por segundo y la sesión expira tras 10 minutos de inactividad ([Capital.com Open API](https://open-api.capital.com/)). Desde aquí el host `api-capital.backend-capital.com` responde (400 `error.null.client.token`, es decir, alcanzable pero sin sesión). La profundidad histórica de 1m en Capital.com no está documentada (**NO VERIFICADO**). Para un backtest largo de cripto conviene data.binance.vision (klines 1m, alcanzable).

---

## 2. "Big Money"

### 2a. CFTC Commitments of Traders (COT)

**Evidencia (horizonte semanal o mayor)**
- **Sanders, Boris y Manfredo (2004), energía:** las posiciones netas **no anticipan** los retornos. Lo contrario sí ocurre: los retornos positivos preceden aumentos en la posición neta de los no comerciales la semana siguiente ([ASU](https://asu.elsevierpure.com/en/publications/hedgers-funds-and-small-speculators-in-the-energy-futures-markets)).
- **Sanders, Irwin y Merrin (2009), 10 mercados agrícolas:** "muy poca evidencia" de valor predictivo ([JARE](https://ageconsearch.umn.edu/record/54547/files/JARE_Aug09__04R_pp276-296.pdf)).
- **Wang (2003), futuros del S&P 500:** los extremos de sentimiento de los grandes operadores dan pronósticos más fiables, a horizonte semanal o mensual ([Applied Fin. Econ.](https://econpapers.repec.org/RePEc:taf:apfiec:v:13:y:2003:i:12:p:891-898)).
- **Banco de Inglaterra (2006)** sobre futuros financieros: contenido informativo limitado ([BoE QB](https://www.bankofengland.co.uk/-/media/boe/files/quarterly-bulletin/2006/the-information-content-of-aggregate-data-on-financial-futures-positions.pdf)).
- **Conclusión:** en el mejor caso, el COT es un sesgo de días a semanas. **No aporta nada a 1–15 minutos.** Además, los datos son del martes y se publican el viernes a las 15:30 ET. En un backtest hay que alinearlos con la fecha de publicación (point-in-time) para no tener sesgo de anticipación.

**API.** CFTC Socrata, gratis y sin clave, con límites de throttling sin token (**NO VERIFICADO** el número exacto). Alcanzable (200):
- Legacy Futures Only: `https://publicreporting.cftc.gov/resource/6dca-aqww.json`, con historia desde 1986-01-15 (lo comprobé con `min(report_date)`).
- TFF (Traders in Financial Futures): `.../resource/gpe5-46if.json`. Ya tiene el reporte de "BITCOIN - CHICAGO MERCANTILE EXCHANGE" con fecha 2026-10-27.
- Se filtra con `$where=market_and_exchange_names like '%GOLD%'`.
- La skill `cot-contrarian-detector` exige **FMP Premium+**, y es innecesaria porque Socrata es gratis.

### 2b. Derivados cripto: funding, open interest (OI), liquidaciones, long/short y ballenas

**Evidencia**
- **Schmeling, Schrimpf y Todorov, "Crypto carry"** ([BIS WP 1087](https://www.bis.org/publ/work1087.pdf); [CEPR DP20719](https://cepr.org/publications/dp20719)): un carry o funding alto **predice caídas futuras** y sube el precio del seguro contra caídas. El mecanismo combina apalancamiento de inversores pequeños que persiguen tendencia con escasez de capital de arbitraje. El horizonte es de días a semanas, no de minutos.
- **Inan (SSRN 5576424):** el funding en sí es predecible fuera de muestra con modelos AR dobles ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5576424)). Ojo: el estudio predice el funding, no el precio.
- **Kim y Hansen (arXiv 2607.09426, perpetuos de Binance 2021–2024):** hay predictibilidad en los cuartos de hora (R² OOS de 3.37%, AUC de 0.60). El desbalance de órdenes de cada cuarto de hora predice retornos a **4–12 horas**, con efectos mucho más débiles a frecuencias finas. Los autores dicen explícitamente que "el componente predecible es pequeño respecto a los costos de transacción": alrededor de 0.5 pb frente a 10 pb de ida y vuelta ([arXiv](https://arxiv.org/html/2607.09426v2)).
- **Liquidaciones y OI a minutos:** no encontré estudios revisados por pares. Solo hay material de practicantes y casos de un solo evento (**NO VERIFICADO**).
- **Uso razonable:** un filtro de **régimen y riesgo**. Con funding u OI extremos, reducir tamaño o evitar entrar a favor de la masa. Una cascada de liquidaciones en curso implica volatilidad alta y spreads abiertos. No sirve como disparador de entradas.

**APIs. Prueba de alcance del 2026-11-05**

| Fuente | Endpoint probado | Resultado | Auth y límites | Historia para backtest |
|---|---|---|---|---|
| **data.binance.vision** | `futures/um/daily/metrics/BTCUSDT` | **200** | Sin clave, archivos ZIP | **Métricas a 5 min** (OI, OI en USD, long/short de top traders y de cuentas, ratio de volumen taker) **desde 2020-09-01** (lo verifiqué). También `fundingRate` mensual, `premiumIndexKlines` de 1m (proxy del funding minuto a minuto), `aggTrades` y `bookDepth`. **No hay liquidaciones** (`liquidationSnapshot` da 404). `bookTicker` existe para 2024 y no para 2026. |
| Binance fapi / api | `fapi.binance.com/futures/data/openInterestHist` | **451** | Bloqueo geográfico | Usar los archivos de Vision para backtest. En vivo, no disponible desde aquí. |
| Bybit | `api.bybit.com` | **403** | Bloqueo geográfico vía CloudFront | — |
| **OKX** | `public/funding-rate`, `public/funding-rate-history`, `public/open-interest`, `rubik/stat/contracts/long-short-account-ratio` (5m), `rubik/.../open-interest-volume` (5m), `public/liquidation-orders` | **200 en todos** | Sin clave. Límite aproximado de 20 req/2 s por endpoint (**NO VERIFICADO**) | Funding con historial paginado. Las series "rubik" solo cubren un periodo reciente: pedir `begin=1700000000000` devolvió "Illegal time range". Las liquidaciones también son solo recientes. Para backtest hay que **grabarlas desde hoy**. |
| **Deribit** | `public/ticker`, `get_funding_rate_value`, `get_book_summary_by_instrument` | **200** | Sin clave para endpoints públicos | El funding histórico funciona (consulté 2024-10). WebSocket `wss://www.deribit.com/ws/api/v2` respondió **101**. |
| **Hyperliquid** | `POST https://api.hyperliquid.xyz/info` con `metaAndAssetCtxs` y `fundingHistory` | **200** | Sin clave, límite por peso (**NO VERIFICADO**) | **Funding horario desde noviembre de 2023** (lo verifiqué con `startTime=1700000000000`). WebSocket respondió **101**. |
| Kraken Futures | `futures.kraken.com/derivatives/api/v3/tickers` | **200** | Sin clave | Incluye funding y OI por ticker (**NO VERIFICADO** el historial). |
| Coinbase | `api.exchange.coinbase.com/products/BTC-USD/ticker` y `/book?level=2` | **200** | Sin clave | Spot. WebSocket `advanced-trade-ws` respondió **101**. |
| Gate.io | `api/v4/futures/usdt/contracts/BTC_USDT` | **200** | Sin clave | Funding indicativo. |
| BitMEX | `api/v1/funding` | **403** | Bloqueado | — |
| Coinglass | `open-api.coinglass.com` | 200 con "API key missing" | El plan gratuito exige clave y es limitado (**NO VERIFICADO**) | — |
| Coinalyze | `api.coinalyze.net/v1` | 401 | Clave gratuita (**NO VERIFICADO** el límite) | Agrega OI, funding y liquidaciones de varios exchanges. |
| Whale Alert | `api.whale-alert.io` | 404 en `/status` | De pago o clave (**NO VERIFICADO**) | Su horizonte predictivo no está demostrado. **OFF.** |

**Recomendación para cripto:** usar **data.binance.vision** (métricas de 5m y `premiumIndexKlines`) para el backtest, y **OKX + Hyperliquid + Deribit** en vivo. Ojo: la fuente del backtest (Binance) y la de vivo (OKX/Hyperliquid) son distintas, así que hay que validar que las series coinciden en el periodo que se traslapa. Las liquidaciones hay que empezar a grabarlas desde ya.

---

## 3. Retail (sentimiento de clientes)

**Capital.com sí tiene el endpoint** ([Open API](https://open-api.capital.com/)):
- `GET /api/v1/clientsentiment/{marketId}` y `GET /api/v1/clientsentiment?marketIds=A,B` devuelven `longPositionPercentage` y `shortPositionPercentage`.
- Requiere los headers `CST` y `X-SECURITY-TOKEN`.
- **No hay endpoint histórico:** solo da el valor actual. Para backtest hay que **grabarlo** cada N minutos, durante meses, antes de poder evaluarlo.

**Evidencia**
- **IG / DailyFX** promueven el IG Client Sentiment como indicador **contrario**, sobre todo en mercados con tendencia ([DailyFX educación](https://dailyfx.com/education/market-sentiment/trading-signals-from-ig-client-sentiment.html)). Ellos mismos dicen que no es infalible y que a veces da señales ambiguas. **No es evidencia independiente:** la publica el propio broker, y no encontré un backtest revisado por pares.
- **Nolte y Nolte (2016, Eur. J. Finance), con unos 2,000 clientes de OANDA:** el flujo retail **sí contiene información** útil para pronósticos de corto plazo fuera de muestra, así que no es puro ruido ([Lancaster eprints](https://eprints.lancs.ac.uk/id/eprint/71649)). Esto **contradice** la idea simple de "ir contra el retail".
- **Otro estudio con datos de OANDA:** el flujo retail **sigue** al precio pasado durante varias horas, es decir, persigue la tendencia. El estudio aparece citado en la [búsqueda de Konstanz](https://kops.uni-konstanz.de/server/api/core/bitstreams/f0e46283-5d68-402a-8fdd-93082a41cdcb/content) (**NO VERIFICADO** en texto completo).
- **Los clientes retail pierden.** ESMA y los propios brokers publican que la mayoría de las cuentas retail de CFDs pierde dinero (74–89% según el broker) (**NO VERIFICADO** para la cifra de Capital.com hoy). Que pierdan sí está documentado. Que su **posicionamiento agregado** prediga la dirección a minutos **no** lo está.
- **Heimer y Simon** (red social de traders de FX) documentan contagio social y efecto disposición, es decir, conducta, no predicción de precio (**NO VERIFICADO** en texto completo).
- **Horizonte:** el sentimiento cambia lento (horas o días). Como señal de minutos su valor esperado es bajo.

**Otras fuentes**
- **Myfxbook Community Outlook:** el endpoint `api/get-community-outlook.json` existe y respondió "Invalid session". Necesita login con cuenta gratuita. Tampoco tiene historial.

**Recomendación: "probar después".** Empezar a grabar el sentimiento de Capital.com desde el día 1, que no cuesta nada, y evaluarlo cuando haya 3–6 meses de datos. Mientras tanto, OFF en decisiones.

---

## 4. Noticias y macro

### 4a. Calendario económico (el agente con mejor sustento)

**Evidencia del efecto a minutos**
- **Ederington y Lee (1993, J. Finance)**, en futuros de tasas y FX: casi todo el ajuste de precio ocurre en el **primer minuto**. La volatilidad sigue **muy elevada unos 15 minutos** y un poco elevada por horas ([IDEAS](https://ideas.repec.org/a/bla/jfinan/v48y1993i4p1161-91.html)).
- **Andersen, Bollerslev, Diebold y Vega (AER 2003):** el FX salta casi de inmediato con las sorpresas macro, y las malas noticias pesan más ([NBER w8959](https://www.nber.org/system/files/working_papers/w8959/w8959.pdf)).
- **Fleming y Remolona (1999, J. Finance)**, en Treasuries: el **spread se abre mucho antes y durante** el anuncio, por control de inventario, y vuelve a la normalidad en **5–15 minutos** ([IDEAS](https://ideas.repec.org/a/bla/jfinan/v54y1999i5p1901-1915.html); [WP FRBNY](https://fraser.stlouisfed.org/files/docs/historical/frbny/researchpapers/frbny_researchpapers_9633.pdf)).
- **Chaboud et al. (Fed IFDP 823)**, con datos de EBS a 1 minuto en EUR/USD y USD/JPY: volumen y volatilidad suben en los minutos siguientes al anuncio ([Fed IFDP 823](https://www.federalreserve.gov/pubs/ifdp/2004/823/ifdp823.htm)).

**Ventana de bloqueo recomendada.** Es un punto de partida que el backtest debe optimizar:
- **Eventos de alto impacto** (CPI, NFP, FOMC con su conferencia, decisiones del BCE/BoE, PCE, GDP adelantado): desde **T−5 hasta T+15 minutos** no abrir posiciones nuevas, y cerrar o proteger las abiertas.
- **FOMC:** ampliar hasta **T+45 minutos**, porque la conferencia de prensa empieza 30 minutos después del comunicado.
- **Eventos de impacto medio:** de T−2 a T+5 minutos.
- **A qué instrumentos aplica:** USD afecta a todo (FX, oro, índices y, por correlación, BTC y ETH). EUR afecta a EUR/USD y GBP afecta a GBP/USD.

**APIs probadas**
- **ForexFactory JSON** `https://nfs.faireconomy.media/ff_calendar_thisweek.json`: **200**, sin clave, 115 eventos esta semana.
  - Campos: `title`, `country` (moneda), `date` (ISO con zona horaria), `impact` (High/Medium/Low/Holiday), `forecast` y `previous`.
  - **No incluye `actual`.**
  - También existe en `.xml`.
  - `ff_calendar_lastweek.json` y `ff_calendar_nextweek.json` dan **404**, así que **no hay historial**.
  - El feed se actualiza unas pocas veces al día y tiene límite de descargas por hora (**NO VERIFICADO** el número exacto). Hay que guardarlo en caché.
  - `forexfactory.com/calendar?week=…` responde 403 (Cloudflare), así que no se puede scrapear desde aquí.
- **FXMacroData** `https://api.fxmacrodata.com/v1/calendar/usd`: **200 sin clave para USD**. Para EUR y otras monedas pide clave de pago (`api_key_required`).
  - Da 473 eventos con `announcement_datetime_utc`, `market_tier` (1–3), `event_importance` y la fuente oficial (NY Fed, BLS, etc.).
  - Solo trae eventos **futuros**, hasta 2027.
- **Trading Economics:** la cuenta `guest:guest` ya no funciona ("discontinued"). Solo de pago.
- **FMP** `stable/economic-calendar`: requiere clave. El plan gratuito tiene 250 req/día según la skill. Es la fuente de `economic-calendar-fetcher`.
- **Finnhub:** requiere clave (401). El calendario económico parece de plan premium (**NO VERIFICADO**).
- **Historial para backtest.** Lo más fiable es **reconstruirlo de fuentes oficiales**:
  - Las fechas de FOMC de [federalreserve.gov](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) (responde 200).
  - Las fechas de publicación de CPI y Employment Situation con el **API de FRED/ALFRED** `fred/release/dates` (clave gratuita, responde sin clave con "api_key is not set").
  - BLS da 403 desde aquí.
  - La hora es fija: 08:30 ET para CPI y NFP, 14:00 ET para FOMC.
  - Alternativa: los eventos de alto impacto se pueden detectar **empíricamente** como saltos de volatilidad o spread en las velas bid/ask de Capital.com.

### 4b. Sentimiento de titulares

- **Evidencia a minutos:** débil. En acciones, un estudio noruego (tesis) encuentra unos −17 pb a 90 minutos tras noticias negativas, y ningún efecto con noticias positivas ([NHH](https://openaccess.nhh.no/nhh-xmlui/handle/11250/2678235)). En cripto casi todo es diario: efecto el mismo día que se diluye a 7 y 30 días, y más fuerte con noticias negativas ([Econ. Modelling 2023](https://ideas.repec.org/a/eee/ecmode/v126y2023ics0264999323002092.html)). Los proveedores de baja latencia (RavenPack, Bloomberg) son caros. Con APIs gratuitas la latencia es de minutos, y el mercado ya reaccionó en el primer minuto (Ederington y Lee).
- **APIs:**
  - **GDELT** doc API: alcanzable, pero respondió 429 ("una petición cada 5 s"). Se actualiza cada 15 minutos y es gratis.
  - **CryptoPanic:** 403 sin clave (requiere token).
  - **Alpha Vantage NEWS_SENTIMENT:** requiere clave gratuita, unas 25 req/día en el plan gratuito (**NO VERIFICADO**).
  - **Finnhub news:** clave gratuita.
- **Recomendación: OFF como señal.** Como mucho, un detector de "evento no programado" (pico en el conteo de titulares de GDELT) para pausar el bot, y solo si el backtest muestra que reduce pérdidas extremas.

---

## 5. Correlaciones y lead-lag

- **Oro frente a DXY y tasas reales a 10 años.** La relación negativa con las tasas reales **se rompió desde finales de 2022** por las compras de bancos centrales. T. Rowe Price y Janus Henderson sostienen que hoy funciona "desde una base más alta" y sigue dando dirección a corto plazo ([T. Rowe Price](https://www.troweprice.com/content/dam/ide/articles/pdfs/2024/q4/what-is-driving-gold-prices-to-all-time-record-highs-na.pdf); [Janus Henderson](https://www.janushenderson.com/en-us/offshore/article/chart-to-watch-whats-behind-the-divergence-between-gold-and-real-treasury-yields/)). Implicación: la correlación cambia con el tiempo, así que solo sirve una correlación móvil, nunca un coeficiente fijo.
- **BTC frente a Nasdaq.** La correlación varía mucho:
  - 90 días de unos 0.65 en mayo de 2022.
  - Mínimos desde 2021 en abril de 2025 ([Block Scholes/CoinDesk](https://www.blockscholes.com/communications/coindesk-bitcoin-no-longer-correlated-to-us-stocks)).
  - Es asimétrica: más fuerte en las caídas ([FXStreet nov-2025](https://www.fxstreet.com/cryptocurrencies/news/bitcoins-correlation-with-nasdaq-stronger-during-market-downturns-202511142200)).
  - Uso: **riesgo de cartera**, para no tener a la vez BTC, ETH, US100 y US500 largos como si fueran apuestas independientes. No sirve como señal.
- **Futuros frente a contado.** Kawaller, Koch y Koch (1987) encuentran que los futuros del S&P adelantan al índice de contado 20–45 minutos ([IDEAS](https://ideas.repec.org/a/bla/jfinan/v42y1987i5p1309-29.html)). Stoll y Whaley encuentran unos 5 minutos ([JFQA](https://www.cambridge.org/core/product/6C0C02141F02160D48AB9CA1FDFB2785)). Buena parte se debe a precios rezagados de las acciones del índice (*non-trading*), no a un adelanto aprovechable. **Los CFD de índices de Capital.com se cotizan a partir de futuros**: el DXY lo dice explícitamente ("front two months of US Dollar Index futures", [Capital.com DXY](https://capital.com/us-dollar-index)), y para US100 y US500 está **NO VERIFICADO**. Por lo tanto **no hay adelanto futuro→CFD aprovechable**, salvo latencia del broker.
- **US100 frente a US500.** Casi el mismo subyacente en el mismo horario. Cabe esperar un adelanto menor a 1 minuto, no aprovechable (**NO VERIFICADO**, no encontré estudio).
- **BTC frente a ETH.** Con datos horarios la causalidad es mayormente bidireccional y "apenas explotable" (Sifat et al. 2019, [RIBAF](https://econpapers.repec.org/RePEc:eee:riibaf:v:50:y:2019:i:c:p:306-321)). Con datos tick, una tesis de Southampton encuentra que **BTC a menudo va rezagado** ([tesis](https://eprints.soton.ac.uk/504578/1/Final_Thesis_for_archive.pdf)). Un *preprint* de 2025 encuentra que el CME suele adelantar al spot de BTC, con resultados mixtos en alta volatilidad ([arXiv 2506.08718](https://arxiv.org/abs/2506.08718v1)). **No hay base para un "BTC adelanta a ETH" a 1 minuto.**
- **Un adelanto que sí vale la pena probar:** el precio de BTC en exchanges con más liquidez (Coinbase, OKX y Deribit, todos alcanzables) frente al CFD de Capital.com. Si el CFD se actualiza tarde, la diferencia es una señal de ejecución (**NO VERIFICADO**; requiere grabar ticks de ambos).

**Datos**
- **Capital.com** ofrece el CFD **US Dollar Index (DXY)** con spread de 0.054 y horario aproximado de 00:00 a 21:00 UTC de lunes a viernes ([Capital.com](https://capital.com/us-dollar-index)). Si hay CFD de bono de EE. UU. a 10 años está **NO VERIFICADO**. Hay que buscarlo con `GET /api/v1/markets?searchTerm=`.
- **FRED** da datos diarios sin clave por CSV: `fredgraph.csv?id=DFII10` (tasa real a 10 años) respondió **200** con historia desde 2003. Con clave gratuita, el API completo.
- **Intradía de tasas:** no hay fuente gratuita fiable (**NO VERIFICADO**). Se puede usar el CFD del DXY de Capital.com como proxy del dólar.

---

## 6. Microestructura

- **Evidencia.** Cont, Kukanov y Stoikov (2014, J. Fin. Econometrics) muestran que el *order flow imbalance* (OFI) explica linealmente el cambio de precio **en el mismo intervalo**. Es una relación **contemporánea**, con pendiente inversa a la profundidad, a escalas de segundos ([arXiv 1011.6402](https://arxiv.org/abs/1011.6402)). Como señal predictiva el horizonte es de **segundos**. En cripto el desbalance precede movimientos de corto plazo, pero los costos dominan ([arXiv 2506.05764](https://arxiv.org/pdf/2506.05764v2); [arXiv 2010.01241](https://arxiv.org/pdf/2010.01241)). Kim y Hansen confirman que lo predecible es mucho menor que el costo de ida y vuelta.
- **Estacionalidad intradía de la volatilidad.** Es un hecho robusto (Andersen y Bollerslev 1997, **NO VERIFICADO** en texto completo): hay picos en las aperturas de Londres y Nueva York y spread alto en el *rollover* (21:00–22:00 UTC). Es barato y útil para ajustar stops y tamaño, y para no operar en el rollover. Se calcula con las propias velas bid/ask de Capital.com.
- **Spread en vivo.** Viene del bid/ask de Capital.com (REST o streaming). Es el filtro número uno: no entrar si el spread supera el percentil X de la hora correspondiente.
- **L2 cripto en vivo:** respondieron **101** los WebSockets de Kraken (`wss://ws.kraken.com/v2`), Coinbase (`advanced-trade-ws`), Deribit y Hyperliquid. El de OKX no respondió a la prueba de curl (000), aunque su REST sí funciona. Los REST de libro de Kraken (`/0/public/Depth`) y Coinbase (`/book?level=2`) dan **200**. **Historial:** `bookDepth` (porcentajes de profundidad) y `aggTrades` en data.binance.vision, alcanzables. Con `aggTrades` se pueden calcular desbalance de volumen taker y VWAP de BTC y ETH.
- **Recomendación:** spread y estacionalidad **ON** como filtros. OFI **probar**, solo para BTC y ETH, como filtro de *timing* de entrada (no entrar contra un desbalance fuerte en los últimos 10–30 s), sabiendo que su horizonte es más corto que la barra de 1 minuto.

---

## 7. Stage 0: MCP servers y skills existentes (no instalé nada)

### Skills del repo clonado `tradermonty/claude-trading-skills`

Licencia MIT, último commit 2026-11-02. Repositorio: `/tmp/claude-0/-home-user-README/82cdbbb4-ddee-5e71-af10-eeafa19fca7d/scratchpad/ext/tradermonty/skills`.

| Skill | Qué API usa | Clave | Útil aquí |
|---|---|---|---|
| `economic-calendar-fetcher` | FMP `stable/economic-calendar` | `FMP_API_KEY` (gratis, 250 req/día) | Parcial. Es para que un LLM lo lea, no para el bot. Sirve como referencia de código. ForexFactory + FXMacroData no necesitan clave. |
| `fxmacrodata-calendar` | `api.fxmacrodata.com/v1` | USD sin clave; resto `FXMACRODATA_API_KEY` (de pago) | **Sí, como referencia.** Su lógica de "si falla, asumir riesgo de evento" es buena práctica. Solo da eventos futuros. |
| `cot-contrarian-detector` | FMP COT | **FMP Premium+** | No. Horizonte semanal; usar CFTC Socrata gratis si acaso. |
| `crypto-regime-analyzer` | CoinGecko + `fapi.binance.com` | Sin clave | **No funciona aquí**: `fapi.binance.com` da 451. Su horizonte es diario. |
| `institutional-flow-tracker` | FMP 13F | `FMP_API_KEY` | No. Son acciones, con 45 días de rezago. |

**Evaluación de confianza:** es código abierto (MIT) y está activo. Las skills solo leen APIs de datos y no ejecutan órdenes. Su diseño apunta a análisis discrecional, no a señales de minutos. **No vale la pena instalarlas para el bot.** Como mucho, conviene leer `fxmacrodata-calendar/scripts/fetch_calendar.py` como patrón.

### MCP servers encontrados

- **`kjpou1/forexfactory-mcp`** (MIT, unas 15 estrellas, scraper con Playwright, 1 herramienta; la carga de historial está en el *roadmap* sin hacer) ([GitHub](https://github.com/kjpou1/forexfactory-mcp)). Scrapear ForexFactory puede violar sus términos, y aquí el sitio da 403. **No instalar**: el JSON de faireconomy basta.
- **`capital-com-sv/capital-mcp`** (MIT, unas 8 estrellas, 38 herramientas, incluye sentimiento) ([GitHub](https://github.com/capital-com-sv/capital-mcp)). **Ojo: `CAP_ALLOW_TRADING` vale true por defecto**, y Capital.com no tiene claves de solo lectura. No pude confirmar que sea oficial: la organización "capital-com-sv" sugiere que sí, pero el propio README dice que Capital.com no avala software de terceros. Solo valdría para exploración manual en cuenta **demo**, con `CAP_ALLOW_TRADING=false` y `CAP_DRY_RUN=true`. Para el bot conviene el cliente REST propio. Otras alternativas no oficiales: `syedair/capital-com-mcp-server` (PyPI) y `SimonTarara62/capitalcom-mcp-server` (alrededor de 1 estrella).
- **Coinglass MCP** (`forgequant/coinglass-mcp`, `aviman1109/coinglass_mcp`) requieren clave de Coinglass. **LiquidVision MCP** es remoto, sin clave, cubre OI y funding de 13 venues, y sus "mapas de liquidación" son **modelos**, no datos ([glama](https://glama.ai/mcp/servers/lv-analytics/liquidvision-mcp/tree)). **No instalar**: los datos públicos de OKX, Hyperliquid y Deribit son directos y gratis, y un MCP remoto añade un tercero opaco a la cadena de datos.
- **`Crypto-Data-API/cryptodataapi-skills`** (skills.sh): plan gratuito de 5 req/min, depende de un proveedor comercial ([GitHub](https://github.com/Crypto-Data-API/cryptodataapi-skills)). **No instalar.**

**Veredicto Stage 0:** **ninguna instalación es necesaria.** Todas las fuentes útiles tienen APIs públicas directas que el bot puede consumir sin intermediarios. Los MCP o skills solo servirían para análisis manual del usuario con Claude, nunca en la ruta crítica del bot.

---

## 8. Tabla final

| Fuente | Instrumentos | Horizonte predictivo | Fuerza de la evidencia | API gratis y ¿alcanzable? | ¿Historia para backtest? | Recomendación |
|---|---|---|---|---|---|---|
| Tendencia multi-timeframe (1m→4h) | Todos | Horas (momentum intradía); a minutos sin evidencia | Débil-media; Neely y Weller: no rentable tras costos | Capital.com `/prices` (sí) | Sí: Capital.com (profundidad NO VERIFICADA) y Binance Vision para cripto | **Probar** |
| Soporte/resistencia y números redondos | FX, XAU (también índices) | Minutos (intradía) | **Media-fuerte** (Osler 2000/2001) | Derivado de velas | Sí | **Probar (prioridad)** |
| VWAP | BTC, ETH (volumen real); índices y FX sin volumen real | Benchmark de ejecución, no predictivo | Débil | aggTrades de Binance Vision (sí) | Sí (cripto) | **Probar** (solo cripto) |
| Momentum última media hora EE. UU. | US100, US500 | 30 minutos al cierre | Media-fuerte (JFE 2018/2021) | Velas | Sí | **Probar** |
| COT (CFTC) | XAU, NQ, ES, EUR, GBP, BTC | Semanas | Débil o nula; las posiciones siguen al precio | Socrata (sí, desde 1986) | Sí (point-in-time del viernes) | **OFF** |
| Funding y carry cripto | BTC, ETH | Días o semanas (riesgo de caída) | Media (BIS 2023) | OKX, Hyperliquid, Deribit (sí); Binance/Bybit (no) | Sí: Binance Vision (funding y premium 1m), Hyperliquid desde 2023 | **Probar como filtro de régimen** |
| OI y long/short cripto | BTC, ETH | Horas (4–12 h); a minutos débil | Débil-media; no supera costos | OKX rubik (sí, solo reciente) | Sí: Binance Vision 5m desde 2020-09 | **Probar (filtro)** |
| Liquidaciones cripto | BTC, ETH | Minutos (volatilidad) | Anecdótica | OKX `liquidation-orders` (sí, reciente) | **No**: hay que grabar desde hoy | **Grabar y probar después** |
| Whale Alert y flujos on-chain | BTC, ETH | No demostrado | Nula | De pago o clave | No | **OFF** |
| Sentimiento retail de Capital.com | Todos | Horas o días; dirección ambigua | Débil y de brokers (IG); Nolte: el retail informa | Sí (con sesión) | **No**: hay que grabar | **Grabar y probar después** |
| Myfxbook / IG sentiment | FX, XAU, índices | Igual que el anterior | Débil | Myfxbook con login; IG con cuenta | No | **OFF** |
| Calendario macro (bloqueo de entradas) | Todos (USD domina) | **Minutos (de T−5 a T+15, FOMC hasta +45)** | **Fuerte** (Ederington-Lee, ABDV, Fleming-Remolona) | FF JSON (sí), FXMacroData USD (sí) | Reconstruible: Fed + FRED/ALFRED (clave gratis) + detección empírica | **ON** |
| Sentimiento de titulares (GDELT, CryptoPanic, AV) | Todos | Minutos a días; las APIs gratis llegan tarde | Débil | GDELT (sí, 1 req/5 s); CryptoPanic y AV con clave | GDELT sí; el resto limitado | **OFF** (si acaso, pausa por evento no programado) |
| Correlación DXY y tasas reales con oro | XAU, EUR/USD, GBP/USD | Días; inestable desde 2022 | Media pero cambiante | CFD DXY de Capital.com (sí); FRED diario (sí) | Sí | **Probar** (filtro de riesgo) |
| Correlación BTC con Nasdaq | BTC, ETH, US100 | Días; asimétrica | Media | Velas | Sí | **ON solo para límites de exposición** |
| Lead-lag futuros→CFD y US100↔US500 | Índices | Menos de 1 minuto, no aprovechable | Fuerte el fenómeno, nula su explotabilidad | — | — | **OFF** |
| Lead-lag BTC→ETH | BTC, ETH | No demostrado a 1 minuto | Débil o contradictoria | Coinbase, OKX, Kraken (sí) | Binance Vision | **OFF** (probar solo exchange→CFD) |
| Spread en vivo y estacionalidad horaria | Todos | Inmediato (costo y riesgo) | **Fuerte** | Capital.com bid/ask (sí) | Sí (velas bid/ask) | **ON** |
| Desbalance del libro (OFI, L2) | BTC, ETH | **Segundos** | Fuerte (contemporánea); predictiva menor que el costo | Kraken, Coinbase, Deribit, Hyperliquid WS (101) | bookDepth y aggTrades de Binance Vision | **Probar** (timing de entrada) |
