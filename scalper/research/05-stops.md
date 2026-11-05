# 05 · Gestión de stops (Stop Manager): evidencia, restricciones y política por defecto

**Alcance:** bot de scalping (velas de 1 a 5 min, posiciones de minutos) en CFD de Capital.com (costo = spread) sobre BTC/USD, ETH/USD, XAU/USD, US100, US500, EUR/USD y GBP/USD. El Stop Manager mueve el stop del servidor solo a favor: break-even (BE) más costos, trailing (ATR o estructura), candados escalonados y cierre parcial opcional.
**Fecha:** 2026-11-05. Lo marcado "(NO VERIFICADO)" no se confirmó con una fuente primaria en esta sesión.

---

## 0. Resumen ejecutivo

1. **Teoría.** Si el precio es una martingala, por el teorema de paro opcional ninguna regla de salida basada en información pasada cambia la esperanza bruta (= 0): stops, BE, trailing y parciales solo **cambian la forma de la distribución** (% de ganadoras, varianza, cola), y la esperanza neta es −costo. Los stops añaden valor solo si los rendimientos son **predecibles condicionalmente a la trayectoria** (autocorrelación positiva o momentum, cambios de régimen). Esa es exactamente la conclusión de Kaminski & Lo (2014) y de Lo & Remorov (2017).
2. **Mi estudio** (BTC/ETH 1m de Binance, ago–oct 2026, más oro, NQ y EURUSD de Yahoo en 5m). Con entradas aleatorias, **todas las políticas quedan dentro de ±0.03R entre sí**, y casi ninguna diferencia es estadísticamente significativa. El costo domina: E[R] va de −0.19R a −0.25R cuando el costo es aproximadamente 0.2R.
3. **Hallazgo metodológico clave.** En un backtest con OHLC, suponer que el stop se llena *exactamente* en su nivel infla artificialmente el trailing: en un paseo aleatorio sintético le da entre +0.04R y +0.13R. Lo validé y el sesgo escala con 1/√(subpasos). **Siempre hay que modelar deslizamiento en las órdenes stop.** Sin eso, el trailing "gana" en backtest por puro artefacto.
4. **Microestructura.** En BTC y ETH, el ATR(14) de 1m (3.5 y 5.5 bps) es **del mismo tamaño que el spread** supuesto (3 y 5 bps). Un stop basado en el ATR de 1m cuesta unos 0.6R por operación (E ≈ −1.3R). El stop y el trailing deben medirse en la escala del **ATR de 5m** y con un piso de aproximadamente **5× el spread**.
5. **BE.** Mover a BE pronto (+0.5 ATR) reduce la σ del resultado un 25–30%, pero convierte en "scratch" el ~60% de las operaciones que llegan a +0.5 ATR. Si el nivel de BE no incluye un colchón para el deslizamiento, esas operaciones terminan ligeramente negativas: el % de operaciones ≥0 baja de 0.49 a 0.24. Mover el BE no crea esperanza.
6. **Parcial 50%.** Es matemáticamente una mezcla convexa de dos salidas, así que su esperanza es el promedio de ambas y nunca supera a la mejor. Reduce la σ un 10–12% y deja la esperanza ≈ igual o ligeramente menor (−0.008R en BTC, con IC que excluye 0).

---

## 1. Literatura sobre la efectividad del stop-loss

| Trabajo | Resultado clave | Relevancia para el bot |
|---|---|---|
| **Kaminski & Lo (2014)**, "When do stop-loss rules stop losses?", *J. Financial Markets* 18:234–254 ([MIT DSpace](https://dspace.mit.edu/handle/1721.1/114876), [RePEc](https://ideas.repec.org/a/eee/finmar/v18y2014icp234-254.html)) | Definen la "stopping premium" analíticamente. **Bajo paseo aleatorio, el stop-loss siempre reduce el rendimiento esperado** (te saca del activo de mayor rendimiento sin compensación). Bajo momentum o autocorrelación positiva puede sumar. En el estudio empírico (acciones de EE. UU. con rotación a bonos, mensual, 1950–2004), ciertas reglas añaden entre 50 y 100 pb por mes **durante los periodos de stop-out**. | Si a 1–5 min no hay momentum condicional, el stop es un **control de riesgo**, no una fuente de alfa. |
| **Han, Zhou & Zhu (2016)**, "Taming momentum crashes: a simple stop-loss strategy" ([SSRN 2407199](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2407199); resúmenes en [Alpha Architect](https://alphaarchitect.com/2016/08/taming-the-momentum-roller-coaster-fact-or-fiction/) y [CXO](https://www.cxoadvisory.com/technical-trading/stop-losses-to-avoid-stock-momentum-crashes/)) | Un stop del 10% por acción dentro del mes, sobre la cartera de momentum, reduce la peor pérdida mensual (EW) de −49.79% a −11.36%. Los rendimientos medios reportados difieren según la versión: 1.01%→1.73% mensual según un resumen, y 0.99%→1.93% (stop del 15%) según CXO **(NO VERIFICADO contra el PDF)**. Las cifras son brutas de costos. | El stop sirve sobre todo para **cortar colas** en una estrategia que *ya tiene* edge y crashes. No convierte en rentable una estrategia sin edge. |
| **Lo & Remorov (2017)**, "Stop-loss strategies with serial correlation, regime switching, and transaction costs", *JFM* 34:1–15, DOI 10.1016/j.finmar.2017.02.003 ([MIT DSpace](https://dspace.mit.edu/handle/1721.1/107017)) | En una muestra amplia de acciones de EE. UU., **los stops ajustados rinden menos que buy-and-hold por exceso de costos de transacción**. Solo superan a buy-and-hold en activos con autocorrelación suficientemente alta. Reducen el riesgo a la baja, "pero no sustancialmente". | Es el caso exacto de un scalper con spread: entre más ajustado el stop y más frecuente el trading, más se come el costo. |

**Diagnóstico de autocorrelación con mis datos** (Binance 1m, ago–oct 2026; script en `scripts/stops_study.py`):

- BTC: autocorrelación de lag 1 de +0.009 (1m) y −0.015 (5m); razón de varianzas VR(15)=0.95 y VR(60)=0.96.
- ETH: VR(15)=0.93 y VR(60)=0.92.

Es decir, hay **ligera reversión a la media** intradía, no momentum. Según la literatura, en ese régimen los stops y trailings ajustados no deberían añadir esperanza. Mis backtests son consistentes con eso: el breakout de 20 barras tiene esperanza bruta negativa (−0.065R a costo 0 en BTC 5m).

---

## 2. Break-even: cuándo ayuda y cuándo perjudica (MAE/MFE)

**Marco MAE/MFE.** Sweeney formalizó la idea: el MAE (*Maximum Adverse Excursion*) de las **operaciones ganadoras** indica cuánto "respiran" antes de funcionar ([Sweeney, *Maximum Adverse Excursion*, Wiley 1997](https://gov.wiley.com/WileyCDA/WileyTitle/productCd-0471141526.html)). La heurística práctica es colocar el stop más allá del percentil 75–90 del MAE de las ganadoras ([MQL5, analizador MAE/MFE](https://www.mql5.com/en/articles/23245); [LuxAlgo](https://www.luxalgo.com/library/concept/mae-mfe-distributions/)). Los percentiles son heurísticas de practicantes, no resultados de Sweeney (NO VERIFICADO en el libro). La misma lógica aplica al BE: **la distancia entre el disparador del BE y el nivel de BE debe ser mayor que el retroceso típico de las ganadoras**. Si no lo es, el BE recorta ganadoras.

**Teoría (paseo aleatorio, objetivo en b y BE en 0).** Si la operación ya tiene un MFE de x, la probabilidad de regresar a BE antes del objetivo es (b−x)/b. Con b = 1.5 ATR y BE disparado en x = 0.5, el **67%** de esas operaciones terminan en scratch. La esperanza bruta no cambia: solo se cambian ganadoras de +1.5 por scratches de 0 y perdedoras de −1.5 por 0, en proporciones que se compensan.

**Medición empírica** (5m, SL = TP = 1.5 ATR, camino de 1m, tope de 180 min):

| | MAE de ganadoras p50 / p75 / p90 (ATR) | P(regresa a 0 antes del TP \| MFE ≥ 0.5) | Ídem \| MFE ≥ 1.0 |
|---|---|---|---|
| BTC aleatoria | 0.41 / 0.85 / 1.20 | 0.59 (teoría 0.67) | 0.34 (0.33) |
| BTC breakout | 0.34 / 0.83 / 1.18 | 0.61 | 0.40 |
| ETH aleatoria | 0.43 / 0.87 / 1.19 | 0.62 | 0.36 |
| ETH breakout | 0.49 / 0.90 / 1.26 | 0.63 | 0.42 |

Lectura:

- El **p75 del MAE de las ganadoras ≈ 0.85 ATR**. Un BE disparado en +0.5 ATR deja el stop a solo 0.5 ATR del precio, por debajo del retroceso típico de una ganadora. **Mover pronto convierte ganadoras en scratches**.
- Disparar en ≥ +1.0 ATR deja ≥ 1.0 ATR de aire. Solo un ~35–42% de las operaciones que llegan ahí regresan a 0, cerca del valor teórico.
- En el breakout, la probabilidad de regresar después de +1.0 ATR (0.40–0.42) es **mayor** que en un paseo aleatorio (0.33). Es consistente con la reversión a la media: los breakouts tienden a devolverse.

**Cuándo ayuda el BE:**

- Cuando el edge se concentra en los primeros minutos (momentum de corto plazo real).
- Cuando el objetivo es bajar varianza o drawdown, no subir la esperanza.
- Para limitar la pérdida ante gaps de noticias.

**Cuándo perjudica:**

- Con disparadores menores al p75 del MAE de las ganadoras.
- Cuando el nivel "BE + costos" no cubre el **deslizamiento** de la orden stop.
- Cuando el costo por re-entrada es alto (si el bot re-entra después de un scratch, paga el spread otra vez).

---

## 3. Métodos de trailing y salidas parciales

- **ATR / Chandelier (Le Beau).** El stop se coloca a k·ATR por debajo del máximo del periodo. El default de gráficas es 22 periodos y k = 3 ([StockCharts](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/chandelier-exit), [Barchart](https://www.barchart.com/education/technical-indicators/chandelier-exit)). Los practicantes usan k entre 2.5 y 3.5 ([Incrediblecharts](https://www.incrediblecharts.com/indicators/chandelier_exits.php)). En el uso original se colgaba del máximo *desde la entrada* ([LuxAlgo](https://www.luxalgo.com/library/concept/chandelier-stop.md), NO VERIFICADO contra Le Beau). Para el bot conviene la variante "máximo desde la entrada − k·ATR congelado al entrar": no se afloja si el ATR sube.
- **Estructura (swing high/low).** El stop va debajo del último mínimo de swing confirmado, menos un colchón (≥1 spread y 0.25 ATR). A 1–5 min suele quedar a <1 ATR: equivale a un trailing ajustado y hereda sus problemas de costos.
- **Parabolic SAR (Wilder, 1978).** Acelera hacia el precio con el tiempo: AF de 0.02 a 0.20 (NO VERIFICADO). En mercados laterales salta de lado a lado. No encontré evidencia seria a favor en horizontes de minutos.
- **Trailing porcentual.** Es una distancia fija en %. Ignora el régimen de volatilidad y es peor que el ATR cuando la volatilidad intradía cambia 3× entre sesiones (ver `scripts/hourly_vol_output.txt`: BTC hace 9–10 bps por vela de 1m en la apertura de EE. UU. contra 3–4 bps en Asia).
- **Candados escalonados.** Al llegar a +1.0 ATR el stop pasa a BE+costos, a +1.5 se asegura +0.5, a +2.0 se asegura +1.0, y así. Ventaja: **menos modificaciones de la orden** (límites de la API, §4).
- **Salida parcial (scale-out).** Cerrar 50% en +1 ATR y dejar el resto con la regla original equivale a tener **dos posiciones de 0.5** con salidas distintas. Por linealidad, E[scale-out] = 0.5·E[salida 1] + 0.5·E[salida 2] ≤ max(E1, E2). Reduce la varianza porque diversifica la salida, pero **no puede superar a la mejor salida pura**. En un CFD sin comisión, el parcial no añade costo de spread (el spread se paga por unidad). La evidencia de practicantes en trend following muestra que **todas** las combinaciones de parciales probadas redujeron el rendimiento total ([Enlightened Stock Trading](https://enlightenedstocktrading.com/trend-following-profit-targets-do-they-work)). Contar los stop-outs completos como −1R es indispensable para no autoengañarse ([The Right Trader](https://therighttrader.com/learn/risk-management/partial-profit-taking)).

---

## 4. Restricciones de microestructura y de Capital.com

**Ruido en relación con el spread** (medianas; Binance ago–oct 2026; Yahoo para oro, índices y FX):

| Instrumento (proxy) | Rango de 1m p50 | ATR14 1m | ATR14 5m | Spread supuesto Capital.com (NO VERIFICADO) | ATR1m / spread | 5×spread (piso de stop) |
|---|---|---|---|---|---|---|
| BTC (BTCUSDT) | 3.1 bps | 3.5 | 10.9 | ~3 bps | ~1.2 | 15 bps ≈ 1.4 ATR5m |
| ETH (ETHUSDT) | 4.9 | 5.5 | 15.4 | ~5 bps | ~1.1 | 25 bps ≈ 1.6 ATR5m |
| Oro (GC fut., PAXG) | 3.95 (GC) | 4.35 | 9.85 | ~1 bp | ~4 | 5 bps ≈ 0.5 ATR5m |
| US100 (NQ fut.) | 4.6 | 5.0 | 7.9* | ~1 bp | ~5 | 5 bps |
| US500 (ES fut.) | 2.6 | 2.7 | 4.8* | ~1 bp | ~2.7 | 5 bps |
| EUR/USD | ~0** | 0.71 | 1.72 | ~0.6 bps | ~1.2 | 3 bps ≈ 1.7 ATR5m |
| GBP/USD | ~0** | 0.67 | 1.83 | ~1 bp | <1 | 5 bps ≈ 2.7 ATR5m |

\* Incluye la sesión nocturna (por eso la mediana es baja). \*\* Las velas de 1m de FX en Yahoo tienen muchos precios repetidos; el dato de 1m es poco fiable. Los datos de Yahoo de 1m cubren solo unos 7 días, y los de 5m, unos 60 días.

**Conclusión:** en cripto y FX, el ATR de 1m es ≈ al spread. Un trailing de 1×ATR(1m) es pura fricción. **La distancia mínima útil del trailing es ~max(3–5×spread, 1×ATR(5m))**. En oro e índices hay más margen (ATR1m de 3 a 5 veces el spread).

**Reglas de Capital.com (API pública, [open-api.capital.com](https://open-api.capital.com/); copia local en `dl/docs.txt`):**

- `GET /api/v1/markets/{epic}` devuelve `dealingRules` con `minStopOrProfitDistance`, `maxStopOrProfitDistance`, `minStepDistance`, `minGuaranteedStopDistance`, `minDealSize`, `minSizeIncrement` y `trailingStopsPreference`. Cada campo tiene la forma `{unit, value}` y la unidad puede ser `PERCENTAGE` o `POINTS`. El ejemplo de la documentación (SILVER) muestra `minStopOrProfitDistance = 0.01 %`, `maxStopOrProfitDistance = 60 %` y **`trailingStopsPreference: "NOT_AVAILABLE"`**. Los valores reales de los 7 instrumentos **no se pudieron consultar sin sesión** (la API pública responde `error.null.client.token`). El bot debe leerlos al arrancar y validarlos en cada modificación **(NO VERIFICADO por instrumento)**.
- El trailing nativo usa `trailingStop: true`, que **requiere `stopDistance`** y **no es compatible con `guaranteedStop`** (los stops garantizados tampoco se permiten en modo hedging). La respuesta de sesión incluye el flag `trailingStopsEnabled` (en el ejemplo es `false`), así que el trailing nativo puede estar deshabilitado a nivel cuenta. La docs no especifica una distancia mínima de trailing ni su granularidad. En IG, por analogía, existe un "step" mínimo separado ([IG help](https://www.ig.com/en/help-and-support/cfds/orders--stops-and-limits/how-do-i-add-a-trailing-stop-to-an-open-position)); en Capital.com eso queda **(NO VERIFICADO)**.
- **Límites de tasa:** 10 solicitudes/s por usuario; 1 cada 0.1 s al abrir posiciones o crear órdenes; 1000 por hora en `POST /positions` en Demo; sesión de 10 minutos. **Mover el stop "cada tick" en 7 instrumentos puede chocar con el límite.** Conviene actualizar solo al cruzar umbrales (escalones ≥ 0.25 ATR o ≥ 1 spread, al cierre de la vela de 1m) y con *debounce*.
- **Lado del precio:** en un CFD, el stop de un largo se dispara con el bid y el de un corto con el ask (convención estándar, NO VERIFICADO en la docs de Capital.com). Si el largo entró al ask, un stop exactamente en ese precio (evaluado contra el bid) ya neutraliza el spread; si el bot registra la entrada a mid, el BE neto es mid + ½ spread. En ambos casos hay que sumar el **colchón de deslizamiento**.

---

## 5. Mini-estudio empírico

**Datos:** Binance spot 1m de BTCUSDT y ETHUSDT, del 1 de agosto al 31 de octubre de 2026 (unas 132 mil velas cada uno, en `data/binance/`). Como réplica gruesa, también Yahoo 5m de GC, NQ y EURUSD (~60 días, en `data/yahoo/`).

**Scripts** (`/tmp/claude-0/-home-user-README/82cdbbb4-ddee-5e71-af10-eeafa19fca7d/scratchpad/scripts/`): `stops_study.py` (motor; salida `stops_study_output.txt`), `paired_and_yahoo.py` (diferencias pareadas y Yahoo; `paired_output.txt`), `validate_rw.py`, `validate_iid.py`, `validate_iid2.py` (validación en paseo aleatorio).

**Diseño.** *Entradas aleatorias* (dirección por volado, momento al azar): aíslan la salida; por construcción no hay edge bruto, así que las salidas solo pueden redistribuir. *Breakout*: cierre fuera del máximo/mínimo de 20 barras, enfriamiento de 20 barras; prueba la interacción entrada-salida. ATR14 de la temporalidad de señal (1m o 5m) congelado al entrar; **trayectoria siempre en velas de 1m**. Supuestos conservadores intravela: stop antes que objetivo/parcial; BE/trailing se actualizan al cierre de la vela de 1m; gap → fill en apertura. Costo round-trip (spread): BTC 3 bps, ETH 5 bps (NO VERIFICADO vs spreads en vivo; sensibilidad 0 y 5 bps); oro y NQ 1 bp; EURUSD 0.6 bps. Deslizamiento de 0.5× spread en cada salida por stop. Piso: 1.5·ATR ≥ 5·costo. Tope de tiempo: 60 min (señal 1m) / 180 min (señal 5m). R = 1.5·ATR. IC95 por bootstrap de bloques diarios.

**Políticas:** (a) SL = TP = 1.5 ATR; (b) (a) + BE+costos en +0.5 ATR; (c) BE en +1.0; (d) BE en +1.5 (≈ nunca); (e1/e2/e3) BE en +1.0 y luego trailing desde el máximo a 1.0/2.0/3.0 ATR, sin TP; (e4) trailing de 1.0 desde el inicio, TP 3; (f1) parcial 50% en +1 ATR; (f2) f1 + BE en el resto; (g) escalones de 0.5 ATR, TP 3.

**5.1 Validación (lo más importante de esta sección).** En un paseo aleatorio sintético (iid, 30 subpasos por vela), la esperanza bruta debería ser 0 para todas las políticas. El motor da ≈0 para (a), (d) y (f), pero **+0.06R para el trailing** y +0.045R para los escalones. Este sesgo **escala con 1/√subpasos**: +0.135R con 5 subpasos, +0.051R con 30 y +0.008R con 300. Coincide con el *overshoot* teórico de ≈0.583·σ_paso, la corrección de continuidad de Broadie, Glasserman y Kou (1997) para barreras discretas. Causa: llenar el stop exactamente en su nivel cuando en realidad el precio "salta". **Las políticas que salen por stop casi siempre (trailing) se ven artificialmente bien en backtests de OHLC sin deslizamiento.** En datos reales sin deslizamiento, el trailing de BTC 5m "gana" +0.09R a costo 0; casi todo ese margen es este artefacto, más el ruido.

**5.2 Resultados principales** (deslizamiento de 0.5× spread, piso de ATR; tablas completas en `stops_study_output.txt`).

*BTC 5m, entradas aleatorias, costo de 3 bps (N = 8,768; ATR efectivo 10.8 bps; costo/R = 0.185):*

| Política | E[R] neta | E[bps] | σ(R) | Win | % ≥0 | Δ vs (a) [IC95] |
|---|---|---|---|---|---|---|
| a fijo 1.5/1.5 | −0.199 | −3.6 | 1.02 | 0.49 | 0.49 | — |
| b BE@0.5 | −0.179 | −3.3 | 0.74 | 0.23 | 0.23 | +0.007 [−0.007, +0.023] |
| c BE@1.0 | −0.193 | −3.5 | 0.92 | 0.39 | 0.39 | −0.000 [−0.011, +0.009] |
| d BE@1.5 | −0.200 | −3.6 | 1.02 | 0.49 | 0.49 | ≈0 |
| e1 BE@1 + trail 1.0 | −0.175 | −3.1 | 1.06 | 0.43 | 0.43 | +0.014 [−0.005, +0.033] |
| e2 BE@1 + trail 2.0 | −0.167 | −3.0 | 1.30 | 0.26 | 0.26 | +0.024 [−0.001, +0.057] |
| e3 BE@1 + trail 3.0 | −0.167 | −3.0 | 1.43 | 0.20 | 0.20 | — |
| f1 parcial 50% | −0.202 | −3.6 | 0.90 | 0.50 | 0.50 | −0.008 [−0.014, −0.001] |
| f2 parcial + BE | −0.198 | −3.6 | 0.87 | 0.59 | 0.59 | −0.008 [−0.018, +0.002] |
| g escalones | −0.177 | −3.2 | 1.05 | 0.39 | 0.39 | +0.016 [−0.002, +0.033] |

Nota: las diferencias de la columna Δ provienen de una corrida pareada aparte (`paired_output.txt`), con otra muestra aleatoria de entradas. Por eso no coinciden exactamente con la resta de las E[R] de la tabla.

*Breakout de 20 barras en 5m (Δ vs (a) [IC95]):*

- **BTC** (N = 875; E(a) = −0.237R): BE@0.5 +0.022 [−0.024, +0.064]; trail 1.0 −0.013; parcial +0.000. Nada es significativo.
- **ETH** (N = 841; E(a) = −0.244R): BE@0.5 −0.028; trail 1.0 −0.021; trailing de 1.0 desde el inicio −0.048 [−0.101, +0.003]. Nada es significativo.
- **NQ** (Yahoo 5m, N = 388): BE@1 −0.051 [−0.096, −0.008]; trail 1.0 −0.079 [−0.140, −0.011]; trail 2.0 −0.169 [−0.370, −0.024]. **El trailing perjudica de forma significativa** (índice con reversión intradía).
- **EURUSD** (N = 518): trail 1.0 +0.088 [+0.009, +0.170]; parcial + BE +0.068 [+0.016, +0.130]. Está al borde, con N pequeño y muchas pruebas a la vez: es probable que sea ruido.
- **Oro** (N = 389): trail 2.0 +0.079 [−0.025, +0.185]. No es significativo.

*Señal y ATR de 1m (BTC y ETH):*

- **Sin piso:** el costo/R mediano es 0.57–0.6 y E[R] ≈ **−1.3 a −1.4R** por operación (las ventanas de ATR muy bajo inflan la media).
- **Con piso** (stop ≥ 15 bps en BTC y ≥ 25 bps en ETH, aplicado en el ~95% de los casos): E ≈ −0.21 a −0.27R. En la práctica eso convierte el stop de 1m en un stop fijo en bps.

*Sensibilidad (BTC 5m, entradas aleatorias):*

- A costo 0, todas las políticas quedan entre −0.003 y +0.09R. Los valores positivos aparecen solo en las políticas de trailing y escalones, que son las que tienen el artefacto de §5.1.
- Con 5 bps, todas quedan entre −0.24 y −0.25R.
- Sin deslizamiento (3 bps), el BE@0.5 sube su % ≥0 de 0.23 a **0.68** y el trailing parece 0.05R mejor que (a). Ambos efectos desaparecen al modelar el deslizamiento.

**Máximo drawdown** (R acumulado; dominado por la deriva del costo y el traslape): en BTC 5m aleatorio va de 1,510R (e2) a 1,770R (f1) sobre 8,768 operaciones, y sigue a la esperanza.

**Lectura honesta:**

1. Con entradas sin edge, **ninguna salida crea edge**. El efecto dominante es el costo/R; las salidas mueven la esperanza ±0.02R, dentro del ruido y del sesgo del modelo.
2. Lo que sí cambia de forma robusta es la **forma**. El BE temprano baja la σ de 1.02 a 0.74 y el win rate de 0.49 a 0.23. El trailing ancho sube la σ y la cola derecha, con win rate de 0.20–0.26. El parcial baja la σ un 12% con una esperanza igual o ligeramente menor.
3. Con entradas breakout no hay evidencia de que el BE o el trailing ayuden en cripto, y hay evidencia en contra en NQ. Es coherente con VR < 1, es decir, con Kaminski & Lo y con Lo & Remorov.
4. **Limitaciones:** OHLC y no ticks (orden intravela desconocido, tratado de forma conservadora); Binance spot como proxy de los CFD; spreads supuestos y constantes (se amplían en noticias y rollover); solo 3 meses; Yahoo 5m es demasiado grueso para resolver BE/trailing dentro de la vela.

---

## 6. Política por defecto recomendada (a revalidar en la Etapa 2)

**Reglas comunes del Stop Manager:**

1. **Stop inicial:** d₀ = max(k_SL·ATR14(5m), 5·spread_actual, minStopOrProfitDistance del epic, convertido a precio).
2. **BE + costos:** se dispara cuando el MFE llega a ≥ max(1.0·ATR5m, p75 del MAE de las ganadoras de la propia estrategia). El nivel es el BE neto de spread (ver §4, lado del precio) + colchón de deslizamiento (≥0.5·spread o 1–2 ticks).
3. **Trailing tipo Chandelier "desde la entrada":** stop = max(stop, MFE_máx − k_tr·ATR_entrada). Se activa después del BE y se evalúa al **cierre de cada vela de 1m**, no tick por tick. Solo se envía `PUT /positions` si la mejora es ≥ max(0.25·ATR5m, 1·spread, minStepDistance).
4. **Candados escalonados como alternativa de bajo tráfico** a la API.
5. **Tope de tiempo:** cierre por tiempo cuando se agota el horizonte del scalping.
6. **Sin cierre parcial por defecto.** Solo usarlo si el objetivo es bajar la varianza o el drawdown y se acepta un costo de esperanza ≤0.01R.
7. **Trailing nativo de Capital.com solo si** `trailingStopsPreference` lo permite y `trailingStopsEnabled = true`. De lo contrario, usar un trailing "sintético", modificando el `stopLevel`.
8. **Backtest:** siempre con deslizamiento en los stops.

| Familia | SL inicial | BE (disparador / nivel) | Trailing | Notas | Grilla para la Etapa 2 |
|---|---|---|---|---|---|
| **Cripto** (BTC, ETH) | 1.5·ATR5m, piso de 5×spread (≈15 / 25 bps) | +1.0 ATR5m / BE neto + colchón de 0.5 spread | Activo después de +1.0; 2.0·ATR5m | Spread ≈ ATR1m: **nunca escalar el stop con ATR1m**. Ampliar en la apertura de EE. UU. | k_SL {1.0, 1.5, 2.0}; BE {0.75, 1.0, 1.5, nunca}; k_tr {1.0, 1.5, 2.0, 3.0}; activación {1.0, 1.5}; tope {30, 60, 120, 180} min; colchón {0.25, 0.5, 1.0}·spread |
| **Oro** (XAU) | 1.5·ATR5m (piso de 5×spread ≈ 5 bps) | +1.0 ATR5m / + spread + colchón | 2.0·ATR5m después de +1.0–1.5 (indicio +0.08R, no significativo) | Costo/R bajo (~0.07): más libertad. Riesgo de gap en datos macro, así que modelar deslizamiento de 1–2× spread en noticias. | Igual que cripto, más un filtro de noticias {sí, no} |
| **Índices** (US100, US500) | 1.5·ATR5m | **Tardío**: +1.5 ATR o nunca | **Ninguno o muy ancho** (≥3 ATR). En NQ el trailing de 1–2 ATR perdió entre 0.08 y 0.17R (significativo) | Reversión intradía: preferir SL/TP fijos + tope de tiempo. Separar la apertura del cash (9:30 ET) del resto. | BE {1.0, 1.5, nunca}; k_tr {2.0, 3.0, ninguno}; TP {1.0, 1.5, 2.0}; tope {15, 30, 60} min; sesión {cash, extendida} |
| **FX** (EUR/USD, GBP/USD) | 1.5·ATR5m, piso de 5×spread (≈3 bps EUR, ≈5 bps GBP) | +1.0 ATR5m | 1.0–1.5·ATR5m después de +1.0 (indicio +0.09R en EURUSD breakout, al borde) | GBP: ATR1m < spread, así que se requieren horizontes ≥5m. Evitar el rollover y los spreads ampliados. | k_SL {1.5, 2.0}; BE {0.75, 1.0, 1.5}; k_tr {1.0, 1.5, 2.0}; parcial {0, 50% @1 ATR}; tope {30, 60, 120} min |

**Criterio de aceptación para la Etapa 2.** Una regla de gestión solo entra si mejora la E[R] neta sobre (a) con un IC95 (bootstrap por días) que excluya 0, y además:

- con deslizamiento modelado;
- fuera de muestra (walk-forward);
- tras corregir por pruebas múltiples.

Si no cumple, se elige la política por **forma** (σ, drawdown, % ≥0) según el objetivo de riesgo, sabiendo que la esperanza la pone la **entrada**, no el stop.
