# Socios · productos digitales con creadores

Encontramos creadores de finanzas personales con audiencia que confía en ellos, les proponemos un
producto digital hecho para su gente, lo construimos, lo vendemos en Whop y Whop reparte cada venta
automáticamente: 50% el creador y 50% nosotros.

## Decisiones (y por qué)

| Tema | Decisión | Por qué |
|---|---|---|
| Nicho | **Finanzas personales para trabajadores en México y Latinoamérica** (ahorro, deudas, quincena, presupuesto) | Es un tema que crece y no pasa de moda. La gente sí paga por plantillas y planes de dinero y confía en quien le explica. Además ya tenemos Quincy como prueba real. Se excluyen trading, cripto y «hazte rico». |
| Vender, cobrar, entregar y repartir | **Whop + página propia en tu dominio** | Whop cobra, entrega el producto y le paga al creador su parte en cada venta («revenue share»). Página propia para que se vea de marca y no genérico. |
| Correo | **Tu Gmail personal** (gratis); dominio y Google Workspace cuando haya ventas | Para 20 correos personalizados al día basta. Instantly y ListKit no hacen falta. |
| Buscar creadores | **API de YouTube (gratis)** + el script `scripts/buscar_creadores.py` | 10,000 consultas al día sin costo. Instagram y TikTok se revisan a mano desde el enlace del canal. |
| Producto | Gratis: Google Sheets o Notion, Canva o Gamma, y código aquí si es app | Sin suscripciones. |
| Agentes | Claude Code (esta sesión) | Ya lo pagas, no hay costo extra. |

**Costo:** $0 al mes por ahora. Whop no cobra mensualidad; se queda
un porcentaje de cada venta (~3% más el procesamiento de tarjeta). Revisa la cifra actual en
https://docs.whop.com/fees.

## Los agentes

| Agente | Archivo | Qué hace |
|---|---|---|
| Plan de la plataforma | `andamio.md` | Marca, producto insignia, ediciones con creadores y orden de trabajo. |
| Cazador | `agentes/1-cazador.md` | Encuentra creadores y los califica. |
| Escritor | `agentes/2-escritor.md` | Primer correo personalizado. |
| **Closer** | `agentes/3-closer.md` | Contesta como experto en ventas hasta el sí o la llamada. |
| Productor | `agentes/4-productor.md` | Diseña y construye el producto. |
| Lanzador | `agentes/5-lanzador.md` | Whop, reparto automático y lanzamiento de 7 días. |

La oferta (reparto, qué pone cada quien, qué nunca se promete) vive solo en `agentes/oferta.md`.
También están como agentes de Claude Code en `.claude/agents/`: en cualquier sesión de este repo puedes
pedir «usa el closer con este correo».

## Pasos para arrancar (en orden)

1. **Marca:** Andamio (ver `andamio.md`), pero a los creadores se les escribe desde tu Gmail personal y con tu nombre (`socios/data/remitente.json`).
2. **Llave de YouTube:** ya está creada. En Google Cloud, restríngela a «YouTube Data API v3».
3. Cuando haya ventas: dominio propio + Google Workspace, con SPF, DKIM y DMARC.
4. **Buscar:** `python3 socios/scripts/buscar_creadores.py` → `socios/data/prospectos.csv`.
5. **Whop:** crea tu negocio (o usa el que tienes) y activa los pagos a tu cuenta.
6. **Conectar tu Gmail a Claude** para que el Closer revise respuestas cada hora y te deje
   los borradores listos. Tú solo das «Enviar» desde el celular.
7. Calienta el buzón: 5 correos al día la primera semana, luego subes 5 por semana hasta 20.

## Privacidad

Este repo es público. `socios/data/` (correos y conversaciones) está en `.gitignore` y no se sube nunca.
