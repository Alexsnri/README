# Plan de monetización de Quincy

Plan vivo del agente de Monetización. Última revisión: **2026-11-02**. Fase actual: **1 · Audiencia** (solo preparar, no cobrar).
Próxima revisión: 15 de noviembre de 2026.

## Resumen en 5 líneas

1. **Dirección propia gratis: hecha.** Quincy vive en `https://quincy-mx.github.io/` desde el 28 oct; la dirección vieja redirige. Contacto activo: hola.quincymx@gmail.com.
2. **Referidos financieros = el ingreso más grande y natural**, en el momento en que la gente tiene dinero (aguinaldo en dic, PTU en may). Ya está lista la página que los llevará: `aguinaldo-a-rendir/` (sin enlaces todavía).
3. **No hay programas de afiliados abiertos** de Nu, Klar, Openbank, Stori, Plata, Ualá ni CETES en México. Hay programas de "invita a un amigo" (personales, con tope) y acuerdos directos con las fintech o por redes de afiliados. El camino real es **escribirles directo** cuando haya tráfico.
4. **B2B es lo único que puede dar dinero este año:** piloto gratis de 90 días con plática de aguinaldo. Kit listo en `estado/b2b-kit.md`; **correos antes del 13 de noviembre**.
5. **Patrocinio de temporada** (aguinaldo/PTU) cuando haya 5,000+ seguidores o 20,000 visitas al mes.

## 1. Dominio propio

**Hecho (28 oct 2026):** organización gratis de GitHub `Quincy-mx` → **https://quincy-mx.github.io/**. Los dominios gratis "de verdad"
(DigitalPlat `.us.kg`/`.dpdns.org`/`.qzz.io`) aparecen en la lista negra de Spamhaus o fueron suspendidos por phishing; EU.org desalienta
sitios comerciales; js.org es solo para proyectos de JavaScript; Freenom cerró. El robot `quincy-pages.yml` publica con `scripts/agentes/mudanza.py`.
Si algún día se compra `quincy.mx` (~$300 a $700 MXN al año), basta con cambiar la variable `QUINCY_SITIO_NUEVO` a `https://quincy.mx/`.
**Ojo para afiliados:** algunas redes piden dominio propio; si una nos rechaza por `github.io`, ese es el momento de comprar `quincy.mx`.

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

**Precio sugerido:** piloto **gratis 90 días** para las primeras 10 organizaciones (así lo dice `empresas.html`) (a cambio de poder medir uso y usar su opinión con permiso).
Después: **$4,900 MXN al mes** hasta 500 personas; taller en vivo de 1 hora "Tu aguinaldo y tu PTU sin estrés": **$6,000 MXN**.
(Precio de arranque para validar; se ajusta con las primeras 3 respuestas.)

**Gancho nuevo: NOM-035.** Obliga a todos los centros de trabajo a prevenir factores de riesgo psicosocial; el estrés por dinero es uno.
Quincy no certifica nada: se ofrece como una acción de bienestar que RR. HH. puede documentar.

**Kit completo para el dueño:** `estado/b2b-kit.md` (a quién escribir, búsquedas de LinkedIn, nota de conexión, 3 correos, respuestas a
objeciones, qué pedir cuando digan que sí y tabla de seguimiento). Fecha límite útil para diciembre: **viernes 13 de noviembre**.

**En el sitio:** `empresas.html` con la sección del piloto (90 días); "Solicitar piloto" abre un correo ya escrito a hola.quincymx@gmail.com.
Enlace con marca probado el 2 nov en quincy-mx.github.io (`app.html?marca=…&color=…&cta=…&cta_txt=…`): funciona, sin errores.

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

1. **Esta semana, antes del viernes 13 de noviembre · ventas a empresas (30 min al día).** Abre `quincy/agentes/estado/b2b-kit.md`:
   escribe a 10 personas de RR. HH. que conozcas con el correo 1, y manda 10 solicitudes de LinkedIn al día con la nota de conexión.
   Anota en la tabla del kit a quién escribiste y qué contestó.
2. **Cuando una empresa diga que sí:** pide su logo o nombre, su color y el enlace de su programa, y pásaselos a cualquier agente.
3. **Referidos (opcional, 5 min):** si usas Openbank, Mercado Pago o Nu, abre en la app la sección de "invita a un amigo", lee los términos y
   dime si permiten compartir el enlace en un sitio web. Si sí, pégalo en la bitácora y lo pongo en `aguinaldo-a-rendir/` con su aviso.
4. **Para cobrar más adelante (no urge):** cuenta bancaria y RFC con actividad empresarial o RESICO, porque las empresas piden factura.

## Registro de corridas

- 2026-11-02 (corrida del día 1): congelamiento del sitio hasta el martes 3, así que solo plan y kit. Nuevo `estado/b2b-kit.md` (gancho NOM-035, fecha límite 13 nov). Enlace con marca probado en la dirección nueva. Referidos: sigue sin haber programa público de afiliados de bancos o SOFIPOs en México; no encontré términos de "invita a un amigo" de Nu México que permitan publicarlo.
- 2026-10-28 (5): `empresas.html` con la sección del piloto y contacto por correo listo (`CONFIG.CONTACT_EMAIL`). Desperté a Director, SEO, Contenido, Producto y Ley y datos a pedido del dueño.
- 2026-10-28 (4): **mudanza hecha.** https://quincy-mx.github.io/ en línea; la dirección vieja redirige (probado con `?ref=wa`). Salud del sitio: 0 errores. Pendiente del dueño: cambiar el token que pegó en el chat y dar de alta la propiedad en Search Console.
- 2026-10-28 (3): el robot ya no redirige el sitio viejo hasta comprobar que el nuevo responde; pasos del dueño detallados.
- 2026-10-28 (2): el dueño pidió dominio gratis. Búsqueda a fondo; elegida la organización de GitHub `quincy-mx`. Mudanza automática programada (`mudanza.py` + robot de publicación).
- 2026-10-28: plan inicial; página `aguinaldo-a-rendir/` publicada sin referidos; `CONFIG.REFERIDOS` y `FY.referidos()` en `js/core.js`.
