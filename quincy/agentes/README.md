# Equipo de agentes de Quincy

Quincy funciona sola entre semana. Cinco agentes de Claude corren con horario fijo (hora de la Ciudad de México),
cada uno en una sesión nueva, leen su manual y hacen su trabajo sin pedir permiso. Al final mandan una
notificación corta al dueño.

| Agente | Manual | Cuándo | Qué hace |
|---|---|---|---|
| Ley y datos | `1-ley-y-datos.md` | martes 21:13 | Vigila salario mínimo, UMA, reformas a la LFT, CETES e inflación. Actualiza la app y sus pruebas. |
| SEO y crecimiento | `2-seo.md` | miércoles 22:41 | Revisa la salud del sitio, dónde sale Quincy en Google, y mejora o crea una página por semana. |
| Contenido | `3-contenido.md` | jueves 20:26 | Mantiene siempre 2 semanas de reels, posts y carruseles listos para programar. |
| Marca | `4-marca.md` | día 3 de cada mes 19:52 | Vigila en el IMPI marcas "Quincy" nuevas o que cambian de estatus, y copias. |
| Director | `5-director.md` | domingo 18:37 | Mide (visitas, salud), revisa el trabajo de los demás, fija prioridades y le da al dueño sus 3 tareas de la semana. |

Los agentes se coordinan por archivos:

- `bitacora.md`: lo que hizo cada agente, lo más nuevo arriba. Todos la leen al empezar y escriben al terminar.
- `estado/prioridades.md`: lo que el Director decidió que importa esta semana. SEO y Contenido lo siguen.
- `estado/*.json`: memoria de cada agente (posiciones en Google, marcas vigiladas, métricas).
- `informes/AAAA-MM-DD.md`: informe semanal del Director.

## Reglas para todos los agentes

**Al empezar**
1. Tu sesión ya trae el repositorio conectado con permiso de escritura (busca la carpeta que contiene `quincy/`,
   normalmente `/home/user/README`). Si no está, clónalo con `git clone https://github.com/Alexsnri/README`; si después el push
   da 403, haz tu trabajo igual, no publiques y di en tu mensaje final exactamente qué falló.
   Esta sesión se reutiliza cada semana: no te fíes de lo que recuerdes de corridas anteriores, todo lo vigente está en el repositorio.
2. `git fetch origin main && git checkout -B agente origin/main` para trabajar sobre lo último publicado.
3. Lee este archivo, tu manual, `estado/prioridades.md` y las primeras 60 líneas de `bitacora.md`.
4. Corre `date` y trabaja con la fecha real. No supongas la fecha.

**Mientras trabajas**
- Cambios pequeños, útiles y reversibles. Mejor una cosa bien hecha que cinco a medias.
- Todo número de ley o de dinero necesita una fuente oficial con fecha: DOF, CONASAMI, INEGI, SAT, Banxico, IMSS, gob.mx.
  Si no la encuentras, no cambies el número: anótalo en la bitácora como pendiente.
- Las páginas para buscadores se generan con `quincy/scripts/build_seo.py`. Edita el script y córrelo; no edites a mano el HTML generado.
- La lista para programar se genera con `quincy/scripts/marketing/build_programar.py` a partir de `build_social.py`.
- Escribe como habla la gente en México: tú, frases cortas, sin anglicismos ni tecnicismos. Nada de promesas de dinero.
- Quincy da información general, no asesoría legal individual. Para conflictos laborales recomienda PROFEDET (gratis).

**Nunca**
- Borres `quincy/google*.html` (verificación de Google), cambies el token de Cloudflare en `js/core.js` ni toques secretos.
- Gastes dinero, compres, contrates o te registres en servicios a nombre del dueño.
- Publiques en redes sociales, mandes mensajes o correos a personas, ni comentes como si fueras el dueño.
  Puedes dejar textos listos para que él los mande.
- Inventes datos, testimonios, cifras de usuarios o reseñas.
- Desactives o borres pruebas para que pasen.
- Reescribas historia de git (`--force`, `rebase` de lo ya publicado).

**Antes de publicar cambios del sitio**
1. `node quincy/scripts/test_ley.js` debe decir "Todas las pruebas pasan".
2. Si tocaste páginas o JS, ábrelas con Playwright (ya viene instalado: `require('playwright')`) y confirma que no hay errores en consola.
3. Si cambiaste archivos de la app (`js/`, `css/`, `app.html`, `index.html`), sube la versión de `CACHE` en `quincy/sw.js`.

**Para publicar**
```
git add -A quincy .github && git commit -m "<agente>: <qué cambió y por qué>"
git pull --rebase origin main && git push origin HEAD:main
```
Si el push falla por red, reintenta hasta 4 veces (espera 2, 4, 8 y 16 segundos).
GitHub Pages publica en 1 o 2 minutos. Después corre `python3 quincy/scripts/agentes/salud_sitio.py`.
Si salen errores nuevos por tu cambio, arréglalo o haz `git revert` de tu commit y publica.

**Al terminar (siempre, aunque no hayas cambiado nada)**
1. Agrega tu entrada arriba de todo en `bitacora.md`:
   ```
   ## AAAA-MM-DD · <Agente>
   - Hice: …
   - Encontré: …
   - Para el dueño: … (o "nada")
   ```
2. Publica la bitácora con el mismo procedimiento.
3. Tu último mensaje es la notificación que le llega al dueño al celular. Si tienes la herramienta `PushNotification`, mándalo también con ella. Escríbelo en español, en 3 a 5 líneas:
   qué hiciste, el resultado más importante y, si aplica, qué tiene que hacer él. Sin tecnicismos.

## Datos del proyecto

- Sitio: https://alexsnri.github.io/README/quincy/ (GitHub Pages, rama `main`, carpeta `quincy/`).
- Redes: Instagram @quincy_app, TikTok @quincyapp. La publicación en Instagram es manual desde `marketing/programar.html`
  (no hay token de API). Si algún día existe el secreto `INSTAGRAM_TOKEN`, el robot `.github/workflows/quincy-social.yml` publica solo.
- Marca: colores Noche #07121A, Mar #15404F, Sol #FFB547, Marea #5AD6C8, Niebla #EAF3F4. Fuentes Unbounded, Figtree, JetBrains Mono.
  Manual completo en `marketing/marca/index.html`.
- Analítica: Cloudflare Web Analytics (sin cookies). El Director lee las visitas si existe la variable `CF_API_TOKEN`.
- Google Search Console verificado para la propiedad `https://alexsnri.github.io/README/quincy/`, sitemap enviado.
- Marca registrable: "Quincy" está libre en la clase 36 y en la 9 solo hay marcas vencidas o abandonadas (ver `4-marca.md`).
