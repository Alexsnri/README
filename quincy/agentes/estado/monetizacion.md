# Plan de monetización de Quincy

Plan vivo del agente de Monetización. Última revisión: **2026-10-28**. Fase actual: **1 · Audiencia** (solo preparar, no cobrar).
Próxima revisión: 1 de noviembre de 2026.

## Resumen en 5 líneas

1. **Dirección propia gratis:** `https://quincy-mx.github.io/` (organización de GitHub, gratis). La mudanza ya está programada; falta que el dueño cree la organización. Los dominios gratis de verdad están en listas negras o no aceptan sitios comerciales.
2. **Referidos financieros = el ingreso más grande y natural**, en el momento en que la gente tiene dinero (aguinaldo en dic, PTU en may). Ya está lista la página que los llevará: `aguinaldo-a-rendir/` (sin enlaces todavía).
3. **No hay programas de afiliados abiertos** de Nu, Klar, Openbank, Stori, Plata, Ualá ni CETES en México. Hay programas de "invita a un amigo" (personales, con tope) y acuerdos directos con las fintech o por redes de afiliados. El camino real es **escribirles directo** cuando haya tráfico.
4. **B2B** (`empresas.html`) es la segunda fuente: piloto gratis de 60 días y después cuota mensual por empresa.
5. **Patrocinio de temporada** (aguinaldo/PTU) cuando haya 5,000+ seguidores o 20,000 visitas al mes.

## 1. Dominio propio

**Decisión del dueño (28 oct 2026): tiene que ser gratis.** Búsqueda a fondo de dominios gratis, resultado:

| Opción gratis | ¿Sirve para Quincy? | Por qué |
|---|---|---|
| **Organización de GitHub `quincy-mx` → `https://quincy-mx.github.io/`** | **Sí, la elegida** | Gratis para siempre, mismo servidor y misma confianza que hoy, HTTPS, y el sitio queda en la raíz: `quincy-mx.github.io/aguinaldo/` en vez de `alexsnri.github.io/README/quincy/aguinaldo/`. Ya está todo programado para mudarse solo. |
| DigitalPlat (`.us.kg`, `.dpdns.org`, `.qzz.io`, `.xx.kg`, `.qd.je`) | No | Un reporte de mayo 2026 dice que están en la lista negra de Spamhaus; `.us.kg` fue suspendido por phishing. Para una app de dinero sería ver avisos de "sitio peligroso". `quincy.dpdns.org` ya está ocupado. |
| EU.org (`quincy.eu.org`, libre) | No | Su política pide a sitios comerciales usarlo "solo como último recurso" y la aprobación tarda semanas o meses. Quincy va a monetizar. |
| js.org / is-a.dev | No | js.org solo acepta proyectos del ecosistema JavaScript (y `quincy.js.org` ya está tomado). is-a.dev es para páginas personales de programadores. |
| Freenom (`.tk`, `.ml`, `.ga`) | No | Cerró en 2024. |
| `.mx` gratis | No hay | Las promociones de "dominio gratis" vienen atadas a pagar hosting; el `.mx` gratis oficial es solo para escuelas. |
| `quincy.pages.dev`, `.netlify.app`, `.vercel.app` | No | Ya están ocupados. |

Nota: `quincymx` ya existe como usuario de GitHub; por eso el nombre es `quincy-mx`. GitHub confirma si está libre al crear la organización.

**Cómo funciona la mudanza (ya programada, se activa sola):** el robot `.github/workflows/quincy-pages.yml` usa `scripts/agentes/mudanza.py`.
Cuando existen la variable `QUINCY_SITIO_NUEVO`, la variable `QUINCY_REPO_NUEVO` y el secreto `QUINCY_PUBLICAR_TOKEN`, publica el sitio completo
en el repositorio nuevo con las direcciones cambiadas, y en el sitio viejo cada página redirige a la misma página nueva (conserva `?ref=`).
Los archivos de verificación de Google viajan con el sitio, así que la nueva propiedad de Search Console se verifica con un clic.
El código sigue viviendo en este repositorio; los agentes no cambian nada de su forma de trabajar.

**Después de la mudanza (agentes):** cambiar `SITE` en `scripts/agentes/salud_sitio.py`, `scripts/build_seo.py` y demás scripts a la dirección nueva,
y la dirección del sitio en `agentes/README.md`. Si algún día se compra un dominio (`quincy.mx` sigue libre, ~$300 a $700 MXN al año),
basta con cambiar `QUINCY_SITIO_NUEVO` a `https://quincy.mx/`: el robot escribe el archivo CNAME solo.

## 2. Referidos y afiliados financieros (México, solo regulados)

### Lo que encontré (oct 2026)

- **Programas formales de afiliados para sitios web:** no encontré ninguno público de bancos o SOFIPOs mexicanas. Las fintech captan con
  campañas propias, "invita a un amigo" y acuerdos con creadores por medio de agencias (por ejemplo, Stori trabajó con la plataforma Rizzult).
- **"Invita a un amigo" (referidos personales):** Mercado Pago ("Invita y gana", paga cuando el invitado hace su primer pago; montos según promoción),
  Openbank ("Conecta y gana", hasta $12,000 por referidos, primeros 30 referidos, vigencia al 31/12/2026, según su blog de agosto 2026).
  Son personales y con tope: **sirven para probar, no para escalar**, y hay que leer si sus términos permiten publicarlos en un sitio.
- **Redes de afiliados con ofertas financieras:** Admitad y financeAds trabajan ofertas de banca y tarjetas en Latinoamérica. Hay que revisar
  su catálogo para México una vez con dominio propio (sin dominio no te aceptan).
- **Mercado Libre Afiliados** (`mercadolibre.com.mx/l/afiliados`): no es financiero, paga por productos. Podría servir para "regalos con tu aguinaldo",
  pero choca con el mensaje de ahorro. **No recomendado por ahora.**

### Candidatos a acuerdo directo (ordenados por lo que le conviene a la persona, no por lo que pagan)

| Institución | Tipo y protección | Por qué encaja con Quincy | Cómo contactar |
|---|---|---|---|
| cetesdirecto (BONDDIA, CETES) | Gobierno federal | La opción más segura; ya la recomendamos. **No paga referidos**: se queda como recomendación honesta. | — |
| Openbank (Santander) | Banco, IPAB | Tiene programa de referidos activo; apartados con rendimiento. | Programa "Conecta y gana" en su app; alianzas: buscar contacto en `openbank.mx` |
| Nu México | Banco, IPAB | La cuenta más conocida; Cajitas. | Alianzas por LinkedIn / prensa de Nu México |
| Ualá, Plata, Revolut, Mifel | Bancos, IPAB | Cuentas con rendimiento con promociones fuertes en 2026. | Equipos de marketing/alianzas (LinkedIn) |
| Klar, Stori, DiDi, Finsus | SOFIPOs, Prosofipo (25 mil UDIS) | Tasas altas, pero menos protección: se presentan con esa advertencia. | Marketing/alianzas |
| Mercado Pago | IFPE, **sin seguro de depósitos** | Muy usado, pero no tiene IPAB. Se menciona con advertencia; último lugar. | "Invita y gana" en la app |

**Antes de activar cualquier enlace:** verificar que la entidad esté en el padrón de la CNBV y en el registro de la CONDUSEF (SIPRES),
y anotar en esta tabla la fecha de la verificación.

### Cómo se activa en el sitio (ya está listo)

- `js/core.js` tiene `CONFIG.REFERIDOS = {}`. Para activar uno se agrega, por ejemplo:
  `openbank: { nombre: "Abre tu cuenta Open", url: "https://…", nota: "Banco · protegido por el IPAB" }`.
- `FY.referidos(el)` pinta los botones solo si hay enlaces, siempre con el aviso **"Enlace de referido: Quincy puede recibir una comisión"**
  y `rel="sponsored"`. Si está vacío no se muestra nada.
- Página con el lugar ya puesto: `aguinaldo-a-rendir/` (debajo del resultado de la calculadora).
- Para medir: cada enlace llevará `?ref=quincy-<pagina>` cuando el programa lo permita; clics en Cloudflare.

### Momentos de mayor conversión (calendario)

| Cuándo | Gancho | Página |
|---|---|---|
| 1 nov a 20 dic | "Tu aguinaldo, ¿dónde lo pones a rendir?" | `aguinaldo-a-rendir/` (lista) |
| Enero | Cuesta de enero, fondo de emergencia | Pendiente: "fondo de emergencia" |
| Mayo a junio | "Tu PTU a rendir" | Pendiente: `ptu-a-rendir/` (misma plantilla) |
| Siempre | Tandas vs CETES | `tanda/` |

## 3. Quincy para empresas (B2B)

**A quién:** empresas con mucha gente de nómina que vive al día y pide adelantos o préstamos:
1. Maquilas y manufactura (norte y Bajío): rotación alta, aguinaldo y PTU grandes.
2. Call centers y BPO: plantillas jóvenes, alta rotación.
3. Retail, cadenas de restaurantes y tiendas de conveniencia.
4. Logística y repartidores con nómina.
5. Cajas de ahorro, Afores y universidades (como canal, no como cliente final).

**Propuesta de valor:** menos adelantos de nómina y menos rotación; tu gente sabe cuánto le toca de aguinaldo, vacaciones y PTU
(menos dudas a RR. HH.); Quincy con su logo, sin que la empresa maneje datos personales (todo corre en el teléfono).

**Precio sugerido:** piloto **gratis 60 días** para la primera empresa de cada sector (a cambio de poder medir uso y usar su opinión con permiso).
Después: **$4,900 MXN al mes** hasta 500 personas; taller en vivo de 1 hora "Tu aguinaldo y tu PTU sin estrés": **$6,000 MXN**.
(Precio de arranque para validar; se ajusta con las primeras 3 respuestas.)

**Correo listo para el dueño** (mandarlo a gente de RR. HH. que conozcas o por LinkedIn):

> **Asunto:** Que tu equipo sepa cuánto le toca de aguinaldo (piloto gratis)
>
> Hola, [nombre]:
>
> Soy [tu nombre], hago Quincy, una app gratuita que le dice a cada persona cuánto le toca de aguinaldo, vacaciones y PTU según la ley,
> y cuánto puede gastar al día para llegar a la quincena. No pide registro y no guarda datos personales.
>
> Estoy buscando 3 empresas para un piloto gratis de 60 días: Quincy con su logo para su equipo y una plática corta antes del aguinaldo.
> A cambio solo te pido tu opinión al final.
>
> ¿Te late una llamada de 15 minutos esta semana o la que entra?
>
> Puedes verla aquí: https://alexsnri.github.io/README/quincy/empresas.html
>
> Saludos,
> [tu nombre] · [tu teléfono]

**Pendiente en el sitio:** mejorar `empresas.html` (piloto gratis arriba, "qué se lleva tu empresa" en 3 puntos, contacto directo por correo
o WhatsApp en lugar del formulario de GitHub). Lo hago en la próxima corrida, coordinado con Producto para no chocar con el rediseño.

## 4. Patrocinios

**Cuándo:** con 5,000+ seguidores entre Instagram y TikTok o 20,000 visitas al mes (meta de fase 2).
**Marcas afines:** bancos y SOFIPOs reguladas, aseguradoras (seguro de vida y gastos médicos accesibles), Afores, cajas de ahorro,
apps de nómina y beneficios para empleados, CONDUSEF/PROFEDET para campañas de educación (sin pago, por alcance).
**No:** préstamos rápidos con tasas altas, casinos, apuestas, cripto especulativa.

**Propuesta de temporada "Aguinaldo con Quincy" (1 dic a 20 dic):**
- Mención "Presentado por [marca]" en la calculadora de aguinaldo y en la tarjeta para compartir.
- 3 reels/TikToks con el gancho de temporada y la marca integrada.
- Una sección "Pon tu aguinaldo a rendir con [marca]" con aviso de patrocinio y comparativa honesta intacta.
- Reporte final con visitas, cálculos y veces compartido (de Cloudflare, sin datos personales).
- Precio sugerido para el primer patrocinio: a definir con las métricas reales de diciembre de 2026.

## 5. Premium y anuncios

Sin datos de demanda todavía. Premium solo si la gente lo pide (reporte PDF de "lo que me toca", plan de ahorro guiado).
Anuncios: solo en páginas de buscadores y solo si no bajan el uso; no antes de fase 2.

## Lo que necesito del dueño

Todo es gratis. Solo lo que GitHub no deja hacer a nadie más que a ti (unos 10 minutos en total):

1. **Crear la organización gratis:** entra a https://github.com/account/organizations/new?plan=free , nombre `quincy-mx`, tu correo,
   "My personal account". (Si dice que no está disponible, usa `holaquincy` y avísame en la bitácora.)
2. **Crear el repositorio del sitio:** https://github.com/organizations/quincy-mx/repositories/new , nombre exacto `quincy-mx.github.io`, Public, sin README.
3. **Crear el permiso para que el robot publique allá:** https://github.com/settings/personal-access-tokens/new
   → Resource owner: `quincy-mx` → Only select repositories: `quincy-mx.github.io` → Repository permissions: **Contents: Read and write**
   → Expiration: 1 año → Generate. Copia el token.
4. **Guardarlo en este repositorio:** https://github.com/Alexsnri/README/settings/secrets/actions/new → Name `QUINCY_PUBLICAR_TOKEN` → pega el token.
5. **Dos variables:** https://github.com/Alexsnri/README/settings/variables/actions/new
   → `QUINCY_SITIO_NUEVO` = `https://quincy-mx.github.io/` y luego `QUINCY_REPO_NUEVO` = `quincy-mx/quincy-mx.github.io`.
6. **Primera publicación:** https://github.com/Alexsnri/README/actions/workflows/quincy-pages.yml → Run workflow.
7. **Encender Pages en el repositorio nuevo:** https://github.com/quincy-mx/quincy-mx.github.io/settings/pages → Source: Deploy from a branch
   → Branch `main`, carpeta `/ (root)` → Save. Espera 2 minutos y abre https://quincy-mx.github.io/
8. **Segunda publicación** (Run workflow otra vez): ahora el robot ve que el sitio nuevo ya abre y pone las redirecciones en el viejo.
   Mientras el nuevo no responda, el viejo se queda igual: no hay riesgo de dejar a nadie en una página rota.
9. **Google:** https://search.google.com/search-console → Agregar propiedad → Prefijo de URL `https://quincy-mx.github.io/`
   → Verificar con "Archivo HTML" (ya está subido) → Sitemaps → `sitemap.xml`.

Para cobrar más adelante (fase 2, no urge): cuenta bancaria y RFC con actividad empresarial o RESICO, porque los programas y las empresas piden factura.
El registro de la marca en el IMPI lo sigue el agente de Marca.

## Registro de corridas

- 2026-10-28 (3): el robot ya no redirige el sitio viejo hasta comprobar que el nuevo responde; pasos del dueño detallados.
- 2026-10-28 (2): el dueño pidió dominio gratis. Búsqueda a fondo; elegida la organización de GitHub `quincy-mx`. Mudanza automática programada (`mudanza.py` + robot de publicación).
- 2026-10-28: plan inicial; página `aguinaldo-a-rendir/` publicada sin referidos; `CONFIG.REFERIDOS` y `FY.referidos()` en `js/core.js`.
