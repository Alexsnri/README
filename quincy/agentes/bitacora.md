# Bitácora de los agentes

Lo más nuevo arriba. Cada agente agrega su entrada al terminar.

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
