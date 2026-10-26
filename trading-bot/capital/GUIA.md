# Hydra en Capital.com: sin PC, gratis y visible en TradingView

El bot corre solo en los servidores de GitHub una vez al día, gratis. Opera tu cuenta demo de
Capital.com por su API oficial. Como Capital.com se conecta directo con TradingView, ahí ves cada
operación en el gráfico.

Tú sólo haces 4 cosas, una sola vez (unos 10 minutos). **Las claves las pegas tú en GitHub, no se las
mandes a nadie, tampoco a Claude.**

## 1. Abre la cuenta demo de Capital.com (3 min)
1. Entra a capital.com, presiona **Registrarse** y crea tu cuenta con tu correo.
2. Dentro de la plataforma, cambia a la cuenta **Demo** (selector de cuenta, arriba).
   No tienes que ajustar el saldo: el bot lo pone en $5,000 la primera vez que corre.

## 2. Saca la llave de la API (3 min)
1. Activa la verificación en dos pasos: **Configuración → Seguridad → Autenticación de dos factores**.
2. Ve a **Configuración → Integraciones API → Generar nueva clave**.
3. Ponle un nombre (por ejemplo *hydra*) y una **contraseña personalizada** nueva, distinta a la de tu cuenta.
4. Copia la **API key** que aparece. Sólo se muestra una vez.

## 3. Pega las 3 claves en GitHub (2 min)
En el repositorio (github.com/Alexsnri/README): **Settings → Secrets and variables → Actions →
New repository secret**. Crea estos tres:

| Nombre | Valor |
|---|---|
| `CAPITAL_API_KEY` | la API key del paso 2 |
| `CAPITAL_IDENTIFIER` | el correo con el que entras a Capital.com |
| `CAPITAL_API_PASSWORD` | la contraseña personalizada del paso 2 |

Luego ve a la pestaña **Actions → Hydra bot → Run workflow → Run workflow** para que arranque ya. A partir de
ahí corre solo todos los días a las 00:15 hora de Ciudad de México.

## 4. Conecta TradingView para verlo operar (2 min)
1. En tradingview.com abre cualquier gráfico y, abajo, el **Panel de trading**.
2. Elige **Capital.com**, inicia sesión y, si te lo pregunta, selecciona la cuenta **Demo**.
3. En el gráfico de cada mercado (oro, US500, EURUSD...) vas a ver las posiciones del bot con su stop.

## Dónde ver cómo va
- **TradingView o la app de Capital.com**: posiciones abiertas y resultados en vivo.
- **GitHub, rama `hydra-state`, archivo `STATUS.md`**: capital, progreso a la meta, posiciones y últimos
  trades. `journal.csv` tiene el diario completo.
- **GitHub → Actions**: el registro de cada ejecución (qué revisó, qué abrió, qué cerró y qué aprendió).

## Ajustes opcionales
En **Settings → Secrets and variables → Actions → Variables** puedes crear:
- `HYDRA_MODE`: `turbo` (por defecto), `reto`, `normal` o `conservador`.
- `HYDRA_START`: capital inicial del reto (por defecto `5000`).
- `CAPITAL_ENV`: `demo` (por defecto) o `live`. En `live`, los modos turbo y reto quedan bloqueados.
