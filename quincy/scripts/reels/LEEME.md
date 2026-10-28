# Reels animados de Quincy

Motor para generar los reels de `marketing/video/animados/` y los carruseles de `marketing/carruseles/`.

- `reels_def.py`: guion de cada reel. Cada escena tiene una línea de voz; los elementos aparecen cuando la voz dice su palabra clave.
- `engine.html`: motor de animación cuadro por cuadro (1080×1920, 30 fps).
- `render.js`: dibuja cada cuadro con Playwright y lo manda a ffmpeg.
- `audio.py`: música original (100 BPM, Am–F–C–G), efectos sincronizados y voz con la música bajando cuando habla.
- `pipeline.sh <id>…`: todo junto, normalizado a −14 LUFS.
- `carousels.js`: carruseles de 6 fotos (1080×1350).

Voz: ElevenLabs (modelo `eleven_v4`, voz "Carlos Garza | Mexican Narrator"), un audio por reel con `[long pause]` entre escenas.
`split_el.py <id>` corta ese audio en escenas por las pausas más largas y deja los `.wav` que usa `reels_def.py`.
Si no hay audio de ElevenLabs, `reels_def.py` genera la voz con Piper (`es_MX-claude-high`, Apache-2.0).
Uso comercial: la voz de ElevenLabs requiere un plan de pago de ElevenLabs. Ajusta las rutas de `pipeline.sh` y `reels_def.py` a tu equipo.
