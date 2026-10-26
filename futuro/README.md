# Futuro Yo

Conoce a tu yo de 65. Simulador de retiro para México con avatar que envejece, carta de tu yo del futuro, tarjeta para compartir y misiones. Gratis, sin registro y sin servidores.

**Sitio:** https://alexsnri.github.io/README/futuro/ (después de activar GitHub Pages)

## Qué hay aquí

| Archivo | Para qué sirve |
|---|---|
| `index.html` | La app completa (HTML, CSS y JS en un solo archivo). |
| `plan.html` | Plan de negocio: tesis, modelo, costos, riesgos y los próximos 90 días. |
| `data/rates.json` | Tasa de CETES e inflación. Se actualiza sola cada semana. |
| `scripts/update_rates.py` | Pide las tasas a la API oficial de Banxico. |
| `sw.js`, `manifest.webmanifest` | Hacen que se pueda instalar como app y funcione sin internet. |
| `marketing/` | Calendario de 30 días y plan de lanzamiento. |

## Automatizaciones

- `.github/workflows/futuro-pages.yml` publica `futuro/` en GitHub Pages en cada cambio.
- `.github/workflows/futuro-rates.yml` actualiza `data/rates.json` cada miércoles si existe el secreto `BANXICO_TOKEN`. Si no existe, no hace nada y la app usa las últimas tasas guardadas.

## Activar (una sola vez)

1. Settings → Pages → Build and deployment → Source: **GitHub Actions**.
2. Unir esta rama a `main`.
3. Opcional: pedir el token gratis en https://www.banxico.org.mx/SieAPIRest/service/v1/token y guardarlo en Settings → Secrets and variables → Actions como `BANXICO_TOKEN`.

## Supuestos del cálculo

- Todo en pesos de hoy: tasa real = (1 + tasa nominal) / (1 + inflación) − 1, con capitalización mensual.
- El ahorro mensual sube cada año con la inflación.
- Ingreso de retiro: regla del 4% anual.
- No incluye Afore, impuestos ni comisiones.
