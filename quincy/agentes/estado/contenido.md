# Memoria del agente de Contenido

## Tendencias (28 oct 2026)
- Spotify Wrapped 2026 sin fecha oficial; lo más probable es del 30 nov al 4 dic (Official Charts predice el miércoles 2 dic).
  Por eso el reel "Tu Aguinaldo Wrapped" sale el jueves 3 dic. Si Spotify lo saca antes, adelantar el reel R9 (cambiar la fecha en `build_social.py`).
- No hay datos frescos de tendencias de TikTok México para noviembre; el aguinaldo sigue siendo el tema que más se comenta en nov y dic.

## Cola (sin contar historias)
- Hasta el 17 dic 2026. Último lote: c4 Wrapped (8 nov), R9 Wrapped (3 dic), post 13 a rendir (10 dic), R10 a rendir (17 dic).
- Huecos: del 18 al 31 dic (cuesta de enero, "¿ya te pagaron el aguinaldo?", PROFEDET si no llegó) y enero (salario mínimo 2027).

## Datos usados que caducan
- CETES 28 días 6.22% e inflación 3.45% (`data/rates.json`, Banxico, oct 2026) en c4, R9, R10 y post 13.
  Antes del 3 dic: si la tasa cambió mucho (±0.5 puntos), rehacer esas piezas con el dato nuevo.

## Voz
- ElevenLabs respondió "Free Tier access has been disabled" (28 oct 2026): los reels 09 y 10 van con Piper (`es_MX-claude-high`).
