# Bitácora de los agentes

Lo más nuevo arriba. Cada agente agrega su entrada al terminar.

## 2026-10-28 · Producto y diseño (4)
- Hice: simplifiqué la app en el celular (encargo del dueño): 4 pestañas (Hoy, Me toca, Herramientas, Tú) y encabezado limpio;
  Hoy con solo el anillo y "Registrar gasto" arriba, lo demás en hojas y bloques plegables; Me toca en tarjetas que se expanden;
  Herramientas como cuadrícula. Arreglé la fecha final de "Tu quincena". Portada en celular 4,667 → 2,974 px con 3 bloques claros y
  la tarjeta "Ponlo a rendir" (idea de Monetización). El sitio viejo ahora entrega un service worker que se borra solo (en `mudanza.py`).
- Encontré: Hoy pasó de 18 a 8 elementos tocables en la primera pantalla (1,787 → 1,046 px); Me toca de 3,786 a 1,136 px.
  En la dirección nueva las imágenes Open Graph, el canonical y `?ref=` funcionan. Probado: persona nueva, migración, ejemplo, gasto,
  ¿me alcanza?, compartir, tanda `?t=`, reto `?reto=`, en 390 y 1440 px, sin errores. Detalle en `estado/producto.md`.
- Para Monetización: toqué `scripts/agentes/mudanza.py` (solo agrega `SW_ADIOS` al redirigir el sitio viejo).
- Para el dueño: nada.

## 2026-10-28 · Orquestador (de parte del dueño)
- Hice: activé los avisos con los enlaces del dueño: canal de WhatsApp (`CONFIG.AVISOS.whatsappCanal`) y formulario de Brevo
  (`CONFIG.AVISOS.correoForm`). `CONFIG.CONTACT_EMAIL` = hola.quincymx@gmail.com (piloto B2B por correo). `privacidad.html` completo
  (responsable Alejandro Sánchez, Brevo, 28 oct 2026) y enlazado desde la casilla de aceptación. `sw.js` v16. Probado: los botones
  se activan solo al aceptar; 0 errores. Ya en vivo en quincy-mx.github.io.
- Para todos: ya no pidan al dueño el canal de WhatsApp, el formulario de correo ni el correo de Quincy. Los suscriptores viven en Brevo.
- Para el dueño: cambiar la contraseña del Gmail de Quincy (la escribió en el chat) y activar la verificación en dos pasos.

## 2026-10-28 · SEO (corrida extra)
- Hice: `aguinaldo/` ahora enlaza a `aguinaldo-a-rendir/` desde el texto ("¿Ya sabes cuánto te toca? Ponlo a rendir"). Acorté las
  descripciones de aguinaldo (157), finiquito (159), vacaciones (160) y PTU (151) y el título de PTU ("PTU 2027: cuánto te toca de
  reparto de utilidades", 59 con "| Quincy"). `lastmod` al 28 en el sitemap. Empecé `estado/seo.json` con 11 consultas.
- Encontré: Quincy todavía no aparece en ninguna consulta (la dirección nueva tiene días; Google no la conoce aún). Arriba salen
  hacecuentas.com, facturama, BBVA y periódicos. "tanda qué número conviene" solo da resultados sin relación: hueco que nuestra
  página puede ganar. Salud del sitio: 0 errores; los 5 avisos quedan resueltos al publicar.
- Oportunidad (Ley y datos): varias notas mencionan una propuesta para subir el aguinaldo a 30 días; vigilar si avanza en el DOF.
  Una guía dice que la fecha límite real es el viernes 18 de diciembre de 2026 (el 20 cae en domingo); la ley dice "antes del 20",
  nosotros decimos 19: revisar si conviene aclarar que el 19 es sábado.
- Para el dueño: en Search Console (propiedad nueva) pide "Solicitar indexación" de `https://quincy-mx.github.io/aguinaldo/`.

## 2026-10-28 · Director (corrida extra)
- Hice: revisé todo lo de hoy en la dirección nueva (Playwright en celular y computadora: sin errores) y reescribí `estado/prioridades.md`
  para los días previos al lanzamiento, con **congelamiento desde el sábado 31 a las 12:00** (solo arreglos hasta el martes 3).
  Limpié la fuente de CETES que salía con espacios basura (`data/rates.json` y `update_rates.py`) y cambié a `quincy-mx.github.io` los
  textos listos para copiar de `marketing/lanzamiento.md` y `posts.md`. Informe en `informes/2026-10-28.md`.
- Encontré: 0 errores, 5 avisos de SEO. Sin datos de visitas (no hay `CF_API_TOKEN`). Hoy ya van ~14 corridas, el tope semanal:
  no habrá más corridas extra esta semana, solo las del horario.
- Para Producto: el service worker es red primero, así que con internet la dirección vieja redirige bien; revisa que quien la abrió antes
  no se quede sin conexión con la versión vieja.
- Para el dueño: (1) cambia el token expuesto y envía `sitemap.xml` en la propiedad nueva de Search Console; (2) cambia la bio de
  Instagram y TikTok a https://quincy-mx.github.io/ ; (3) lunes 2: reel R1 y el mensaje de WhatsApp (en el informe).

## 2026-10-28 · Monetización (4)
- Hice: el dueño pidió que todo el equipo se ponga a trabajar: desperté a Director (15:47), SEO (15:53), Contenido (15:59), Producto (16:05)
  y Ley y datos (16:11), hora de México, con sus pendientes. `empresas.html`: nueva sección "El piloto: 90 días, sin costo y sin contrato"
  y `CONFIG.CONTACT_EMAIL` en `js/core.js` (si hay correo, "Solicitar piloto" abre un correo ya escrito). `sw.js` v15.
- Encontré: el botón de piloto llevaba a un formulario de GitHub, que pide cuenta de GitHub; casi nadie de RR. HH. la tiene.
- Para el dueño: crear un correo gratis para Quincy y pasarlo a cualquier agente (va en `CONTACT_EMAIL`).

## 2026-10-28 · Monetización (3)
- Hice: **Quincy ya vive en https://quincy-mx.github.io/** (gratis). El robot de publicación arma el sitio con la dirección nueva y lo sube a
  `Quincy-mx/quincy-mx.github.io`; la dirección vieja redirige página por página y conserva `?ref=`. Probado en navegador: sin errores.
  `salud_sitio.py` ya revisa la dirección nueva (0 errores). El robot deduce el repositorio si falta `QUINCY_REPO_NUEVO`.
- Para todos: la dirección vieja en el código se cambia sola al publicar; no hace falta tocarla. Search Console: falta la propiedad nueva.
- Para el dueño: cambiar el token que se pegó en el chat (está expuesto) y agregar `https://quincy-mx.github.io/` en Search Console.

## 2026-10-28 · Monetización (2)
- Hice: el dueño pidió que el dominio sea gratis. Búsqueda a fondo: los dominios gratis (DigitalPlat `.us.kg`/`.dpdns.org`/`.qzz.io`)
  aparecen en la lista negra de Spamhaus o fueron suspendidos por phishing; EU.org desalienta sitios comerciales; js.org es solo para
  proyectos de JavaScript; Freenom cerró. Elegí una organización gratis de GitHub: `https://quincy-mx.github.io/`.
  Programé la mudanza automática: `scripts/agentes/mudanza.py` y pasos nuevos en `quincy-pages.yml` (no hacen nada hasta que existan
  la variable `QUINCY_SITIO_NUEVO` y el secreto `QUINCY_PUBLICAR_TOKEN`). El sitio viejo redirige página por página y conserva `?ref=`.
- Para todos: cuando el sitio se mude, cambiar `SITE` en los scripts y en `agentes/README.md` (ver `estado/monetizacion.md`).
- Para el dueño: 6 pasos gratis en "Lo que necesito del dueño" de `estado/monetizacion.md` (crear organización, repositorio, token y 2 variables).

## 2026-10-28 · Producto y diseño (3)
- Hice: la app ahora empieza con una bienvenida de menos de 1 minuto (una pregunta por pantalla, con privacidad clara) que termina en
  "Hoy puedes gastar $X" y lo que te toca por ley. Un solo perfil para Hoy, Me toca, Futuro y Tanda, editable en "Tus datos" con
  respaldo en archivo y borrar todo. Quien ya usaba la app no ve la bienvenida (sus datos se migran). La portada pasa el sueldo a la app.
  Avisos opcionales (calendario siempre; WhatsApp y correo cuando haya enlaces) y `privacidad.html` lista sin enlazar.
- Encontré: todo probado en 390 y 1440 px (persona nueva, migración, ejemplo, respaldo, borrar), sin errores de consola, accesibilidad 100.
- Para el dueño: para activar los avisos (1) crea el canal de WhatsApp de Quincy y copia su enlace; (2) abre una cuenta gratis en un
  servicio de correos con formulario de suscripción (por ejemplo MailerLite o Brevo) y copia el enlace del formulario; (3) en
  `quincy/privacidad.html` cambia [NOMBRE DEL RESPONSABLE], [CORREO DE CONTACTO], [NOMBRE DEL SERVICIO DE CORREOS] y [FECHA];
  (4) pega los enlaces en `CONFIG.AVISOS` de `quincy/js/core.js` (o pásaselos a cualquier agente y lo hace).

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
