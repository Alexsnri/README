# 01 · API de Capital.com: investigación para un bot de scalping (solo DEMO)

Fecha de la investigación: 2026-11-05. La fuente principal es la documentación oficial en [open-api.capital.com](https://open-api.capital.com/) (la descargué y la leí completa) y el Help Center oficial, que consulté por su API pública de Zendesk porque las páginas HTML regresan 403. Todo lo marcado **(NO VERIFICADO)** sale de terceros, de inferencias o de datos que no pude confirmar en una fuente oficial.

---

## 1. Autenticación y sesión

**URLs base**
| Entorno | REST | WebSocket |
|---|---|---|
| **DEMO** | `https://demo-api-capital.backend-capital.com/api/v1` | `wss://api-streaming-capital.backend-capital.com/connect` |
| Live (NO usar) | `https://api-capital.backend-capital.com/api/v1` | el mismo host WS |

- Las dos URLs base vienen en [la documentación oficial](https://open-api.capital.com/). El [entorno Postman oficial de demo](https://github.com/capital-com-sv/capital-api-postman) usa `https://demo-api-capital.backend-capital.com/api/v1`.
- **Hay un solo host WebSocket para demo y live.** La documentación solo publica `wss://api-streaming-capital.backend-capital.com/connect` ([docs](https://open-api.capital.com/)), y el MCP oficial lo usa con cualquiera de los dos entornos ([config.py de capital-mcp](https://raw.githubusercontent.com/capital-com-sv/capital-mcp/main/capital_mcp/config.py)). La respuesta de `POST /session` trae `streamingHost` ([docs](https://open-api.capital.com/)), así que conviene leer el host de ahí. El entorno (demo o live) lo determinan los tokens CST/X-SECURITY-TOKEN, no el host. Esto último lo inferí **(NO VERIFICADO)**. Probé con DNS y los hosts `demo-streaming-…` y `demo-api-streaming-…` no resolvieron.
- Lo comprobé con curl sin credenciales: `GET /api/v1/time` en demo responde `{"serverTime":...}`. `GET /api/v1/ping` sin tokens responde `{"errorCode":"error.null.client.token"}`. El servidor expone los headers `CST` y `X-SECURITY-TOKEN` (`access-control-expose-headers`).

**Cómo obtener la API key** ([docs](https://open-api.capital.com/), [FAQ de API](https://help.capital.com/hc/en-us/articles/4415179146386-How-to-generate-an-API-key)):
1. Activar **2FA**, que es obligatorio antes de generar la key.
2. Ir a Settings > API integrations > Generate new key y capturar una etiqueta, una **contraseña personalizada** (distinta de la de la plataforma), una caducidad opcional (por defecto 1 año) y el código 2FA.
3. La key se muestra **una sola vez**. Solo existe un tipo de privilegio, el de trading: **no hay keys de solo lectura**. Se pueden pausar o reactivar. Hay un máximo de 100 intentos de generación en 24 h ([docs](https://open-api.capital.com/)).
4. Una key se borra si la cuenta queda SUSPENDED/BLOCKED o si caduca ([docs](https://open-api.capital.com/)).

**`POST /session`** ([docs](https://open-api.capital.com/))
- Header: `X-CAP-API-KEY: <api key>`.
- Body: `{"identifier": "<login/email>", "password": "<contraseña personalizada de la API key>", "encryptedPassword": false}`.
- La respuesta trae los **headers `CST`** (token de autorización) y **`X-SECURITY-TOKEN`** (identifica la cuenta financiera). El body incluye `accountType`, `accountInfo{balance,deposit,profitLoss,available}`, `currencyIsoCode`, `currentAccountId`, `streamingHost`, `accounts[]`, `clientId`, `timezoneOffset`, `hasActiveDemoAccounts`, `hasActiveLiveAccounts` y `trailingStopsEnabled`.
- Límite: **1 request/s por API key**. Puede responder 400, 401 o 429.
- Todas las llamadas siguientes llevan los headers `CST: <cst>` y `X-SECURITY-TOKEN: <token>`.

**Contraseña cifrada (opcional)** ([docs](https://open-api.capital.com/))
1. `GET /session/encryptionKey` con `X-CAP-API-KEY` regresa `encryptionKey` (una llave pública RSA en base64) y `timeStamp`.
2. Se cifra `base64(password + "|" + timeStamp)` con RSA en modo PKCS1 y se codifica el resultado en base64. La documentación dice "AES", pero su código de ejemplo usa RSA/PKCS1.
3. Se envía `POST /session` con `encryptedPassword: true`.

**Duración de la sesión** ([docs](https://open-api.capital.com/))
- Los tokens valen **10 minutos desde su último uso**. Si pasa más tiempo de inactividad, la siguiente request da error y hay que crear otra sesión.
- `GET /ping` con CST y X-SECURITY-TOKEN mantiene viva la sesión y responde `{"status":"OK"}`.
- El MCP oficial considera que la sesión expira a los 540 s, es decir 9 min ([session.py](https://raw.githubusercontent.com/capital-com-sv/capital-mcp/main/capital_mcp/session.py)).
- `DELETE /session` cierra la sesión.

**Cambiar de cuenta**: `PUT /session` con body `{"accountId": "..."}` ([docs](https://open-api.capital.com/)). Responde `trailingStopsEnabled`, `dealingEnabled`, `hasActiveDemoAccounts` y `hasActiveLiveAccounts`. **El streaming WS se cae al cambiar de cuenta** ([FAQ en docs](https://open-api.capital.com/)). `GET /session` regresa `clientId`, `accountId`, `timezoneOffset`, `locale`, `currency` y `streamEndpoint`.

> Seguridad: la misma API key sirve para demo y live, y no existe modo de solo lectura. La única barrera es la URL base. Por eso el bot debe **fijar en el código la URL demo y rechazar cualquier otra**.

---

## 2. Precios históricos y datos de mercado

**`GET /prices/{epic}`** ([docs](https://open-api.capital.com/))
- `resolution`: `MINUTE, MINUTE_5, MINUTE_15, MINUTE_30, HOUR, HOUR_4, DAY, WEEK`.
- `max`: por defecto 10, **máximo 1000** velas por request.
- `from` y `to`: formato `YYYY-MM-DDTHH:MM:SS` (p. ej. `2022-04-01T01:01:00`). Filtran sobre `snapshotTimeUTC`.
- Sin parámetros regresa las velas de 1 minuto de los últimos 10 minutos.
- Respuesta: `prices[]` con `snapshotTime`, `snapshotTimeUTC`, `openPrice/closePrice/highPrice/lowPrice` (cada uno con `{bid, ask}`) y `lastTradedVolume`. Incluye además `instrumentType`.
- **Profundidad de los datos MINUTE: (NO VERIFICADO).** La documentación no la dice y no encontré otra fuente. Hay que medirla en demo, paginando hacia atrás con `from`/`to` hasta que llegue vacío o un error 400. 1000 velas M1 son unas 16.7 h, así que un backtest largo necesita muchas requests (con un límite de 10 req/s).

**`GET /markets`** ([docs](https://open-api.capital.com/)): acepta `searchTerm` (con prioridad) o `epics` (hasta 50, separados por coma). Sin parámetros lista todos los mercados. Cada elemento trae `epic, symbol, instrumentType, instrumentName, lotSize, bid, offer, high, low, netChange, percentageChange, updateTime(UTC), delayTime, streamingPricesAvailable, marketStatus (TRADEABLE/CLOSED…), scalingFactor, marketModes, pipPosition, tickSize`. También existen `GET /marketnavigation` y `/marketnavigation/{nodeId}` (`limit` de hasta 500).

**`GET /markets/{epic}`** ([docs](https://open-api.capital.com/); el ejemplo es SILVER):
- `instrument`: `epic, symbol, name, lotSize, type, guaranteedStopAllowed, streamingPricesAvailable, currency, marginFactor, marginFactorUnit ("PERCENTAGE")`.
  - `openingHours`: horarios por día con `zone: "UTC"`. En el ejemplo: lun–jue `00:00-21:59` y `23:05-00:00`.
  - `overnightFee {longRate, shortRate, swapChargeTimestamp, swapChargeInterval (en minutos, 1440)}`.
- `dealingRules`: `minStepDistance`, `minDealSize`, `maxDealSize`, `minSizeIncrement`, `minGuaranteedStopDistance`, `minStopOrProfitDistance` y `maxStopOrProfitDistance`, todos con la forma `{unit: POINTS|PERCENTAGE, value}`. Además `marketOrderPreference` y **`trailingStopsPreference`** (en el ejemplo, `"NOT_AVAILABLE"`).
  - **No existe un campo separado para la "distancia mínima del trailing stop"** en la documentación. Supongo que aplica `minStopOrProfitDistance` **(NO VERIFICADO)**.
- `snapshot`: `marketStatus, bid, offer, high, low, decimalPlacesFactor, scalingFactor, marketModes`.

---

## 3. WebSocket

Fuente de toda esta sección: [docs](https://open-api.capital.com/).
- URL: `wss://api-streaming-capital.backend-capital.com/connect`.
- Cada mensaje lleva `destination`, `correlationId`, `cst`, `securityToken` y `payload`.
- **Suscripción a cotizaciones**:
  ```json
  {"destination":"marketData.subscribe","correlationId":"1","cst":"…","securityToken":"…","payload":{"epics":["OIL_CRUDE"]}}
  ```
  - La confirmación llega como `payload.subscriptions{EPIC:"PROCESSED"}`.
  - Cada tick llega con `destination:"quote"` y el payload `{epic, product:"CFD", bid, bidQty, ofr, ofrQty, timestamp(ms)}`.
  - Para cancelar se usa `marketData.unsubscribe`.
- **Velas en vivo**: `OHLCMarketData.subscribe` con payload `{epics[], resolutions[] (por defecto MINUTE, mismos valores que REST), type: "classic"|"heikin-ashi"}`.
  - Los eventos llegan con `destination:"ohlc.event"` y `{resolution, epic, type, priceType:"bid", t, o, h, l, c}`.
  - El ejemplo solo muestra `priceType: "bid"`. No sé si también llegan velas ask **(NO VERIFICADO)**.
- **Límite: 40 epics por conexión.**
- **Keepalive**: mandar `{"destination":"ping","correlationId":"5","cst":"…","securityToken":"…"}` **al menos cada 10 min**. La "duración de sesión WS" es de 10 minutos.
- La documentación solo lista estos destinos: market data, OHLC y ping. **No hay un canal de eventos de órdenes o posiciones.** Las ejecuciones hay que consultarlas por REST (`/positions`, `/confirms`, `/history/activity`). Un plugin de terceros ([PyneCore](https://pypi.org/project/pynesys-pynecore-capitalcom/)) dice lo mismo.

---

## 4. Órdenes y posiciones

Todos los endpoints de esta sección vienen de las [docs](https://open-api.capital.com/).

**`POST /positions`** (a mercado)
| Campo | Notas |
|---|---|
| `direction` | `BUY`/`SELL` (obligatorio) |
| `epic`, `size` | obligatorios |
| `guaranteedStop` | bool, default false. Si es true, requiere `stopLevel`, `stopDistance` o `stopAmount`. **No se puede usar con trailingStop ni con hedgingMode=true** |
| `trailingStop` | bool. Si es true, **`stopDistance` es obligatorio**. No se puede combinar con guaranteedStop |
| `stopLevel` / `stopDistance` / `stopAmount` | nivel de precio, distancia o monto de pérdida |
| `profitLevel` / `profitDistance` / `profitAmount` | lo mismo para el take profit |

- La respuesta solo trae `{"dealReference":"o_…"}`. El sistema crea primero una orden con el prefijo `o_`.
- **Que la respuesta sea exitosa no garantiza que la posición se haya abierto.** Hay que confirmar con **`GET /confirms/{dealReference}`**, que regresa `date, status (OPEN…), dealStatus (ACCEPTED/REJECTED), epic, dealReference, dealId, affectedDeals[{dealId,status:"OPENED"}], level, size, direction, guaranteedStop, trailingStop`.
  - El `dealId` de la posición está en `affectedDeals` y puede haber más de uno.
  - La documentación no muestra el campo `reason` en el ejemplo de confirmación. Que traiga `reason`/`rejectReason` en un rechazo está **(NO VERIFICADO)**: hay que registrar el JSON completo.

**Otros endpoints de posiciones**
- `GET /positions`: cada posición trae `position{contractSize, createdDateUTC, dealId, dealReference, workingOrderId, size, leverage, upl, direction, level, currency, guaranteedStop}` y `market{…bid, offer, marketStatus…}`.
- `GET /positions/{dealId}`: lo mismo para una sola posición.
- **`PUT /positions/{dealId}`** recibe los mismos campos de stop y TP, más `guaranteedStop` y `trailingStop`, y regresa `dealReference`. Sirve para mover el SL o el TP o para activar el trailing.
  - Según el código del MCP oficial, en un PUT a working orders el bróker **pone en false `guaranteedStop`/`trailingStop` si se omiten**, y los campos que faltan se borran. Por eso el MCP vuelve a mandar los valores existentes ([risk.py](https://raw.githubusercontent.com/capital-com-sv/capital-mcp/main/capital_mcp/risk.py)). Que `PUT /positions` se comporte igual está **(NO VERIFICADO)**: hay que mandar siempre el estado completo.
- **`DELETE /positions/{dealId}`** cierra la posición. **La documentación no define un parámetro `size`, así que la API no ofrece cierre parcial directo.** El Help Center describe el cierre parcial solo en la interfaz web y en la app ([help](https://help.capital.com/hc/en-us/articles/4403989686418-How-to-close-a-position-partially)).
  - Alternativa: con `hedgingMode=false`, "abrir una posición opuesta cierra automáticamente la existente" ([Capital.com](https://capital.com/what-is-hedging-mode-and-how-to-use-it-in-trading)). Que una orden opuesta de **menor tamaño solo reduzca la posición** es **(NO VERIFICADO)**: el plugin PyneCore dice que así lo emula en cuentas netting ([PyPI](https://pypi.org/project/pynesys-pynecore-capitalcom/)). Hay que probarlo en demo.

**Working orders**
- `GET /workingorders`.
- `POST /workingorders` con `direction, epic, size, level, type (LIMIT|STOP)`, `goodTillDate` opcional (UTC) y los mismos campos de stop y TP.
- `PUT /workingorders/{dealId}`: `level`, `goodTillDate` y los stops.
- `DELETE /workingorders/{dealId}`.

**Trailing stop nativo**
- Corre en el servidor como atributo de la posición. Se activa con `trailingStop:true` + `stopDistance`, al abrir o con PUT ([docs](https://open-api.capital.com/)).
- Está disponible en cuentas CFD, salvo para residentes de Francia. El stop solo se mueve a favor ([help](https://help.capital.com/hc/en-us/articles/11187435844242-Can-I-use-trailing-stop-loss)).
- Hay dos interruptores: el flag de cuenta `trailingStopsEnabled` (en `POST`/`PUT /session`) y el flag por mercado `dealingRules.trailingStopsPreference` ([docs](https://open-api.capital.com/)). Si hace falta activar `trailingStopsEnabled` desde la plataforma y no desde la API está **(NO VERIFICADO)**. El bot debe revisar los dos y, si no hay trailing nativo, mover el SL con `PUT`.
- La documentación no prohíbe el trailing en modo hedging. Solo prohíbe el **guaranteed stop** con hedging.

---

## 5. Límites de uso

Fuente: [FAQ "limitations" en las docs](https://open-api.capital.com/) y el [changelog](https://open-api.capital.com/).
| Límite | Valor |
|---|---|
| General | **10 requests/s por usuario** ([también en el Help Center](https://help.capital.com/hc/en-us/articles/6630830103058-Do-you-have-any-limitations-on-your-API)) |
| Abrir posiciones o crear órdenes | **1 cada 0.1 s** por usuario. Más rápido, se rechazan |
| `POST /session` | **1/s por API key** |
| **DEMO: `POST /positions` + `POST /workingorders`** | **1000 por hora** (desde 2022-03-23) |
| `POST /accounts/topUp` | 10/s y **100 por cuenta al día** |
| WebSocket | 40 instrumentos y sesión de 10 min (requiere ping) |
| Generar API keys | 100 intentos en 24 h |
| `/history/activity` | rango máximo de 1 día |

El MCP oficial aplica justo estos números: global 10 req/s, sesión 1 req/s y trading 1 cada 0.1 s ([USAGE.md](https://raw.githubusercontent.com/capital-com-sv/capital-mcp/main/USAGE.md)). Hay una página de estado en status.capital.com ([USAGE.md](https://raw.githubusercontent.com/capital-com-sv/capital-mcp/main/USAGE.md)).

---

## 6. Cuenta

Todos los endpoints de esta sección vienen de las [docs](https://open-api.capital.com/).

**`GET /accounts`**
- Regresa `accounts[]` con `accountId, accountName, status, accountType ("CFD"), preferred, balance{balance, deposit, profitLoss, available}, currency, symbol`.
- `available` es el margen libre. `profitLoss` es el P/L no realizado. La relación `balance = deposit + profitLoss` la deduje del ejemplo: 90.38 + 2.51 = 92.89.

**`GET /accounts/preferences`**
- Regresa `{"hedgingMode": false, "leverages": {"SHARES":{"current":2,"available":[1,2,3,5]}, "CURRENCIES":{…}, "INDICES":{…}, "CRYPTOCURRENCIES":{…}, "COMMODITIES":{…}}}`.
- Las cifras del ejemplo son ilustrativas. Hay que leer las reales de la cuenta.

**`PUT /accounts/preferences`**
- Body `{"leverages": {...}, "hedgingMode": bool}`. Es la forma de cambiar el apalancamiento por clase de activo y el modo hedging.
- En demo no se puede fijar apalancamiento por orden individual; solo por clase de activo ([help](https://help.capital.com/hc/en-us/articles/360016572320-What-is-the-maximum-leverage)).

**`POST /accounts/topUp`** (demo)
- Body `{"amount": n}`, con un mínimo de **-400000** y un máximo de 400000. El balance no puede pasar de 100000 y hay un límite de 100 llamadas al día ([docs](https://open-api.capital.com/)).
- **La cuenta demo empieza con 1,000** ([help](https://help.capital.com/hc/en-us/articles/30648929372306-How-do-I-change-my-demo-account-balance)). Para dejarla en **$100** se puede mandar `amount: -900`. Que acepte montos negativos se deduce del mínimo documentado de -400000, pero no lo he probado **(NO VERIFICADO)**.
- **La cuenta demo se cierra si pasan 2 semanas sin operar** ([help](https://help.capital.com/hc/en-us/articles/4403947617298-How-long-can-I-use-a-demo-account-for)).

**`GET /history/activity`**
- Parámetros `from`/`to` (máximo 1 día), `lastPeriod` (en segundos, máximo 86400), `detailed=true`, `dealId` y `filter` en FIQL (p. ej. `epic==GOLD;source==SL`).
- `source` puede ser `CLOSE_OUT, DEALER, SL, SYSTEM, TP, USER`. Sirve para saber si una posición la cerró el SL, el TP o un margin close-out.

**`GET /history/transactions`**
- Parámetros `from`/`to`/`lastPeriod` (por defecto los últimos 10 min) y `type`. Los tipos incluyen `TRADE, SWAP, TRADE_COMMISSION, TRADE_COMMISSION_GSL, FX_COMMISSION, INACTIVITY_FEE, ADJUSTMENT, NEGATIVE_BALANCE_PROTECTION…`.
- Cada registro trae `date, dateUtc, instrumentName, transactionType, note, reference, size (monto), currency, status`.
- **El costo real del swap sale de `type=SWAP`.**

---

## 7. Sentimiento de clientes

Sí existe ([docs](https://open-api.capital.com/)):
- `GET /clientsentiment?marketIds=SILVER,NATURALGAS` regresa `clientSentiments[{marketId, longPositionPercentage, shortPositionPercentage}]`.
- `GET /clientsentiment/{marketId}` regresa lo mismo para un solo mercado.
- Es solo el porcentaje de clientes en largo o en corto. No trae volumen ni historial.

---

## 8. Entidad regulatoria y apalancamiento para México

- **México no aparece en la lista de países restringidos.** La lista sí incluye a EE. UU., Canadá, Bahamas, India, Japón, Turquía y otros. Además, **no aceptan ciudadanos de EE. UU. aunque vivan en otro país** ([help, actualizado 2026-08-18](https://help.capital.com/hc/en-us/articles/27040372144274-Is-Capital-com-available-in-my-country)).
- Entidad para México: **Capital Com Online Investments Ltd**, autorizada por la **Securities Commission of The Bahamas (SCB)** con licencia **SIA-F245**.
  - El pie del sitio internacional (`/en-int`, al que redirige `/es-mx`) lo confirma ([capital.com/en-int](https://capital.com/es-mx)).
  - Fuentes mexicanas confirman la misma entidad y señalan que **no está supervisada por la CNBV** ([finantres.mx](https://finantres.mx/organismos-reguladores-licencias-capital-com-protege-usuario-mexico/), [financera.mx](https://financera.mx/opiniones/capital-com/)).
  - Mi navegación vino de una IP de Hong Kong, no de México. Que la asignación sea idéntica para una IP o residencia mexicana sale de las fuentes mexicanas citadas, no de una prueba propia.
- **Apalancamiento máximo para clientes retail** ([help, actualizado 2026-09-30](https://help.capital.com/hc/en-us/articles/360016572320-What-is-the-maximum-leverage)). Las pestañas de la tabla son EU / UK / Australia / UAE / **Resto del mundo**. A México le corresponde **"Resto del mundo"**; esa asignación la deduje porque México no es EU, UK, AU ni UAE:
  - **200:1** en pares de divisas, **200:1** en índices, **200:1** en materias primas (incluye el oro), **20:1** en cripto y **20:1** en acciones.
  - Algunos instrumentos tienen un máximo fijo menor.
  - Por comparación: EU 30:1 en majors, 20:1 en oro e índices y 2:1 en cripto. UAE llega hasta 500:1 en EURUSD, oro y US100/US500, y 100:1 en cripto.
- **Margen que muestran las páginas de mercado** en en-int, observado hoy: oro, EURUSD, GBPUSD, US100 y US500 con **1.00 %** (100:1); BTC/USD y ETH/USD con **5.00 %** (20:1). Fuentes: [Gold](https://capital.com/en-int/markets/commodities/gold-spot-commodity), [BTC](https://capital.com/en-int/markets/cryptocurrencies/bitcoin-to-us-dollar-chart), [EURUSD](https://capital.com/en-int/markets/forex/euro-us-dollar-rate-2). Puede tratarse del apalancamiento por defecto y no del máximo. El dato de la cuenta es `GET /accounts/preferences` → `available`.

---

## 9. Spreads, swaps, comisiones y tamaños mínimos

- **No hay comisión por operación**: el costo es el spread. Tampoco cobran por la cuenta demo. Hay una conversión de divisas de 0.7 % para retail y la GSL cobra prima solo si se activa ([Charges & fees](https://capital.com/en-int/ways-to-trade/fees-and-charges)).
- **Los spreads son dinámicos** ([misma fuente](https://capital.com/en-int/ways-to-trade/fees-and-charges)).
- **Fórmula del swap**: 4 % anual de comisión de Capital.com ± la tasa de referencia (SOFR para USD), dividida entre 360 o 365 días. Las posiciones 1:1 no pagan swap salvo excepciones (gas natural, cacao, VIX, pares con TRY) ([help](https://help.capital.com/hc/en-us/articles/360016641939-What-is-the-overnight-funding-fee)).
- **Hora del cargo: 22:00 UTC, que son las 16:00 en CDMX (UTC-6).** En FX y metales preciosos, desde el 11-may-2026 se cobra un **triple swap el miércoles** y no se cobra el fin de semana ([help](https://help.capital.com/hc/en-us/articles/360016641939-What-is-the-overnight-funding-fee)).

Datos observados hoy en las páginas en-int (SCB), con precio indicativo. Las fuentes por fila son: [Gold](https://capital.com/en-int/markets/commodities/gold-spot-commodity), [BTC](https://capital.com/en-int/markets/cryptocurrencies/bitcoin-to-us-dollar-chart), [ETH](https://capital.com/en-int/markets/cryptocurrencies/ethereum-to-us-dollar-chart), [US100](https://capital.com/en-int/markets/indices/us-tech-100-index-1), [US500](https://capital.com/en-int/markets/indices/us-500-index-1), [EURUSD](https://capital.com/en-int/markets/forex/euro-us-dollar-rate-2) y [GBPUSD](https://capital.com/en-int/markets/forex/british-pound-us-dollar-rate-2).

| Instrumento (epic probable) | Precio aprox. | Spread mostrado | Spread % | Swap largo/día | Swap corto/día | Tamaño mín. | Margen |
|---|---|---|---|---|---|---|---|
| Gold Spot (`GOLD`) | 4,136.92 | 0.5 | ~0.012 % | -0.01542 % | +0.00720 % | 0.01 | 1 % |
| BTC/USD (`BTCUSD`) | 80,657 | 50 | ~0.062 % | -0.06164 % | +0.01370 % | 0.0001 | 5 % |
| ETH/USD (`ETHUSD`) | 2,431 | 1.75 | ~0.072 % | -0.06164 % | +0.01370 % | 0.001 | 5 % |
| US Tech 100 (`US100`) | 28,260.7 | 1.8 | ~0.0064 % | -0.02246 % | +0.00023 % | 0.001 | 1 % |
| US 500 (`US500`) | 7,684.2 | 0.6 | ~0.0078 % | -0.02246 % | +0.00023 % | 0.01 | 1 % |
| EUR/USD (`EURUSD`) | (NO VERIFICADO) | 0.00007 (0.7 pip) | – | -0.00801 % | -0.00021 % | 100 | 1 % |
| GBP/USD (`GBPUSD`) | (NO VERIFICADO) | 0.00013 (1.3 pip) | – | -0.00407 % | -0.00415 % | 100 | 1 % |

- **Epics.** `GOLD`, `US500` y `OIL_CRUDE` aparecen en los ejemplos de la documentación ([docs](https://open-api.capital.com/)). `BTCUSD` y `GOLD` aparecen en el README del MCP oficial ([README](https://github.com/capital-com-sv/capital-mcp/blob/main/README.md)). `EURUSD` aparece en el [plugin PyneCore](https://pypi.org/project/pynesys-pynecore-capitalcom/). **`US100` y `ETHUSD` como epics: (NO VERIFICADO).** "US100" es el ticker que muestra la web. Hay que confirmarlos con `GET /markets?searchTerm=...` en demo.
- **Tamaños mínimos.** Las cifras de la tabla son las de la web. El Help Center da otros ejemplos genéricos: forex 500, cripto 0.01, materias primas e índices 0.1, "según el instrumento" ([help](https://help.capital.com/hc/en-us/articles/4403989787538-What-is-the-minimum-trade-size)). **La fuente que manda es `dealingRules.minDealSize` y `minSizeIncrement` de la API.**
- **Diferencia entre demo y live.** En demo la ejecución puede ser instantánea "at touch", mientras que en live puede haber fills parciales o a otros precios ([help](https://help.capital.com/hc/en-us/articles/4403988777874-What-s-the-difference-between-a-demo-and-a-live-trading-account)). **Los resultados de un scalper en demo van a salir optimistas.**
- **Margin call.** Con equity por debajo del 100 % del margen ya no se pueden abrir operaciones. Con equity en 50 % o menos empieza el **close-out automático** ([help](https://help.capital.com/hc/en-us/articles/360016556180-Margin-calls)).

---

## 10. Clientes, MCP y skills existentes (Stage-0)

| Proyecto | URL | Actividad | Licencia | Evaluación |
|---|---|---|---|---|
| **capital-mcp** (oficial: la org `capital-com-sv` está enlazada desde las docs oficiales) | [GitHub](https://github.com/capital-com-sv/capital-mcp) | 8★, 5 forks, 6 commits; imagen `ghcr.io/capital-com-sv/capital-mcp` | MIT | **Confiable.** Python con httpx y fastmcp. Tiene 38 tools, sesión con auto-refresh y ping, rate limiter, WS y flujo preview→confirm. Por defecto limita a 20 órdenes al día y tamaño 1.0. Sirve para inspección manual con Claude, **no como motor de un bot 24/7**. Inconsistencia: la página de docs dice "trading disabled by default" y el README dice "enabled by default" ([docs](https://open-api.capital.com/), [README](https://github.com/capital-com-sv/capital-mcp/blob/main/README.md)) |
| capital-api-postman (oficial) | [GitHub](https://github.com/capital-com-sv/capital-api-postman) | 25★, 7 commits | MIT | Referencia de requests y entornos demo/live |
| api-java-samples (oficial, bot RSI) | [GitHub](https://github.com/capital-com-sv/api-java-samples) | (NO VERIFICADO) | (NO VERIFICADO) | Solo como referencia |
| `capitalcom` (Akinzou) | [PyPI](https://pypi.org/project/capitalcom/), [GitHub](https://github.com/Akinzou/CapitalCom) | 2★, v1.0.4 (2025-07-03) | **CC BY-NC 4.0** | Solo REST, sin WS. Licencia no comercial. **No usar** |
| `python-capital` (iribeirocampos) | [PyPI](https://pypi.org/project/python-capital/), [GitHub](https://github.com/iribeirocampos/python-capital) | 6★, 17 commits, v0.2.2 (2025-12-20) | MIT | Básico, sin WS ni trailing |
| `capitalcom-python` (tunga3109) | [PyPI](https://pypi.org/project/capitalcom-python/) | v0.2.3 (2023-12-25), abandonado | MIT | No usar |
| `capital-com-mcp-server` (syedair) | [PyPI](https://pypi.org/project/capital-com-mcp-server/), [GitHub](https://github.com/syedair/mcp-servers) | 3★, v0.3.2 (2025-09-12) | MIT | Comunitario y no oficial |
| `capitalcom-cli` / capitalcom-mcp-server (SimonTarara62) | [PyPI](https://pypi.org/project/capitalcom-cli/) | v0.6.2 (2026-06-15) | Apache-2.0 | No oficial y con poca tracción |
| `pynesys-pynecore-capitalcom` | [PyPI](https://pypi.org/project/pynesys-pynecore-capitalcom/) | v0.9.6 (2026-10-18) | Apache-2.0 | Atado al framework PyneCore. Sus notas técnicas son útiles |
| Claude skills | [claudemarketplaces finance](https://claudemarketplaces.com/skills/category/finance) | — | — | **No encontré ninguna skill específica de Capital.com.** (NO VERIFICADO de forma exhaustiva en skills.sh) |

**Recomendación: escribir un cliente propio y delgado** (unas 300–500 líneas con `httpx` y `websockets`), usando como referencia de diseño el código MIT del MCP oficial: `session.py`, `rate_limit.py` y `risk.py`. Las razones:
- La API es pequeña: unos 25 endpoints.
- Ningún paquete comunitario tiene tracción ni cubre bien WS y trailing.
- El MCP oficial está pensado para un LLM con confirmación humana, no para trading automático.
- Un cliente propio permite **fijar la URL demo de forma inmutable**.

El MCP oficial se puede instalar aparte con `CAP_ENV=demo` para que Claude inspeccione la cuenta durante el desarrollo.

---

## Implicaciones para el bot

1. **Solo demo.** Usar la constante `BASE_URL = "https://demo-api-capital.backend-capital.com/api/v1"` y un `assert` al arrancar que rechace cualquier otra URL. Antes de operar, verificar que la respuesta de `POST /session` traiga `hasActiveDemoAccounts=true` y que `currentAccountId` sea la cuenta demo. Nunca llamar a `PUT /session` con una cuenta live. La API key es de trading y sirve también para live, así que hay que guardarla como secreto.
2. **Sesión.**
   - `GET /ping` cada **5 minutos**, con margen frente a los 10 minutos de expiración.
   - Refrescar la sesión (crear una nueva) si llega un 401 o un `error.invalid.session`/`error.null.client.token` **(NO VERIFICADO el código exacto)**.
   - Reintentar `POST /session` como máximo 1 vez por segundo, con backoff.
   - Ping al WS cada **4–5 minutos**. Reconectar y volver a suscribirse si se cae o si cambian los tokens.
3. **Presupuesto de requests.**
   - Límite duro: 10 req/s. El bot debería usar ≤ 5 req/s de forma sostenida y separar al menos 0.1 s entre aperturas.
   - **Límite crítico en demo: 1000 `POST /positions` + `POST /workingorders` por hora**, unos 16 por minuto. En la práctica conviene quedarse en **≤ 300 por hora**, unas 5 por minuto, para tener margen ante reintentos.
   - Los cierres (`DELETE`) y las modificaciones (`PUT`) no aparecen en ese límite **(NO VERIFICADO)**.
   - Los precios en vivo deben llegar **por WS** (hasta 40 epics), no consultando REST.
   - Las confirmaciones se consultan con `GET /confirms` cada 200–500 ms, con un timeout de unos 5 s.
4. **Datos históricos.** Máximo 1000 velas por request, así que 1 día de M1 son 2 requests. La profundidad de M1 hay que medirla en demo **(NO VERIFICADO)**. Hay que guardar caché local en SQLite o Parquet.
5. **Lo que una cuenta de $100 puede operar.** Se usa `topUp amount:-900` sobre los 1,000 iniciales, que está **(NO VERIFICADO)**. Precios y tamaños mínimos de hoy, con apalancamiento web de 100:1 (y 20:1 en cripto):
   - **EURUSD**, 100 unidades (mínimo): nocional ≈ $115, margen ≈ $1.15, 1 pip = **$0.01**, spread ≈ $0.007. Un movimiento de 10 pips son $0.10.
   - **GOLD**, 0.01 (mínimo): nocional ≈ $41, margen ≈ $0.41, $1 de movimiento = **$0.01**, spread ≈ $0.005. Con 0.10 oz, $1 de movimiento = $0.10 y el margen ≈ $4.1.
   - **US100**, 0.001: nocional ≈ $28, 1 punto = $0.001. Con 0.01, 1 punto = $0.01 y el margen ≈ $2.8.
   - **US500**, 0.01: nocional ≈ $77, 1 punto = $0.01, spread ≈ $0.006.
   - **BTCUSD**, 0.0001: nocional ≈ $8, margen ≈ $0.40, spread ≈ $0.005. Con 0.001, el nocional ≈ $81 y el margen ≈ $4. El spread es de ~0.06 %, y en scalping se come la ventaja rápido.
   - **ETHUSD**, 0.001: nocional ≈ $2.4. El spread es de ~0.07 %, el más caro relativamente.
   - Conclusión: con $100 y 1 % de riesgo ($1 por operación) **sí se pueden abrir posiciones mínimas** en todos los instrumentos, y el margen no es el cuello de botella. El cuello de botella es **el spread contra el objetivo del scalp**. Los costos más bajos en porcentaje son los de US100, US500, GOLD y EURUSD; las cripto son las más caras.
   - El tamaño debe calcularse siempre con `minDealSize`, `minSizeIncrement` y `minStopOrProfitDistance` de `GET /markets/{epic}`, que hay que guardar en caché al arrancar.
6. **Swap.** El cargo es a las 16:00 hora CDMX, con triple swap el miércoles en FX y oro. Un scalper debería **cerrar todo antes de las 15:55 CDMX**, o tomar en cuenta el swap leyendo `/history/transactions?type=SWAP`. Además, el oro y los índices tienen una pausa diaria de ~22:00–23:05 UTC (16:00–17:05 CDMX), según el ejemplo de `openingHours`. El horario de cada instrumento hay que leerlo de su `openingHours`.
7. **Modo de cuenta.** Conviene `hedgingMode=false` (netting). Una orden opuesta cierra la posición, y hay que probar en demo si una orden opuesta más pequeña la reduce parcialmente **(NO VERIFICADO)**. La API **no tiene cierre parcial directo**.
8. **Trailing stop nativo.** Usarlo solo si `trailingStopsEnabled` y `trailingStopsPreference` lo permiten, mandando siempre `stopDistance`. Si no, programar un trailing propio con `PUT /positions/{dealId}`, mandando el estado completo de SL, TP y flags. Hay que tener en cuenta la latencia y los límites de requests.
9. **Coherencia del estado.** No existe un stream de órdenes. Hay que reconciliar cada 5–15 s con `GET /positions` y usar `/history/activity` (filtrado por `source==SL|TP|CLOSE_OUT`) para saber por qué se cerró cada operación.
10. **Mantener viva la cuenta demo.** Se cierra después de 2 semanas sin operar, así que hay que alertar si el bot pasa más de 10 días sin trades.
