# Andamio · plan de la plataforma

> Guías de dinero profundas, hechas en México y Latinoamérica, escritas con los creadores que la gente ya sigue.

## La idea en una frase

Un catálogo de productos de dinero **que de verdad valgan lo que cuestan**. Cada uno nace de lo que pide
la audiencia de un creador, el creador lo presenta y Whop reparte cada venta en automático.

## Cómo encaja todo (pago, entrega, desarrollo y distribución)

| Pieza | Herramienta | Costo |
|---|---|---|
| Página y catálogo (3D, interactivo) | GitHub Pages: `alexsnri.github.io/README/andamio/`; después, una organización de GitHub `andamio-…` para tener `andamio-….github.io` | $0 |
| Cobro, entrega de archivos y acceso | Whop (un producto por edición) | ~3% + tarjeta por venta |
| Reparto con cada creador | Whop revenue share (automático en cada venta) | incluido |
| Capítulo gratis a cambio del correo | Producto **gratis** en Whop: entrega el capítulo y guarda el correo del lector | $0 |
| Correo de Andamio | Gmail nuevo de la marca (sin dominio por ahora) | $0 |
| Encontrar creadores | `scripts/buscar_creadores.py` (API de YouTube) | $0 |
| Escribir, diseñar y programar | Claude Code + agentes de `agentes/` | ya pagado |

Sin dominio propio el correo sale de Gmail. Para 20 correos personales al día funciona; cuando lleguen las
primeras ventas, el dominio y Workspace son la primera compra.

## El producto insignia: «Las siete quincenas»

Un libro en forma de historia, como *El hombre más rico de Babilonia* pero en el México de hoy: tandas,
quincenas, tarjetas, CETES, Afore, aguinaldo y PTU. Cada capítulo es una historia que se queda en la
cabeza **y** un sistema que se aplica esa misma quincena.

**Historia:** Daniel, 26 años, almacenista en Iztapalapa, gana $7,500 a la quincena y debe dos tarjetas.
Doña Chela tiene un puesto de jugos en el mercado, organiza tandas desde hace 30 años y, sin que nadie lo
sepa, es dueña de tres locales. Le da una lección por quincena con una condición: no hay siguiente lección
hasta que aplique la anterior.

| Quincena | Lección | Lo que el lector hace esa quincena |
|---|---|---|
| 1 | **Lo primero es tuyo.** Antes de pagarle a nadie, apártate el 10%. | Transferencia automática el día de pago. |
| 2 | **Cada peso con nombre.** Un presupuesto por quincena, no por mes. | Plantilla de quincena; cazar gastos hormiga. |
| 3 | **El colchón.** Un fondo para que una emergencia no se vuelva deuda. | Meta de 1 mes de gastos y dónde guardarla. |
| 4 | **La deuda que muerde.** Por qué el pago mínimo es una trampa (con números reales de CAT). | Plan avalancha o bola de nieve; cómo negociar con el banco. |
| 5 | **Que el dinero trabaje.** Interés compuesto, inflación, CETES y aportaciones voluntarias a la Afore, explicados sin vender nada. | Primera inversión con poco dinero. |
| 6 | **Lo que te toca.** Aguinaldo, PTU, vacaciones, prima y finiquito como aceleradores (calculadoras de Quincy). | Calcular lo suyo y decidir a qué va cada peso extra. |
| 7 | **Ganar más y protegerlo.** Pedir aumento, ingreso extra y no perder lo ganado. | Guion para pedir aumento; lista de protección. |

Epílogo: Daniel un año después, y el secreto de Doña Chela.

**Lo que trae (para que nadie sienta que tiró su dinero):**
- Libro en PDF y EPUB, de 150 a 200 páginas, diseñado (no es un Word exportado).
- Cuaderno de trabajo en Google Sheets: quincena, deudas, colchón y metas, con fórmulas.
- Plan de 30 días con una acción al día.
- Audiolibro (opcional, con la voz que elijas en ElevenLabs).
- Garantía de 14 días: si no le sirvió, se le devuelve su dinero. Eso da más confianza que cualquier
  testimonio.

**Precio:** $249 MXN libro + cuaderno · $449 MXN con audiolibro y plan de 30 días.

**Cuidado legal:** es educación financiera, no asesoría de inversión. No recomienda acciones, criptos ni
productos de ningún banco, y cada cifra de ley viene de fuente oficial de 2026.

## Las ediciones con cada creador

Cuando un creador acepta, el Productor lee su perfil (videos, comentarios, preguntas que se repiten) y
arma **su edición**:
- **Prólogo del creador**, escrito con su voz a partir de sus videos (él lo aprueba).
- **Capítulo extra** sobre lo que más le pregunta su audiencia (por ejemplo, deudas de Coppel, vender en
  línea o ahorrar en pareja).
- Su propio producto en Whop con revenue share 50/50 y su enlace.

Después vienen los productos que pidan sus compradores: retos, plantillas, mini cursos o una membresía.
El catálogo crece con lo que la gente ya pidió, no con lo que se nos ocurra.

## Orden de trabajo

1. Página de Andamio en 3D: portada, biblioteca, capítulo gratis y «Para creadores».
2. Escribir «Las siete quincenas»: primero el capítulo 1 completo (sirve de capítulo gratis y de muestra
   para los creadores), luego los demás.
3. Cuaderno de trabajo y plan de 30 días.
4. Montar en Whop: producto gratis (capítulo 1) y producto de pago.
5. Primeros 10 correos a creadores con el capítulo 1 como muestra.
