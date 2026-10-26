# Hydra: bot de trading autónomo para MT5 (Exness) con espejo en TradingView

Hydra opera solo en MetaTrader 5. Combina tres de las estrategias con más evidencia publicada, controla
el riesgo de forma automática y va ajustando cuánto arriesga en cada estrategia según sus propios resultados.

| Carpeta | Qué es |
|---|---|
| `mt5/Hydra.mq5` | El bot (Expert Advisor). Corre en MT5 conectado a tu cuenta Exness y abre/cierra operaciones solo. |
| `tradingview/Hydra.pine` | La misma lógica para TradingView: ves en el gráfico cada entrada, salida y stop. |
| `backtest/backtest.py` | El backtest de 21 años con el que se validó el sistema. |
| `RESULTADOS.md` | Resultados completos y el análisis del reto de $5,000 → $1,000,000. |

## Las estrategias

Los parámetros son los clásicos publicados, **sin optimizar sobre los datos**, para no engañarnos con un
backtest perfecto que luego no funciona.

1. **D: Breakout Donchian 55/20 (las Tortugas).** Compra al romper el máximo de 55 días (vende al romper
   el mínimo) si la EMA 50 está a favor de la EMA 200. Sale al romper el canal de 20 días o con un stop
   móvil de 2.5 ATR.
2. **T: Momentum de series de tiempo** (Moskowitz, Ooi y Pedersen, 2012; Hurst et al., *A Century of
   Evidence on Trend-Following*). Opera cuando al menos 3 de 4 horizontes (1, 3, 6 y 12 meses) apuntan a
   la misma dirección. Stop móvil de 3 ATR.
3. **M: Reversión RSI(2) de Connors.** En índices y metales con tendencia alcista (precio sobre la SMA 200),
   compra retrocesos fuertes (RSI de 2 días < 10) y vende al rebotar sobre la SMA 5.

Universo: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, XAUUSD, XAGUSD, USOIL, US500, USTEC, US30, DE30 y BTCUSD.
En índices no hay ventas en corto.

## Cómo "aprende"

Cada combinación estrategia × símbolo (por ejemplo "XAUUSD_D") lleva su historial de resultados en
múltiplos de R (ganancia ÷ riesgo inicial). Con 8 trades o más, su riesgo se multiplica entre **0.25x** y
**1.5x** según la expectativa de sus últimos 30 trades: lo que funciona recibe más capital y lo que deja de
funcionar recibe menos. Nunca llega a cero, así que sigue probando y puede recuperarse. El historial se
guarda en `Hydra_learning.csv` (carpeta común de MT5), así que no se pierde si reinicias.

En el backtest esto subió el rendimiento de 9.7% a 10.3% anual con 0.5% de riesgo, y de 9.8% a 11.2% con 1%.
Es una mejora modesta y real, no una IA que adivina el mercado.

## Control de riesgo (automático)

- El tamaño de cada operación se calcula para perder sólo el % elegido si salta el stop.
- Hay un tope de riesgo abierto total entre todas las posiciones.
- Si la cuenta cae más de 20% desde su máximo, opera a la mitad de riesgo.
- Si cae más del límite del modo, deja de abrir operaciones nuevas hasta recuperarse.
- Nunca usa más del 50% del margen libre en una operación.
- Todos los stops quedan puestos en el servidor del broker, así que protegen aunque se apague la PC.

| Modo | Riesgo por trade | Riesgo abierto máx. | Pausa por drawdown |
|---|---|---|---|
| Conservador | 0.5% | 6% | 25% |
| Normal | 1% | 10% | 35% |
| Reto $1M | 3% | 20% | 60% |
| **Turbo** (por defecto) | 4% | 25% | 85% |

Turbo es el modo que históricamente llegó más rápido a la meta (ver `RESULTADOS.md`). Arriesgar más que
eso no aceleró el crecimiento y sí hizo mucho más profundas las caídas. Los modos Reto y Turbo quedan
bloqueados en cuentas reales salvo que actives `InpAllowRetoOnReal` a propósito.

---

## Instalación paso a paso (Exness demo con $5,000)

> **No compartas tus contraseñas con nadie, tampoco conmigo.** No las necesito: el bot corre dentro de tu
> MT5 y tú inicias sesión ahí. Cualquier persona o programa que te pida la contraseña de tu bróker para
> "operar por ti" es una señal de alerta.

1. **Crea la cuenta demo.** En el Área Personal de Exness: *Abrir nueva cuenta → Demo → MT5*, tipo
   **Standard**, apalancamiento 1:200 o más, y saldo **5000 USD**. Anota el número de cuenta, el servidor
   (p. ej. `Exness-MT5Trial8`) y la contraseña.
2. **Instala MetaTrader 5** desde el Área Personal de Exness e inicia sesión con esa cuenta demo
   (*Archivo → Iniciar sesión en la cuenta de trading*).
3. **Copia el bot.** En MT5: *Archivo → Abrir carpeta de datos* → entra a `MQL5/Experts/` y pega
   `Hydra.mq5` ahí.
4. **Compílalo.** Abre MetaEditor (F4), abre `Hydra.mq5` y presiona **F7**. Debe decir `0 errors`.
5. **Muestra todos los símbolos.** En *Observación del mercado*, clic derecho → *Mostrar todo*.
   El bot detecta solo el sufijo de Exness (`EURUSDm`, etc.).
6. **Actívalo.** Abre **un solo** gráfico cualquiera (por ejemplo EURUSDm, D1) y arrastra *Hydra* desde el
   Navegador. En la pestaña *Común* marca *Permitir trading algorítmico*; en *Parámetros* deja
   `Modo = Turbo`. Presiona también el botón **Trading algorítmico** de la barra superior para que
   quede en verde.
7. **Listo.** En el gráfico aparece un panel con capital, drawdown, progreso a la meta y riesgo abierto. El
   bot revisa cada 30 segundos y opera una vez al día por símbolo, 60 minutos después de la apertura
   diaria del servidor, para evitar los spreads altos del cambio de día.

### Que opere 24/7

MT5 tiene que estar abierto para que el bot opere. Opciones:
- Dejar tu PC encendida (sin suspensión).
- **VPS de Exness**: gratis si cumples sus requisitos de depósito/volumen (ver Área Personal → VPS).
- **VPS de MetaQuotes**: en MT5, clic derecho sobre la cuenta → *Registrar un servidor virtual*
  (unos USD 10–15/mes). Migras el gráfico con el bot y corre en la nube.

### Ver cómo opera en TradingView

Exness no permite conectar la cuenta al panel de trading de TradingView, así que hay dos caminos
complementarios:
1. **Tus operaciones reales del bot**: entra a **Exness Terminal** (web) o a la app **Exness Trade**
   con la misma cuenta demo. Usan gráficos de TradingView y, como es la misma cuenta, deben mostrar las posiciones que abre el bot
   en MT5.
2. **La lógica del bot en TradingView**: en tradingview.com abre *Editor de Pine*, pega
   `tradingview/Hydra.pine`, guarda y *Añadir al gráfico*. Usa temporalidad **1D**. Verás cada señal,
   stop y salida, y en el *Probador de estrategias* el historial de cada mercado.

### Revisar resultados

- Pestaña *Historial* de MT5, o el diario `Hydra_journal.csv` en
  `C:\Users\<tú>\AppData\Roaming\MetaQuotes\Terminal\Common\Files\` (se abre en Excel).
- Pestaña *Expertos* de MT5: el bot escribe ahí cada orden y cada cosa que aprende.
- Puedes correr el bot en el *Probador de estrategias* de MT5 con datos de Exness (modelo "1 minuto OHLC").

### Si reinicias la demo

Pon `InpResetPeak = true` una vez para que el bot olvide el máximo de capital anterior. Si no, puede
creer que está en drawdown y pausarse.

---

## Repetir el backtest

```bash
python backtest/backtest.py <carpeta_con_json_de_yahoo> 0.5 1 2 3
```
La carpeta debe tener los JSON diarios de Yahoo Finance (`EURUSDX.json`, `GCF.json`, `GSPC.json`, ...).
