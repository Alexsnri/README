# Producto y diseño · ideas, experimentos y resultados

Lo más nuevo arriba. Cada cambio: qué se hizo, qué esperamos y cómo se mide.

## Mediciones (Lighthouse móvil, sitio publicado; mismo entorno antes y después)

| Fecha | Página | Rendimiento | Accesibilidad | Buenas prácticas | SEO | LCP | Peso | Alto en celular |
|---|---|---|---|---|---|---|---|---|
| 2026-10-28 antes | Portada | 75 | 96 | 100 | 100 | 4.4 s | 287 KB | 9,790 px |
| 2026-10-28 después | Portada | 90–92 | 100 | 100 | 100 | 3.2 s | 142 KB | 4,629 px |
| 2026-10-28 antes | Aguinaldo | 87 | 95 | 100 | 100 | 3.1 s | 131 KB | 2,655 px |
| 2026-10-28 después | Aguinaldo | 94 | 100 | 100 | 100 | 3.0 s | 112 KB | 3,241 px |

En local (sin el proxy del entorno de pruebas) la portada da 99/100/100/100. Primer pintado real en vivo medido con Playwright: 0.8 s.
Escritorio 1440 px: la portada pasó de 11,700 px a 2,690 px y ya usa todo el ancho.

## 2026-10-28 · App: bienvenida y un solo perfil (encargo del dueño)

**Qué cambió**
- Bienvenida la primera vez (sin perfil): "Hola, soy Quincy" con tarjeta de privacidad; pago (frecuencia y fecha del próximo pago),
  cuánto te llega, pagos fijos por concepto + ahorro, y trabajo opcional (sueldo, fecha de ingreso, frontera, edad). Al final,
  "Hoy puedes gastar $X" animado y lo desbloqueado (días para tu pago, aguinaldo, vacaciones). "Ver con un ejemplo" deja datos de ejemplo
  marcados. Con enlace de tanda o reto se entra directo.
- Un solo perfil `qc:yo` (pago, trabajo, futuro) en `js/core.js`. Los módulos siguen pidiendo "q", "perfil" y "state" y core lo traduce.
  Quien tenía las llaves viejas se migra sin ver la bienvenida. Hoy y Me toca muestran un resumen con "Editar"; todo se edita en
  la vista nueva "Tus datos" (#datos), con pagos fijos por concepto, edad, avisos, respaldo (JSON) y borrar.
- "Hoy" respeta la fecha de próximo pago que diste (semanal en cualquier día, quincena fuera del 15/fin de mes, mensual).
- La portada pasa el sueldo a la app (`?sueldo=` y `qc:portada`).
- Avisos opcionales: calendario (.ics con aguinaldo y salario mínimo) siempre; canal de WhatsApp y correo solo si `CONFIG.AVISOS`
  tiene enlaces, con casilla de aceptación. `privacidad.html` lista para llenar (sin enlazar hasta entonces).

**Qué esperamos:** más personas que terminan de configurar y regresan (el límite de hoy ya es suyo desde el minuto 1).

**Cómo se mide:** sin analítica de eventos todavía. Proxy: visitas a `app.html` que regresan (Cloudflare) y respuestas al canal/correo
cuando existan. Idea: contar en Cloudflare una visita a `app.html#hoy?listo` al terminar la bienvenida (sin datos personales).

## 2026-10-28 · Historias directo a Instagram (pedido del dueño)

**Problema:** el botón "Historias" solo descargaba un PNG. La tarjeta se dibujaba después del toque y el navegador ya no dejaba abrir
el menú de compartir (necesita que se llame en el mismo toque), así que caía en la descarga. Además mandaba texto junto con la imagen y
pesaba 2.1 MB.

**Qué cambió (`js/compartir.js`):** la tarjeta se prepara antes (con la primera interacción y cada vez que cambian los datos) y al tocar
"Historias" se abre el menú del teléfono solo con la imagen, donde aparece Instagram → Historia. El enlace se copia para pegarlo en el
sticker de enlace. Tarjetas en JPG (~140 KB). Si no se puede subir directo (computadora o navegador dentro de Instagram/WhatsApp) sale una
hoja con la vista previa, la explicación y botones para descargar y copiar el enlace. En el Wrapped el botón sube la tarjeta que estás
viendo ("Subir esta a Instagram"). La tarjeta de la app (`share.js`) también manda solo la imagen.

**Cómo se mide:** visitas con `?ref=historia` y `?ref=wrapped` (vienen del sticker de enlace).

## 2026-10-28 · Rediseño para el lanzamiento (primer gran trabajo)

**Qué cambió**
- Portada de temporada (`index.html`, `js/portada.js`, `css/landing.css`): arriba, una calculadora que funciona al instante con cuenta
  regresiva en vivo. Cambia sola por fecha: aguinaldo (15 oct–19 dic), cuesta de enero (20 dic–15 ene), salario mínimo (16 ene–31 mar),
  PTU (1 abr–29 jun), vacaciones (30 jun–15 ago), quincena/regreso a clases (16 ago–14 oct). Probar otra: `?temporada=ptu`.
  El HTML trae fijo el texto de aguinaldo; en otras temporadas lo cambia el JS (en la corrida de diciembre conviene dejar fijo el de la siguiente).
- Retícula bento: app "Hoy" con demo, calendario de fechas, 7 calculadoras, tu yo de 65, reto diario, Síguenos (IG/TikTok), Avísame (.ics),
  privacidad y empresas. Animaciones solo con CSS (scroll-driven, view transitions) y respetan "reducir movimiento".
- Sin three.js (se borró `js/landing.js`), fondo con degradados CSS sin `filter: blur` (el desenfoque retrasaba el primer pintado ~2 s en
  equipos sin GPU). Fuentes servidas desde `fonts/`, recortadas a español (Unbounded 51→29 KB) con `font-display: swap` y precarga.
- Compartir en 1 toque (`js/compartir.js`) en la portada y todas las calculadoras: WhatsApp con texto listo y `?ref=wa`; "Historias" crea
  una tarjeta 1080×1920 (Web Share con archivo; si no, descarga); "Tu Wrapped" en aguinaldo (5 tarjetas: cuánto, cuenta regresiva,
  libre de ISR, rendimiento en CETES, invitación). Al llegar con `?ref=` sale "Tu amigo ya sabe cuánto le toca. ¿Y tú?" (también en la app).
- Open Graph propia por página (`img/og/*.jpg`, generadas con `node quincy/scripts/build_og.js`).
- "Que no se te pase": recordatorio .ics (aguinaldo, PTU o quincena), Instagram y TikTok en cada calculadora; `CONFIG.WA_CHANNEL` vacío
  en `js/core.js` para el canal de WhatsApp (aparece el botón en cuanto se llene).
- Contraste: `--dim` de app.css subió a #7d9aa5 y el verde de WhatsApp a #15803d (texto blanco legible).

**Qué esperamos**
- Más personas que calculan (la calculadora está en el primer pantallazo, sin desplazarse).
- Más visitas con `?ref=` (wa, historia, wrapped): cada resultado se comparte en 1 toque.
- Mejor tarjeta en WhatsApp al pegar un enlace (imagen propia por página).

**Cómo se mide** (Cloudflare Web Analytics, cuando el Director tenga `CF_API_TOKEN`)
- Visitas con `ref=wa`, `ref=historia`, `ref=wrapped`, `ref=recordatorio` por semana (aparecen en la ruta con consulta).
- Lighthouse móvil de portada y aguinaldo en cada corrida (meta ≥ 90).

## Ideas para siguientes corridas
- Medir clics en "WhatsApp", "Historias" y "Wrapped" (eventos propios sin cookies: un `?ref` distinto por botón ya lo permite al llegar).
- Wrapped también para PTU (mayo) y "Mi quincena" (ticket).
- Página de la cuesta de enero con plan de 30 días (diciembre).
- Rediseñar la vista "Me toca" de la app con el mismo lenguaje bento.
- Cuando exista dominio propio: actualizar `CONFIG.SITE`, canonical y OG.
