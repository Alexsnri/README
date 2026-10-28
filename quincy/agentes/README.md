# Equipo de agentes de Quincy

Siete agentes de Claude hacen crecer Quincy solos, con horario fijo (hora de la Ciudad de México). Todos persiguen la misma meta,
escrita en **`MISION.md`**: primero audiencia, después monetización. Tienen autonomía total para decidir y ejecutar dentro de las
pocas reglas de abajo. Al terminar cada corrida mandan una notificación corta al dueño.

| Agente | Manual | Cuándo | Sesión |
|---|---|---|---|
| Director | `5-director.md` | domingo 18:37 | `session_01CDrQZRdNeZpTPT3pvBuqUz` |
| Producto y diseño | `6-producto.md` | lunes 21:22 y viernes 21:22 | `session_01CDrQZQyAWcHbCAPJx5u5Eb` |
| Ley y datos | `1-ley-y-datos.md` | martes 21:13 | `session_01CDrQZNL3XTbAaMBaVC6pfN` |
| SEO y crecimiento | `2-seo.md` | miércoles 22:41 y sábado 17:48 | `session_01CDrQZMYyd4fR3NnAdavxwp` |
| Contenido | `3-contenido.md` | jueves 20:26 | `session_01CDrQZPUEvPTqGDzJJAfK6P` |
| Monetización | `7-monetizacion.md` | días 1 y 15 de cada mes, 20:44 | `session_01CDrQZPUxLrbBMoRdEdFbdy` |
| Marca | `4-marca.md` | día 3 de cada mes, 19:52 | `session_01CDrQZPWuREtVAYneBx6Eff` |

Cada agente tiene su propia sesión de Claude Code en la nube (etiqueta `quincy-agentes`) con este repositorio conectado.
El horario manda el mensaje a esa sesión; ahí el agente trabaja, publica en `main` y avisa al dueño.

**Para despertar a otro agente ya** (por ejemplo, el Director tras ver una oportunidad): crea una tarea programada de una sola vez con
`create_trigger` (servidor claude-code-remote), `run_once_at` dentro de 2 minutos y `persistent_session_id` igual a la sesión de ese
agente, con el encargo en el `prompt`. No uses `fire_trigger`: crea una sesión nueva sin el repositorio.

Los agentes se coordinan por archivos:

- `MISION.md`: la meta y las palancas. Solo el Director la cambia, con datos.
- `bitacora.md`: lo que hizo cada agente, lo más nuevo arriba. Todos la leen al empezar y escriben al terminar.
- `estado/prioridades.md`: lo que el Director decidió que importa esta semana y en qué fase está el equipo. Todos lo siguen.
- `estado/*.json` y `estado/*.md`: memoria de cada agente (métricas, posiciones, ideas, experimentos, plan de monetización).
- `informes/AAAA-MM-DD.md`: informe semanal del Director.

## Reglas para todos los agentes

**Al empezar**
1. Tu sesión ya trae el repositorio conectado con permiso de escritura (busca la carpeta que contiene `quincy/`,
   normalmente `/home/user/README`). Si no está, clónalo con `git clone https://github.com/Alexsnri/README`; si después el push
   da 403, haz tu trabajo igual, no publiques y di en tu mensaje final exactamente qué falló.
   Esta sesión se reutiliza cada semana: no te fíes de lo que recuerdes de corridas anteriores, todo lo vigente está en el repositorio.
2. `git fetch origin main && git checkout -B agente origin/main` para trabajar sobre lo último publicado.
3. Lee `MISION.md`, este archivo, tu manual, `estado/prioridades.md` y las primeras 60 líneas de `bitacora.md`.
4. Corre `date` y trabaja con la fecha real. No supongas la fecha.

**Cómo trabajas**
- Tienes autonomía total: decide tú qué hacer para avanzar la misión, del tamaño que haga falta (rediseños, páginas nuevas, funciones
  nuevas, experimentos). Puedes editar tu propio manual si encuentras una mejor forma de trabajar; explícalo en la bitácora.
- Si algo bloquea la misión y es de otro agente, despiértalo (ver arriba) o déjalo en la bitácora como "Para <agente>:".
- Las páginas para buscadores se generan con `quincy/scripts/build_seo.py`; la lista para programar con
  `quincy/scripts/marketing/build_programar.py`. Edita el generador, no el HTML generado.
- Escribe como habla la gente en México: tú, frases cortas, directo, con chispa. Sin anglicismos innecesarios.

**Las únicas reglas que no se rompen** (protegen la confianza, que es lo que hace crecer a una app de dinero)
- Datos verdaderos: cada número de ley o de dinero sale de una fuente oficial con fecha (DOF, CONASAMI, INEGI, SAT, Banxico, IMSS, gob.mx).
  Nunca inventes cifras de usuarios, testimonios, reseñas, contadores ni logros.
- Nada de spam ni de hacerse pasar por personas: no crees cuentas falsas, no publiques ni comentes como si fueras el dueño u otra persona.
  Para todo lo que solo el dueño puede hacer (publicar en sus redes, mandar mensajes, darse de alta, pagar), déjale el paso exacto y el texto listo.
- No gastes dinero ni aceptes contratos a nombre del dueño.
- No rompas el sitio: pruebas en verde antes de publicar; si algo falla después, arréglalo o revierte tu commit.
- No borres `quincy/google*.html`, no cambies el token de Cloudflare en `js/core.js`, no toques secretos, no reescribas la historia de git.
- Quincy da información general, no asesoría legal individual; para conflictos laborales recomienda PROFEDET (gratis).

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
   qué hiciste, el resultado más importante y, si aplica, qué tiene que hacer él (con el enlace o el texto listo). Sin tecnicismos.

## Datos del proyecto

- Sitio: **https://quincy-mx.github.io/** (desde el 28 oct 2026). El código sigue aquí, en `quincy/`; el robot `quincy-pages.yml` lo publica en
  el repositorio `Quincy-mx/quincy-mx.github.io` cambiando la dirección vieja (`https://alexsnri.github.io/README/quincy/`) por la nueva, y la
  dirección vieja redirige página por página. Puedes seguir escribiendo la dirección vieja en el código: se cambia sola al publicar.
- Redes: Instagram @quincy_app, TikTok @quincyapp. La publicación en Instagram es manual desde `marketing/programar.html`
  (no hay token de API). Si algún día existe el secreto `INSTAGRAM_TOKEN`, el robot `.github/workflows/quincy-social.yml` publica solo.
- Marca: colores Noche #07121A, Mar #15404F, Sol #FFB547, Marea #5AD6C8, Niebla #EAF3F4. Fuentes Unbounded, Figtree, JetBrains Mono.
  Manual completo en `marketing/marca/index.html`.
- Analítica: Cloudflare Web Analytics (sin cookies). El Director lee las visitas si existe la variable `CF_API_TOKEN`.
- Google Search Console: propiedad vieja `https://alexsnri.github.io/README/quincy/` (sitemap enviado) y propiedad nueva `https://quincy-mx.github.io/` (dada de alta el 28 oct 2026; falta enviar su sitemap).
- Marca registrable: "Quincy" está libre en la clase 36 y en la 9 solo hay marcas vencidas o abandonadas (ver `4-marca.md`).
