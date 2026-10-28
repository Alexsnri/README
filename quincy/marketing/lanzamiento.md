# Quincy · Plan de lanzamiento

**Fecha de lanzamiento:** lunes 2 de noviembre de 2026, en plena temporada de aguinaldo (se paga a más tardar el 19 de diciembre).

**Lo que ya trabaja solo** (no tienes que hacer nada):

- Sitio publicado en GitHub Pages, gratis: https://quincy-mx.github.io/
- 6 páginas de calculadora pensadas para Google (aguinaldo, finiquito, vacaciones, PTU, tanda y quincena). Cada una tiene preguntas frecuentes con datos estructurados.
- Sitemap, robots.txt y aviso automático a Bing, Yandex, Seznam y Naver vía IndexNow en cada publicación.
- Tarjetas para compartir (historias de 1080×1920) dentro de la app: cada usuario que comparte trae a otros.
- Enlaces de tanda: cuando alguien manda su tanda al grupo de WhatsApp, cada miembro abre Quincy.
- Tasas de CETES actualizadas cada semana con GitHub Actions (necesita el secreto `BANXICO_TOKEN`).

- Robot de Instagram (GitHub Actions), listo pero apagado: necesita un token de una cuenta de desarrollador de Meta, que pide verificar un teléfono por SMS.

**Lo que necesita a una persona** (una hora, una vez; detalle en `marketing/guia.html`):

1. Instagram: cuenta profesional y las 23 publicaciones programadas desde la app con `marketing/programar.html` (sin Facebook).
2. TikTok: los 8 reels programados con Metricool (gratis) o en 3 ratos desde TikTok Studio.
3. Dar de alta el sitio en Google Search Console y enviar `sitemap.xml`.
4. Mandar los mensajes de WhatsApp el día 1 y publicar en Reddit el día 2.

## Canales y orden

| Orden | Canal | Acción | Costo |
|---|---|---|---|
| 1 | WhatsApp | Mandar la calculadora de aguinaldo a 10 contactos y 3 grupos de trabajo (mensaje abajo). | $0 |
| 2 | Instagram, TikTok y Shorts | 8 reels con gancho escrito, programados una vez en cada red. | $0 |
| 3 | Instagram y Facebook | 12 posts y 5 historias (`posts/`, `stories/`). | $0 |
| 4 | Reddit | r/MexicoFinanciero y r/mexico (texto abajo). | $0 |
| 5 | Grupos de Facebook de tandas y ahorro | La página /tanda/ y la ruleta. | $0 |
| 6 | Creadores de finanzas y derechos laborales | Mensaje directo a 20 creadores. | $0 |
| 7 | Prensa | Correo a periodistas de finanzas personales (2 rondas en noviembre). | $0 |
| 8 | LinkedIn y recursos humanos | Post para RR. HH. y mensajes a PyMEs con /empresas.html. | $0 |
| 9 | Product Hunt | Lanzamiento en inglés con el video. | $0 |

## Mensajes de WhatsApp

**A contactos:**

> Oye, hice una app gratis que te dice cuánto te toca de aguinaldo (con la ley de 2026) y cuánto puedes gastar al día para llegar a la quincena. No pide registro. ¿Me dices si te sirve? https://quincy-mx.github.io/aguinaldo/

**A grupos de trabajo:**

> ¿Ya saben cuánto nos toca de aguinaldo? Aquí lo calculan en 10 segundos, gratis y sin registro: https://quincy-mx.github.io/aguinaldo/

**A grupos de tanda o familia:**

> Para que no haya pleitos con los números: aquí sorteamos los turnos con una ruleta y a todos les llega el calendario 🎡 https://quincy-mx.github.io/tanda/

## Reddit

**r/MexicoFinanciero**

Título: Hice una calculadora gratis de aguinaldo, finiquito y vacaciones con la ley de 2026 (sin registro)

> Hola. Hice Quincy porque cada noviembre veo las mismas preguntas: ¿cuánto me toca de aguinaldo?, ¿cuánto paga de ISR?, ¿cuánto me dan si renuncio?
>
> Qué hace:
> - Aguinaldo, vacaciones (con "vacaciones dignas"), prima vacacional, tope de PTU, finiquito y liquidación con el salario mínimo y la UMA de 2026.
> - Un límite diario de gasto para llegar a la siguiente quincena.
> - Tandas: sorteo de turnos con ruleta, calendario para el grupo y cuánto gana o pierde cada número frente a CETES.
>
> No pide cuenta, no conecta tu banco y tus datos se quedan en tu teléfono. Es gratis.
>
> Si encuentran un error en algún cálculo, díganmelo y lo corrijo.
>
> https://quincy-mx.github.io/

**r/mexico** (segundo post, día 22, con datos reales de uso)

Título: Calculé qué número de la tanda conviene más (y cuánto pierde el último)

> Comparé una tanda de 10 personas con $1,000 por quincena contra invertir en CETES al 6.23%. El número 1 gana unos $115 y el número 10 pierde unos $114: el primero recibe un préstamo sin intereses y el último ahorra sin rendimiento. Hice una herramienta gratis para calcularlo con tus números y sortear los turnos: https://quincy-mx.github.io/tanda/

## Mensaje para creadores

> Hola, [nombre]. Hice Quincy, una app web gratis que le dice a cualquier trabajador cuánto le toca de aguinaldo, vacaciones, prima, PTU y finiquito con la ley de 2026, cuánto puede gastar al día para llegar a la quincena y qué número de la tanda le conviene. No pide registro ni datos personales.
> Creo que le queda a tu contenido en esta temporada de aguinaldo. No te pido nada a cambio; si te sirve, úsala. Si quieres una versión con tu marca para tu comunidad, también la tengo.
> https://quincy-mx.github.io/

## Correo para periodistas

Asunto: App gratuita calcula aguinaldo, finiquito y qué número de la tanda conviene

> Hola, [nombre]:
>
> Hay 22.9 millones de puestos de trabajo formales en el IMSS (septiembre de 2026). Todos tienen derecho a aguinaldo, vacaciones y prima vacacional, y mucha gente no sabe cuánto le toca. Además, millones de personas ahorran en tandas sin saber que el número que eligen cambia lo que ganan o pierden.
>
> Quincy es una herramienta gratuita hecha en México que:
> - calcula aguinaldo, vacaciones, prima vacacional, tope de PTU, finiquito y liquidación con los valores de 2026;
> - le dice a cada persona cuánto puede gastar al día para llegar a su siguiente quincena;
> - sortea los turnos de una tanda y calcula cuánto gana o pierde cada número frente a CETES.
>
> No pide registro y no guarda datos en servidores. Puedo compartir datos de uso y ejemplos para tu nota.
>
> https://quincy-mx.github.io/

## Product Hunt (inglés)

- **Name:** Quincy
- **Tagline:** Know what you're owed, when you get it and what you can spend today
- **Description:** Quincy is a free, no-signup money app for Mexican workers. It turns labor law into numbers (year-end bonus, vacation, profit sharing, severance) and gives you one number a day: how much you can spend until your next payday. It also runs rotating savings circles ("tandas") with a fair wheel draw, a shared calendar and the real cost of each turn. Your data never leaves your phone.
- **Media:** use `video/reel-01-app-aguinaldo.mp4` and the feed images.
- **First comment:** Why I built it, what's next (an employer edition as an employee benefit) and a request for feedback on the calculations.

## LinkedIn (recursos humanos)

> En noviembre, recursos humanos recibe la misma pregunta cientos de veces: "¿cuánto me toca de aguinaldo?".
> Hicimos Quincy: una herramienta gratuita, con la marca de tu empresa, donde cada colaborador ve su aguinaldo, vacaciones y PTU con la ley de 2026 y un límite diario de gasto para llegar a la quincena. Sin registro y sin datos personales en servidores.
> Buscamos 10 empresas para un piloto gratis de 90 días: https://quincy-mx.github.io/empresas.html

## Métricas a vigilar

| Métrica | Meta del mes 1 | Cómo se mide |
|---|---|---|
| Visitas a la calculadora de aguinaldo | 20,000 | Analítica sin cookies (Cloudflare, opcional) o Search Console |
| Personas que ponen sus números en "Hoy" | 35% | Evento de configuración |
| Tarjetas compartidas | 5% de visitantes | Clic en compartir |
| Tandas creadas y enviadas por WhatsApp | 1,000 | Visitas con `?t=` |
| Regreso a los 7 días | 20% | Analítica |
| Solicitudes de piloto de empresas | 10 | Formulario en GitHub |

Para activar la analítica: crea un sitio gratuito en Cloudflare Web Analytics y pega el token en `CF_ANALYTICS_TOKEN` de `js/core.js`.
