# Reels animados de Quincy

Motor para generar los reels de `marketing/video/animados/` y los carruseles de `marketing/carruseles/`.

- `reels_def.py`: guion de cada reel. Cada escena tiene una línea de voz; los elementos aparecen cuando la voz dice su palabra clave.
- `engine.html`: motor de animación cuadro por cuadro (1080×1920, 30 fps).
- `render.js`: dibuja cada cuadro con Playwright y lo manda a ffmpeg.
- `audio.py`: música original (100 BPM, Am–F–C–G), efectos sincronizados y voz con la música bajando cuando habla.
- `pipeline.sh <id>…`: todo junto, normalizado a −14 LUFS.
- `carousels.js`: carruseles de 6 fotos (1080×1350).

Voz: Piper TTS con la voz `es_MX-claude-high` (licencia Apache-2.0). Ajusta las rutas de `pipeline.sh` y `reels_def.py` a tu equipo.
