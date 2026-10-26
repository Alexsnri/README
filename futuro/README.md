# Futuro Yo

Mira tu cara a los 65 con IA que corre en tu teléfono, descubre cuánto tendrás para tu retiro y regresa cada día por tu racha y el reto diario. Gratis, sin registro y sin subir tu foto.

**Sitio:** https://alexsnri.github.io/README/futuro/ (después de activar GitHub Pages)

## Secciones

| Sección | Qué hace |
|---|---|
| Mi futuro | Simulador con CETES e inflación reales, tu foto envejecida (o un avatar), viaje en el tiempo, "mantén para ver tu cara de hoy", gráfica y carta de tu yo del futuro. |
| Hoy | Racha diaria con escudos, registro de un toque, antojómetro, casa del yo del futuro que sube de nivel, mapa de 5 semanas, cuenta regresiva a la quincena, recordatorios y misiones. |
| Reto | 5 preguntas al día, iguales para todo México, con cuadrícula para compartir y enlace para retar. |
| Más | La ciencia, preguntas frecuentes, fuentes y borrar mis datos. |

Tarjetas para historias (1080×1920): antes y después, mi futuro, nosotros (dos fotos) y mi racha.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `index.html`, `css/app.css` | La app. |
| `js/core.js` | Configuración (sitio, contacto, analítica), estado y cálculos. |
| `js/aging.js` | Envejecimiento de fotos con MediaPipe, dentro del teléfono. |
| `js/sim.js` | Simulador, gráfica, carta y portal. |
| `js/habits.js` | Racha, antojómetro, niveles y misiones. |
| `js/reto.js` | Reto diario. |
| `js/share.js` | Tarjetas para compartir. |
| `js/app.js` | Secciones, marca de instituciones, retos recibidos, tasas. |
| `models/` | Modelos de IA de rostro y cabello (Google MediaPipe, Apache 2.0). |
| `empresas.html` | Página de ventas para instituciones. |
| `plan.html` | Plan de negocio. |
| `marketing/` | Calendario de 30 días y plan de lanzamiento. |

## Versión con marca para instituciones

Agrega parámetros al enlace:

```
https://alexsnri.github.io/README/futuro/?marca=Tu%20Marca&color=2f6fed&cta=https%3A%2F%2Ftu-sitio.mx&cta_txt=Abre%20tu%20cuenta
```

`marca` (nombre, máx. 30 caracteres), `color` (hex de 6 dígitos), `cta` (solo `https://`), `cta_txt` (texto del botón). La marca se queda guardada en el navegador de la persona.

## Retos

El resultado del reto se comparte con `?reto=<número>&p=<aciertos>`. Quien lo abre ve "Te retaron" y juega el reto del día.

## Configuración (en `js/core.js`)

- `CONTACT_URL`: a dónde llegan las solicitudes de piloto. Hoy apunta a un formulario de GitHub Issues.
- `CF_ANALYTICS_TOKEN`: token de Cloudflare Web Analytics (gratis, sin cookies). Vacío = sin analítica.

## Automatizaciones

- `.github/workflows/futuro-pages.yml` publica `futuro/` en GitHub Pages en cada cambio y después de actualizar tasas.
- `.github/workflows/futuro-rates.yml` actualiza `data/rates.json` cada miércoles si existe el secreto `BANXICO_TOKEN`.

## Supuestos del cálculo

- Todo en pesos de hoy: tasa real = (1 + tasa nominal) / (1 + inflación) − 1, con capitalización mensual.
- Ingreso de retiro: regla del 4% anual. Días de retiro = valor futuro ÷ (lo que quieres recibir al mes ÷ 30.4).
- El reto diario usa un supuesto fijo de 3% real al año para que las respuestas sean iguales para todos.
- No incluye Afore, impuestos ni comisiones.
