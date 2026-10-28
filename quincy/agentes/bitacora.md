# Bitácora de los agentes

Lo más nuevo arriba. Cada agente agrega su entrada al terminar.

## 2026-10-28 · Monetización (2)
- Hice: el dueño pidió que el dominio sea gratis. Búsqueda a fondo: los dominios gratis (DigitalPlat `.us.kg`/`.dpdns.org`/`.qzz.io`)
  aparecen en la lista negra de Spamhaus o fueron suspendidos por phishing; EU.org desalienta sitios comerciales; js.org es solo para
  proyectos de JavaScript; Freenom cerró. Elegí una organización gratis de GitHub: `https://quincy-mx.github.io/`.
  Programé la mudanza automática: `scripts/agentes/mudanza.py` y pasos nuevos en `quincy-pages.yml` (no hacen nada hasta que existan
  la variable `QUINCY_SITIO_NUEVO` y el secreto `QUINCY_PUBLICAR_TOKEN`). El sitio viejo redirige página por página y conserva `?ref=`.
- Para todos: cuando el sitio se mude, cambiar `SITE` en los scripts y en `agentes/README.md` (ver `estado/monetizacion.md`).
- Para el dueño: 6 pasos gratis en "Lo que necesito del dueño" de `estado/monetizacion.md` (crear organización, repositorio, token y 2 variables).

## 2026-10-28 · Producto y diseño (2)
- Hice: "Historias" ahora abre el menú del teléfono con la imagen lista para Instagram → Historia (antes solo descargaba un PNG porque la
  tarjeta se dibujaba después del toque). El enlace queda copiado para el sticker. Tarjetas en JPG (2.1 MB → 140 KB). Hoja con vista
  previa cuando no se puede directo (computadora o navegador dentro de otra app). Portada sigue en 99 en local, sin bloqueo.
- Para el dueño: falta el enlace del canal de WhatsApp para `WA_CHANNEL` (no llegó en el mensaje).

## 2026-10-28 · Producto y diseño
- Hice: rediseño completo para el lanzamiento. Portada de temporada con calculadora de aguinaldo y cuenta regresiva en vivo arriba
  (cambia sola por fecha), retícula bento, sin three.js, fuentes propias recortadas y sin desenfoques pesados. Compartir en 1 toque en
  todas las calculadoras: WhatsApp con `?ref=wa`, tarjeta 1080×1920 para historias y "Tu Aguinaldo Wrapped" (5 tarjetas). Aviso
  "Tu amigo ya sabe cuánto le toca, ¿y tú?" al llegar con `?ref=` (portada, calculadoras y app). Imagen Open Graph propia por página
  (`scripts/build_og.js`), Instagram/TikTok y recordatorio .ics en cada calculadora. Detalle y mediciones en `estado/producto.md`.
- Encontré: portada en Lighthouse móvil 75 → 90-92 (local 99), accesibilidad 96 → 100, peso 287 → 142 KB, alto en celular
  9,790 → 4,629 px. Aguinaldo 87 → 94 y accesibilidad 100. El `filter: blur` del fondo retrasaba el primer pintado ~2 s.
- Para SEO: `build_seo.py` tiene ahora `SHARE`, `REMIND` y `HERO_EXTRA` (de Producto) aparte de `PAGES`; los textos siguen siendo tuyos.
  Siguen largas las descripciones de aguinaldo, finiquito, vacaciones y PTU, y el título de PTU (67).
- Para el dueño: abre en tu celular https://alexsnri.github.io/README/quincy/ , escribe tu sueldo y prueba "WhatsApp", "Historias" y
  "Tu Wrapped". Cuando crees el canal de WhatsApp, pega su enlace en `WA_CHANNEL` de `quincy/js/core.js` (o pídeselo a un agente).

## 2026-10-28 · Monetización
- Hice: plan inicial en `estado/monetizacion.md` (dominio, referidos regulados, B2B, patrocinios, lo que falta del dueño).
  Publiqué `aguinaldo-a-rendir/` ("¿Dónde pongo mi aguinaldo a rendir?"): calculadora con CETES de `data/rates.json`, ISR 0.90% (LIF 2026)
  e inflación, y comparativa honesta CETES / banco (IPAB) / SOFIPO (Prosofipo) / billetera / colchón. Sin enlaces de referido.
  Agregué `CONFIG.REFERIDOS = {}` y `FY.referidos(el)` en `js/core.js` (vacío = no se muestra nada; siempre con aviso de comisión).
  `build_seo.py` ahora acepta `eyebrow` y `fuente` por página (las demás quedan igual) y suma la página a "Otras calculadoras". Sitemap y `sw.js` (v7).
- Encontré: `quincy.mx` no tiene registro en DNS (probablemente libre). No hay programas públicos de afiliados de bancos o SOFIPOs en México;
  solo "invita a un amigo" con tope (Mercado Pago, Openbank) o acuerdos directos. Sin dominio propio no aceptan en redes de afiliados.
- Para SEO: enlazar `aguinaldo-a-rendir/` desde el texto de `aguinaldo/` ("¿Ya sabes cuánto te toca? Ponlo a rendir").
- Para Producto: la portada de temporada puede llevar una tarjeta a `aguinaldo-a-rendir/`. No toqué la portada.
- Para el dueño: comprar `quincy.mx` y decidir repositorio (detalles en "Lo que necesito del dueño" de `estado/monetizacion.md`).

## 2026-10-28 · Marca
- Hice: revisión mensual en MARCia (IMPI) de "Quincy" en las clases 9, 35, 36, 41 y 42 y búsqueda web de copias.
  Guardé la revisión en `estado/marca.json`.
- Encontré: sin cambios contra la revisión anterior. Clase 36 sigue libre. Clase 9: Little Einsteins sigue vencida (2014) y
  exp. 2130417 sigue abandonada. Clase 42: exp. 3656827 (American Society for Quality) sigue en trámite. Clase 35: las de
  Youssef Esteban Rodríguez sin cambios. En la web no hay apps ni sitios de finanzas en México o Latinoamérica llamados Quincy
  (solo Quincy Credit Union de EE. UU. y una app para planear XV años, sin relación).
- Para el dueño: falta solicitar el registro de "Quincy" en el IMPI (clases 36 y 9). No hay registro solicitado en la bitácora.

## 2026-10-28 · Arranque del equipo
- Hice: se crearon los 5 agentes, sus manuales, la revisión de salud del sitio (`scripts/agentes/salud_sitio.py`) y el vigía de marca
  (`scripts/agentes/vigia_marca.js`). Se dejó la primera revisión de marca en `estado/marca.json`.
- Encontré: sitio sin errores; 6 avisos de descripciones largas (portada, aguinaldo, finiquito, vacaciones, PTU) y título de PTU de 67 caracteres.
  Cloudflare Web Analytics activo en todas las páginas públicas (token en `js/core.js`).
  Marca: "Quincy" libre en clase 36; en clase 9 solo hay marcas vencidas o abandonadas; en clase 42 hay una solicitud en trámite
  (American Society for Quality, exp. 3656827).
- Para el dueño: lanzamiento el 2 de noviembre (reel 00 fijado, programar Instagram con `programar.html`, recordatorios de TikTok,
  WhatsApp). Pendiente: solicitar el registro de "Quincy" en el IMPI (clases 36 y 9). Opcional: `CF_API_TOKEN` para medir visitas,
  `BANXICO_TOKEN` para tasas automáticas, plan de pago de ElevenLabs para uso comercial de la voz.
