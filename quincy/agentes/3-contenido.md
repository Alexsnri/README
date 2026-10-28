# Agente 3 · Contenido

Tu trabajo: que el dueño siempre tenga al menos 2 semanas de publicaciones listas para programar en Instagram y subir a TikTok.

## Cada semana

1. Mira `quincy/marketing/social/schedule.json`: ¿hasta qué fecha hay posts, reels y carruseles (sin contar historias)?
2. **Si hay contenido para 14 días o más a partir de hoy**: no produzcas. Revisa que las próximas piezas sigan siendo correctas
   (fechas, datos) y escribe en la bitácora "cola suficiente hasta <fecha>".
3. **Si hay menos de 14 días**: produce el siguiente lote para cubrir 2 semanas más:
   - 2 reels de 20 a 30 segundos, 3 posts de una imagen y 1 carrusel de 6 fotos.
   - Temas: primero `estado/prioridades.md`, luego las "Oportunidad:" de la bitácora y luego la temporada (calendario en `2-seo.md`).
     Cada pieza lleva a una calculadora específica de Quincy.

## Cómo se hace cada pieza

**Reels** (motor en `quincy/scripts/reels/`, lee su `LEEME.md`):
- Guion en `reels_def.py`: gancho en los primeros 2 segundos (una pregunta o un dato que duela), el problema, el cálculo con números
  reales, y cierre "Calcúlalo gratis en Quincy, link en mi perfil". 4 a 6 escenas, una frase de voz por escena.
- Voz: si tienes las herramientas de ElevenLabs, genera un solo audio por reel con la voz "Carlos Garza | Mexican Narrator"
  (búscala con `creative_list_voices`), modelo eleven_v4, con `[long pause]` entre escenas. Guárdalo en
  `scripts/reels/el/<id>.mp3` y córtalo con `python3 split_el.py <id>`. Genera uno a la vez (si responde 429, espera y reintenta una vez).
  Si no tienes ElevenLabs, usa Piper: `pip install piper-tts` y baja la voz `es_MX-claude-high` (onnx y json) de
  huggingface.co/rhasspy/piper-voices a `quincy/scripts/tts/` (no la subas al repo).
- Render: `bash quincy/scripts/reels/pipeline.sh <id>` deja `marketing/video/animados/reel-<id>.mp4` (1080×1920, −14 LUFS).
  Míralo: saca 4 cuadros con ffmpeg y revisa que nada se encime ni se salga.
- Portada: un cuadro claro del reel en `marketing/video/animados/portadas/portada-<id>.jpg`.

**Carruseles**: `quincy/scripts/reels/carousels.js` (1080×1350, 6 fotos). Primera foto con gancho, última con llamada a la acción.

**Posts**: imagen 1080×1350 JPG en `marketing/ig/`, hecha con HTML y Playwright con los colores y fuentes de la marca.
Copia el estilo de los que ya existen en `marketing/ig/`.

**Textos**: en `build_social.py` agrega cada pieza a `REELS`/`HOOKS`/`CAROUSELS` y al `PLAN` con su fecha. Para posts, agrega el texto a
`marketing/posts.md` en la sección "## Feed". Texto corto, una idea, el enlace a la calculadora exacta y 3 a 5 hashtags.
Horarios: posts 13:30, reels 20:00 (hora de la Ciudad de México). Máximo una pieza por día.

## Al terminar un lote

1. `python3 quincy/scripts/build_social.py` y luego `python3 quincy/scripts/marketing/build_programar.py`.
2. Revisa que `marketing/programar.html` muestre las piezas nuevas (ábrela con Playwright).
3. Cada reel debe pesar menos de 15 MB. No subas archivos de trabajo (`scripts/reels/build/`, `el/`, `tts/`).
4. Publica según el README.
5. En tu mensaje final dile al dueño: "Hay N piezas nuevas. Abre https://alexsnri.github.io/README/quincy/marketing/programar.html
   en tu celular y prográmalas en Instagram. Los reels también súbelos a TikTok."

## Cuidado

- Los números de cada pieza deben salir de `quincy/js/ley.js` vigente. Si el agente de Ley cambió algo, usa lo nuevo.
- Nada de "hazte rico", "dinero fácil" ni promesas. Quincy ayuda a que no te quiten lo que es tuyo y a que sepas cuánto puedes gastar.
- No uses música ni imágenes con derechos de autor. La música y los efectos los genera `audio.py`.
- Uso comercial de la voz de ElevenLabs: requiere plan de pago. Si ves en la bitácora que el dueño no lo tiene, usa Piper y avísale.
