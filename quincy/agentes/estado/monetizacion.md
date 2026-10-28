# Plan de monetización de Quincy

Plan vivo del agente de Monetización. Última revisión: **2026-10-28**. Fase actual: **1 · Audiencia** (solo preparar, no cobrar).
Próxima revisión: 1 de noviembre de 2026.

## Resumen en 5 líneas

1. **Primero el dominio:** `quincy.mx` parece libre (sin registro en DNS al 28 oct 2026). Cuesta unos $300 a $700 MXN al año. Sin dominio propio casi ningún programa de afiliados te acepta.
2. **Referidos financieros = el ingreso más grande y natural**, en el momento en que la gente tiene dinero (aguinaldo en dic, PTU en may). Ya está lista la página que los llevará: `aguinaldo-a-rendir/` (sin enlaces todavía).
3. **No hay programas de afiliados abiertos** de Nu, Klar, Openbank, Stori, Plata, Ualá ni CETES en México. Hay programas de "invita a un amigo" (personales, con tope) y acuerdos directos con las fintech o por redes de afiliados. El camino real es **escribirles directo** cuando haya tráfico.
4. **B2B** (`empresas.html`) es la segunda fuente: piloto gratis de 60 días y después cuota mensual por empresa.
5. **Patrocinio de temporada** (aguinaldo/PTU) cuando haya 5,000+ seguidores o 20,000 visitas al mes.

## 1. Dominio propio

Comprobado el 28 oct 2026 consultando DNS público (Google DNS). "Sin registro" = el dominio no existe en DNS; casi seguro está libre,
pero solo el registrador lo confirma al comprar.

| Dominio | Estado | Precio aproximado por año | Comentario |
|---|---|---|---|
| **quincy.mx** | Sin registro (probablemente libre) | ~$300 a $700 MXN (≈ US$25 a 40) | **El mejor.** Corto, mexicano, da confianza. |
| quincyapp.mx | Sin registro | igual que .mx | Plan B. |
| quincy.lat | Sin registro | ~US$1 a 2 el 1er año, ~US$26 a 50 al renovar | Barato al inicio, caro al renovar. No recomendado. |
| usaquincy.com / holaquincy.com | Sin registro | ~US$10 a 12 | Plan C si `.mx` falla. |
| quincy.com.mx | Ocupado | — | Registrado (servidores de Triara). |
| quincy.app, quincyapp.com, quincymx.com | Ocupados | — | — |

Precios de referencia: comparadores de precios de dominios (domainoffer.net, jul 2026) y guías de GoDaddy/Tiendanube. Confirmar al comprar;
el primer año suele ser promoción y conviene ver el precio de **renovación** y si incluye IVA.

**Dónde comprarlo:** Akky (`https://www.akky.mx`, registrador mexicano, factura en pesos, IVA incluido) o Cloudflare Registrar
(precio de costo, sin margen, si acepta `.mx` al momento de comprar). Activar renovación automática y bloqueo de transferencia.

**Cómo conectarlo (lo hacen los agentes después de que compres):** el sitio vive dentro del repositorio `Alexsnri/README`, en la carpeta `quincy/`.
Un dominio en GitHub Pages apunta a todo el repositorio, así que quedaría `quincy.mx/quincy/…` y en la raíz saldría tu página `index.html` actual.
Opciones:
- **A (recomendada):** crear un repositorio nuevo vacío `Alexsnri/quincy` y dar acceso a Claude. Los agentes mueven el sitio ahí y queda
  `quincy.mx/aguinaldo/`, limpio. El sitio viejo redirige al nuevo para no perder Google.
- **B (rápida):** conectar `quincy.mx` a este repositorio tal cual y vivir con `quincy.mx/quincy/`.

En ambos casos, en el panel DNS del dominio: 4 registros **A** para `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`,
y un **CNAME** `www` → `alexsnri.github.io`. Luego en GitHub: Settings → Pages → Custom domain → `quincy.mx` → Enforce HTTPS.
Los agentes actualizan `CONFIG.SITE`, canónicas, sitemap y dan de alta la nueva propiedad en Search Console (esto último lo hace el dueño, 2 minutos).

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

En orden. Nada cuesta más de unos cientos de pesos y nada se hace a tu nombre sin ti.

1. **Comprar `quincy.mx`** (≈ $300 a $700 MXN al año) en `https://www.akky.mx` o en Cloudflare Registrar. Activa renovación automática.
2. **Decidir dónde vive:** crear un repositorio vacío `Alexsnri/quincy` (recomendado) o conectar el dominio a este repositorio. Avísanos en la bitácora.
3. **Registro de marca "Quincy" en el IMPI** (clases 36 y 9), ya pedido por el agente de Marca. Ayuda a cerrar acuerdos con bancos.
4. **Cuenta para cobrar:** una cuenta bancaria a tu nombre (o de tu empresa) y tu **RFC con régimen de actividad empresarial o RESICO**
   en el SAT, porque los programas de afiliados y las empresas te van a pedir factura.
5. **Probar un referido personal** (opcional, ahora): si ya usas Openbank o Mercado Pago, copia tu enlace de "invita a un amigo",
   lee sus términos y, si permiten compartirlo públicamente, pégalo en la bitácora. Yo lo pongo en la página con su aviso.
6. **B2B:** manda el correo de arriba a 3 personas de RR. HH. que conozcas.

## Registro de corridas

- 2026-10-28: plan inicial; página `aguinaldo-a-rendir/` publicada sin referidos; `CONFIG.REFERIDOS` y `FY.referidos()` en `js/core.js`.
