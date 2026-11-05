# Scalper DEMO para Capital.com: guía desde el celular

Es un bot que opera solo, 24/7, en tu **cuenta DEMO** de Capital.com. Corre en un servidor en la nube: no
necesitas computadora ni Windows. Lo ves en vivo desde el celular (dashboard) y te avisa por Telegram.

> **Antes de empezar, lee esto.** La investigación (`RESEARCH.md`) y el backtest (`RESULTADOS.md`) dicen que
> **$100 → $10,000 en una noche no es posible** sin una probabilidad casi segura de quemar la cuenta. Después
> de probar 7 estrategias en 7 instrumentos con costos reales, sobrevivió una sola: momentum intradía en el
> US100. Hace unas 3–4 operaciones por semana y su expectativa realista va de +4% a +17% al año con riesgo
> normal. Esto es para aprender y medir en demo; no es una máquina de dinero.

---

## Lo que vas a hacer (unos 20 minutos, todo en el celular)

1. Sacar la API key de Capital.com en modo demo.
2. Crear tu bot de Telegram.
3. Subir el bot a Railway (la nube), pegar tus claves y abrir el dashboard.
4. Vincular Telegram.

### 1. API key de Capital.com (demo)

1. En el navegador del celular entra a **capital.com** e inicia sesión. Si la página móvil no muestra los
   ajustes, activa "Ver versión de escritorio" en el navegador.
2. Cambia a tu cuenta **Demo** con el selector de cuenta, arriba.
3. Activa la verificación en dos pasos: **Configuración → Seguridad → Autenticación de dos factores (2FA)**.
   Sin 2FA no te deja crear la API key.
4. Ve a **Configuración → Integraciones API → Generar nueva clave**. Ponle un nombre (por ejemplo
   `scalper`) y una **contraseña personalizada nueva**, distinta a la de tu cuenta.
5. Copia la **API key**. Solo se muestra una vez; guárdala en las notas del celular mientras terminas.

Vas a necesitar tres cosas: la **API key**, tu **correo** de Capital.com y esa **contraseña personalizada**.

> La misma API key funciona en demo y en real; Capital.com no tiene claves "solo demo". Por eso el bot tiene
> la URL de la demo fija en el código y **se niega a arrancar** si alguien configura otra.

### 2. Tu bot de Telegram

1. En Telegram busca **@BotFather** (tiene palomita azul) y mándale `/newbot`.
2. Ponle un nombre (por ejemplo `Mi Scalper`) y un usuario que termine en `bot` (por ejemplo `mi_scalper_bot`).
3. BotFather te da un **token** con forma `123456789:AA…`. Cópialo.

### 3. Subirlo a Railway (corre 24/7 en la nube)

Railway cuesta unos **US$5 al mes** (plan Hobby); revisa el precio vigente en railway.com/pricing. Lo elegí
porque se configura completo desde el navegador del celular, reinicia el bot solo si se cae y le da una
dirección web segura (https) para el dashboard. Si quieres algo gratis, al final hay una alternativa con
Oracle Cloud, que es más laboriosa.

1. Entra a **railway.com** → **Login** → **Continue with GitHub** (con tu cuenta de GitHub, la del repo
   `README`).
2. **New Project** → **Deploy from GitHub repo** → elige **Alexsnri/README**. Si te pide permiso para ver el
   repositorio, dáselo.
   - Mientras el código siga en la rama de trabajo: en el servicio entra a **Settings → Source → Branch** y
     elige `claude/scalper-capital-demo`. Cuando la juntes con `main`, cámbiala a `main`.
   - Railway lee `railway.json` y construye el bot solo.
3. En el servicio abre **Variables** y agrega estas cinco:

   | Variable | Qué va |
   |---|---|
   | `CAPITAL_API_KEY` | la API key del paso 1 |
   | `CAPITAL_IDENTIFIER` | tu correo de Capital.com |
   | `CAPITAL_API_PASSWORD` | la contraseña personalizada del paso 1 |
   | `TELEGRAM_TOKEN` | el token de BotFather |
   | `DASHBOARD_PASSWORD` | una contraseña que inventes para entrar al dashboard |

4. **Disco para la memoria del bot (importante):** en el proyecto toca **+ Create → Volume**, conéctalo al
   servicio y pon **Mount path** `/data`. Ahí se guardan posiciones, stops, aprendizaje y reportes. Sin
   volumen, cada redeploy empieza de cero.
5. **Dirección web:** en el servicio entra a **Settings → Networking → Generate Domain**. Te da algo como
   `https://readme-production-xxxx.up.railway.app`.
6. Abre esa dirección en el celular, escribe tu `DASHBOARD_PASSWORD` y en el menú del navegador elige
   **"Agregar a pantalla de inicio"**. Queda como una app.

Los nombres de los botones de Railway pueden cambiar un poco con el tiempo; la idea es la misma.

### 4. Vincular Telegram

Abajo, en el dashboard (tarjeta **Control** o **TÚ**), aparece un código de 6 dígitos. Mándale a tu bot de
Telegram `/vincular 123456` con tu código. Desde ese momento te llegan:

- cada operación cerrada, con su ganancia o pérdida y el balance de Capital.com;
- cada breaker (rachas de pérdidas, stop diario o semanal);
- errores graves (como máximo uno de cada tipo cada 10 minutos);
- un resumen diario a las **8:00 a. m.** (hora de CDMX).

Comandos (solo responde a tu chat):

| Comando | Qué hace |
|---|---|
| `/estado` | balance, posición abierta y estado |
| `/pausa` | no abre nada nuevo; las posiciones abiertas siguen con su stop en el servidor |
| `/reanudar` | vuelve a operar |
| `/perfil normal` · `/perfil agresivo` | cambia el riesgo |
| `/reporte` | resumen del día y acumulado, comparado contra el backtest |
| `/promover S1-US500` | pasa a vivo una estrategia que estaba en sombra (solo si el Learner la propone) |

---

## La primera vez que arranca

- **Ajusta la demo a $100.** La demo de Capital.com empieza con $1,000. Si la API lo permite, el bot la deja
  en $100 la primera vez. Si no puede, te avisa: en ese caso cambia el saldo de la demo en la app de
  Capital.com y reinicia el servicio en Railway.
- **Lee las reglas de cada mercado** (tamaño mínimo, distancia mínima del stop, margen), baja 25 días de velas
  de 5 minutos y revisa contra Capital.com que no haya posiciones sin stop.
- Opera con **0.5% de riesgo** durante los primeros 300 trades (fase de "arranque") y después sube a 1%.

## Cómo leer el dashboard

- **Arriba:** el badge **DEMO** siempre visible; el **balance que reporta Capital.com**; "no realizado" va
  aparte; la franja horaria actual.
- **Agentes:** una tarjeta por agente, con su estado.
  - **Scout** busca setups. **Filter** aplica 9 reglas duras (una falla y el setup se descarta).
  - **Analyst** da un score de 0 a 100. **Learner** aprende qué estrategia funciona.
  - **Executor** manda las órdenes. **Risk** aplica el riesgo fijo y los breakers. **Stop Manager** mueve el
    stop, solo a favor. **Logger** escribe todo.
  - Los cinco agentes de información (Trend, Big Money, Retail, News, Correlation) muestran **OFF** cuando el
    backtest dijo que no ayudan y **GUARDIA** cuando funcionan como protección (News).
- **Flujo en vivo:** los últimos setups y hasta dónde llegó cada uno. Los círculos cuentan cuántos vio,
  descartó, evaluó y operó cada agente hoy.
- **Filter:** la última revisión, regla por regla, con su valor.
- **Analyst:** el medidor del score y el desglose de cada parte. Si el score queda en 70 o más, el setup pasa
  a Risk y luego a Executor.
- **Posición:** la gráfica de 1 minuto con entrada, stop (línea roja), objetivo y cada movimiento del stop
  (puntos naranjas), más tamaño, riesgo en dólares, spread y slippage reales, y la ganancia en dólares y en R.
  Si es una posición "SOMBRA", es de papel: el bot está probando una estrategia sin arriesgar dinero.
- **Lectura del mercado:** lo que dice cada agente de información sobre el instrumento.
- **Learner:** cada estrategia (brazo), si está viva o en sombra, cuántos trades lleva, la probabilidad de que
  gane después de costos y su multiplicador de riesgo. Debajo, los últimos cambios con su razón.
- **Equity, Estadísticas y Real vs backtest:** P&L ya con spread y slippage, mejor y peor trade, drawdown, y
  cómo va la realidad contra lo que predijo el backtest.
- **tail -f night.log:** el log en vivo, con formato `HH:MM EVENTO INSTRUMENTO detalle`.
- **Control:** pausar o reanudar, cambiar el perfil y ver el reporte.

## Horario del bot (hora de CDMX, invierno de EE. UU.)

| Hora CDMX | Qué hace |
|---|---|
| 18:00–02:00 | Asia: US100 (y GOLD si se habilita) a medio riesgo |
| 02:00–07:25 | Londres |
| 07:25–07:40 | pausa por los datos de las 8:30 de Nueva York |
| 07:40–11:00 | ventana principal (aquí entra S1-US100, desde las 9:00 CDMX) |
| 11:00–14:45 | tarde de Nueva York |
| 14:45–15:40 | solo administra las posiciones abiertas |
| **15:40–17:30** | **sin posiciones**: rollover, cobro nocturno y spreads máximos |
| viernes 15:40 → domingo 17:30 | cerrado |

Cuando EE. UU. cambia al horario de verano (desde el 14 de marzo de 2027), todo se recorre una hora antes. El
bot usa zonas horarias reales, así que no hay que tocar nada.

## Perfiles de riesgo (`config.yaml`)

| Perfil | Riesgo por trade | Stop diario | Riesgo estimado de perder ≥50% en un año |
|---|---|---|---|
| normal (recomendado) | 0.5% los primeros 300 trades, luego 1% | −6R | 0% |
| agresivo | 2% | −6R | 0.1% (ventaja 2022–26) a 1.2% (ventaja 2025–26); ~25% en un mes si la ventaja real fuera negativa |

En los dos perfiles:

- **Breakers:** 7 pérdidas seguidas pausan 2 horas y bajan a medio tamaño; 10 detienen el día.
- **Nunca** hay martingala, promedio a la baja ni más de una posición por instrumento.

## Si algo pasa

- **El proceso se cae:** Railway lo reinicia solo (`restartPolicyType: ALWAYS`). Si se queda colgado 5
  minutos, el watchdog interno lo reinicia. Al volver, lee el estado desde `/data` y lo verifica contra
  Capital.com.
- **Se pierde la conexión:** los stops viven **en el servidor de Capital.com**, así que te protegen aunque el
  bot esté apagado. Al reconectar, primero revisa que cada posición tenga su stop (y si falta, lo vuelve a
  poner) y después sigue operando.
- **La sesión de la API:** se renueva sola (ping cada 4 minutos y nuevo login si expira).
- **El dashboard dice "sin credenciales":** falta alguna de las tres variables de Capital.com en Railway.
- **"error.invalid.api.key":** la key está mal copiada o se generó en otra cuenta.
- **Demo cerrada:** Capital.com cierra las demos que pasan 2 semanas sin operar. El bot opera unas 3–4 veces
  por semana, así que no debería pasar mientras esté encendido.

## Reportes

- **Telegram:** `/reporte`, o el resumen diario de las 8:00.
- **Dashboard:** botón **Reporte**.
- Cada día se guarda `reports/AAAA-MM-DD.md` y un `acumulado.json` en el disco `/data`.

El reporte trae trades, W/L, P&L con costos, mejor y peor trade, drawdown, qué aprendió el Learner y la
comparación contra el backtest.

## Alternativa gratis: tu propio servidor (Oracle Cloud "Always Free")

Es más laboriosa, pero cuesta $0. Se puede hacer desde el celular:

1. Crea la cuenta en oracle.com/cloud/free. Te pide tarjeta para verificar, pero no cobra.
2. Crea una VM Ubuntu "Always Free" (Ampere).
3. Abre la consola SSH desde el navegador o desde una app como Termius.
4. Pega:

   ```
   curl -fsSL https://raw.githubusercontent.com/Alexsnri/README/main/scalper/deploy/install_vps.sh -o install.sh
   less install.sh      # revísalo antes
   bash install.sh
   ```

   El script instala Docker, te pide las credenciales una sola vez (las guarda en `.env`, con permisos solo
   para ti) y deja el bot arrancando solo cada vez que se prende el servidor. Abre el puerto 80 en la "Security
   List" de Oracle y entra a `http://IP-del-servidor/`.

   Hasta que juntes la rama con `main`, usa `BRANCH=claude/scalper-capital-demo bash install.sh`.

## Seguridad

- Las credenciales viven solo en las variables de Railway (o en `.env` en un VPS, que está en `.gitignore`).
  Nunca se imprimen, nunca se escriben en logs (hay un filtro que las borra) y nunca se mandan al dashboard.
- El dashboard pide contraseña, y Telegram solo obedece al chat vinculado.
- **Solo DEMO:** el bot se niega a arrancar si `CAPITAL_API_URL` o `CAPITAL_ENV` apuntan a otro entorno.

## Para desarrolladores

- **Tests:** `pytest tests` cubre Filter, Risk, tamaño de posición, Stop Manager, horario, candado DEMO y
  Learner.
- **Simulación local sin credenciales:** `BOT_SIM=1 SIM_START=2026-10-05 SIM_SPEED=300 DASHBOARD_PASSWORD=x
  python -m bot`. Necesita los datos del laboratorio.
- **Laboratorio:** `pip install -r lab/requirements.txt`, descargar datos con `lab/histdata.py` y
  `lab/binance_dl.py`, y correr `python -I lab/run_wf.py`.
