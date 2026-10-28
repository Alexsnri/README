# Quincy

Lo que te toca, cuándo te toca y cuánto te queda. Una app web gratis para trabajadores en México: cuánto puedes gastar hoy para llegar a la quincena, cuánto te toca por ley (aguinaldo, vacaciones, prima vacacional, PTU, finiquito y liquidación con los valores de 2026) cómo organizar tu tanda y cómo vivirá tu yo del futuro. Sin registro y sin servidores.

**Sitio:** https://alexsnri.github.io/README/quincy/

## Páginas

| Página | Qué es |
|---|---|
| `index.html` | Portada en 3D: partículas que cambian de forma con el scroll, con demos que funcionan. |
| `app.html` | La app: Hoy, Me toca, Tanda, Futuro, Reto y Más. |
| `aguinaldo/`, `finiquito/`, `vacaciones/`, `ptu/`, `tanda/`, `quincena/` | Páginas de búsqueda con calculadora, artículo y preguntas frecuentes. Se generan con `scripts/build_seo.py`. |
| `empresas.html` | Página de ventas para empresas e instituciones. |
| `plan.html` | Plan de negocio (no se indexa). |
| `marketing/` | Kit de lanzamiento (`marketing/kit.html`), guía paso a paso (`marketing/guia.html`), página para programar Instagram desde el celular (`marketing/programar.html`, con ZIP), 9 reels animados con voz y música (`marketing/video/animados/`, se generan con `scripts/reels/`), 3 carruseles (`marketing/carruseles/`), marca y logos (`marketing/marca/`, con SVG, PNG, portadas y ZIP), 8 reels, imágenes para Instagram (`ig/`), 12 posts, 5 historias, video vertical, textos (`posts.md`), calendario de 30 días y plan de lanzamiento. |

## Código

| Archivo | Para qué sirve |
|---|---|
| `js/core.js` | Configuración (sitio, contacto, analítica), estado, cálculos de dinero en el tiempo y utilidades. |
| `js/ley.js` | Cálculos de la Ley Federal del Trabajo y valores de 2026 (salario mínimo y UMA). **Actualizar cada enero y febrero.** |
| `js/quincena.js` | "Hoy": límite diario, gastos, "¿me alcanza?" y días en verde. |
| `js/derechos.js` | "Me toca": aguinaldo, vacaciones, PTU, finiquito y liquidación, calendario y checklist. |
| `js/sim.js`, `js/avatar.js` | "Futuro": simulador de retiro y avatar que envejece. |
| `js/reto.js` | Reto diario de 5 preguntas, igual para todos cada día. |
| `js/tanda.js` | Tandas: ruleta, calendario, enlace para el grupo y valor de cada turno frente a CETES. |
| `js/share.js` | Tarjetas para historias (futuro, días en verde, aguinaldo, ticket de la quincena y tanda). |
| `js/app.js` | Secciones, marca de empresas, retos recibidos y tasas. |
| `js/portada.js`, `css/landing.css` | Portada: calculadora de temporada (cambia sola por fecha; prueba otra con `?temporada=ptu`), cuenta regresiva y retícula bento. Sin three.js. |
| `js/compartir.js` | Compartir en 1 toque: WhatsApp con `?ref=wa`, tarjeta 1080×1920 para historias, Aguinaldo Wrapped, aviso al llegar con `?ref=` y recordatorios `.ics`. |
| `fonts/` | Unbounded, Figtree y JetBrains Mono (licencia OFL), servidas desde el sitio. |
| `scripts/build_og.js` | Genera las imágenes de vista previa (Open Graph 1200×630) de cada página en `img/og/`. |

## Pruebas

Los cálculos de ley tienen 35 pruebas. Para correrlas:

```
node quincy/scripts/test_ley.js
python3 quincy/scripts/build_seo.py   # regenera las páginas de búsqueda
```

## Versión con marca

```
https://alexsnri.github.io/README/quincy/app.html?marca=Tu%20Empresa&color=2f6fed&cta=https%3A%2F%2Ftu-sitio.mx&cta_txt=Abre%20tu%20cuenta
```

`marca` (máx. 30 caracteres), `color` (hex de 6 dígitos), `cta` (solo `https://`), `cta_txt` (texto del botón) y `ocultar=salida` para esconder la calculadora de finiquito y liquidación.

## Configuración (en `js/core.js`)

- `CONTACT_URL`: a dónde llegan las solicitudes de piloto. Hoy apunta a un formulario de GitHub Issues.
- `CF_ANALYTICS_TOKEN`: token de Cloudflare Web Analytics (gratis, sin cookies). Vacío = sin analítica.

## Automatizaciones

- `.github/workflows/quincy-pages.yml` publica `quincy/` en la rama `gh-pages` en cada cambio y avisa a los buscadores con IndexNow (la llave es `a47e56b41e4abf5e6d43f62e3de33615.txt`). Si el sitio no abre, en Settings → Pages elige "Deploy from a branch" → `gh-pages`.
- `.github/workflows/quincy-social.yml` publica en Instagram lo que marca `marketing/social/schedule.json` (13:37 y 20:07, hora de la Ciudad de México). Necesita el secreto `INSTAGRAM_TOKEN`; sin él no hace nada. Lo publicado queda en `.github/quincy-social/posted.json`. Para regenerar el calendario: `python3 quincy/scripts/build_social.py`. Guía para conectarlo: `marketing/guia.html`.
- `.github/workflows/quincy-rates.yml` actualiza la tasa de CETES y la inflación cada miércoles si existe el secreto `BANXICO_TOKEN`.

## Supuestos

- Salario diario = sueldo mensual ÷ 30.
- Liquidación: mínimo de ley (3 meses de salario integrado, prima de antigüedad con tope de 2 salarios mínimos y finiquito). Los 20 días por año se muestran aparte porque solo aplican en algunos casos.
- Valor de un turno de tanda = lo que recibes en tu turno, llevado al final de la tanda con la tasa de CETES, menos lo que aportas, llevado igual.
- Límite diario = (pago − fijos − ahorro − gastado en el periodo) ÷ días que faltan para el siguiente pago.
- Herramienta educativa: no es asesoría legal, fiscal ni de inversión.
