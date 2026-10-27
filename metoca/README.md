# Me Toca

Lo que te toca, cuándo te toca y cuánto te queda. Una app web gratis para trabajadores en México: cuánto puedes gastar hoy para llegar a la quincena, cuánto te toca por ley (aguinaldo, vacaciones, prima vacacional, PTU, finiquito y liquidación con los valores de 2026) y cómo vivirá tu yo del futuro. Sin registro y sin servidores.

**Sitio:** https://alexsnri.github.io/README/metoca/ (después de activar GitHub Pages)

## Páginas

| Página | Qué es |
|---|---|
| `index.html` | Portada en 3D: partículas que cambian de forma con el scroll, con demos que funcionan. |
| `app.html` | La app: Hoy, Me toca, Futuro, Reto y Más. |
| `empresas.html` | Página de ventas para empresas e instituciones. |
| `plan.html` | Plan de negocio (no se indexa). |

## Código

| Archivo | Para qué sirve |
|---|---|
| `js/core.js` | Configuración (sitio, contacto, analítica), estado, cálculos de dinero en el tiempo y utilidades. |
| `js/ley.js` | Cálculos de la Ley Federal del Trabajo y valores de 2026 (salario mínimo y UMA). **Actualizar cada enero y febrero.** |
| `js/quincena.js` | "Hoy": límite diario, gastos, "¿me alcanza?" y días en verde. |
| `js/derechos.js` | "Me toca": aguinaldo, vacaciones, PTU, finiquito y liquidación, calendario y checklist. |
| `js/sim.js`, `js/avatar.js` | "Futuro": simulador de retiro y avatar que envejece. |
| `js/reto.js` | Reto diario de 5 preguntas, igual para todos cada día. |
| `js/share.js` | Tarjetas para historias. |
| `js/app.js` | Secciones, marca de empresas, retos recibidos y tasas. |
| `js/landing.js`, `css/landing.css` | Escena 3D (three.js r128 desde cdnjs) y animaciones de la portada. |

## Pruebas

Los cálculos de ley tienen 35 pruebas. Para correrlas:

```
node metoca/scripts/test_ley.js
```

## Versión con marca

```
https://alexsnri.github.io/README/metoca/app.html?marca=Tu%20Empresa&color=2f6fed&cta=https%3A%2F%2Ftu-sitio.mx&cta_txt=Abre%20tu%20cuenta
```

`marca` (máx. 30 caracteres), `color` (hex de 6 dígitos), `cta` (solo `https://`), `cta_txt` (texto del botón) y `ocultar=salida` para esconder la calculadora de finiquito y liquidación.

## Configuración (en `js/core.js`)

- `CONTACT_URL`: a dónde llegan las solicitudes de piloto. Hoy apunta a un formulario de GitHub Issues.
- `CF_ANALYTICS_TOKEN`: token de Cloudflare Web Analytics (gratis, sin cookies). Vacío = sin analítica.

## Automatizaciones

- `.github/workflows/metoca-pages.yml` publica `metoca/` en GitHub Pages en cada cambio.
- `.github/workflows/metoca-rates.yml` actualiza la tasa de CETES y la inflación cada miércoles si existe el secreto `BANXICO_TOKEN`.

## Supuestos

- Salario diario = sueldo mensual ÷ 30.
- Liquidación: mínimo de ley (3 meses de salario integrado, prima de antigüedad con tope de 2 salarios mínimos y finiquito). Los 20 días por año se muestran aparte porque solo aplican en algunos casos.
- Límite diario = (pago − fijos − ahorro − gastado en el periodo) ÷ días que faltan para el siguiente pago.
- Herramienta educativa: no es asesoría legal, fiscal ni de inversión.
