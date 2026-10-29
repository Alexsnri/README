"""Banco de frases de Jarvis. Tono: chavo, sarcástico, mexicano, con cariño. Sin ofender a nadie más que al jefe.

Placeholders: {saludo} {n} {v24} {v7} {pagina} {fuentes} {nombre} {hecho} {quien} {cuando} {tarea} {dias}
"""

INTROS = [
    "{saludo}, jefe. Aquí reportándose su mayordomo favorito. El único, pero favorito.",
    "{saludo}, jefe. Abróchese, que vienen noticias.",
    "Qué onda, jefe. {saludo}. Le traigo el chisme del negocio.",
    "{saludo}, patrón. Ya llegó su Jarvis, versión tianguis pero con ganas.",
    "Jefe, {saludo}. Prepárese, que esto no se lee solo… bueno, sí, lo leo yo.",
    "Ajá, ya se subió. {saludo}, jefe. Va el resumen, sin comerciales.",
    "{saludo}, jefe. Respire hondo, que le voy a hablar de su imperio.",
    "Bienvenido a bordo, jefe. {saludo}. Aquí su asistente que no cobra horas extra.",
    "{saludo}, jefecito. Arranque usted la camioneta, yo arranco el chisme.",
    "Atención, atención: el jefe ha entrado al vehículo. {saludo}.",
    "{saludo}, jefe. Le tengo números, chismes y uno que otro regaño.",
    "Ey, jefe, {saludo}. Ponga atención, que no lo voy a repetir… bueno, sí, cada vez que se suba.",
    "{saludo}, jefe. Mientras usted maneja, sus empleados digitales chambean. Así de injusta es la vida.",
    "Qué tal, jefe. {saludo}. Agárrese del volante, que vienen datos.",
    "{saludo}, jefe. Reporte oficial de Quincy, edición no autorizada por nadie.",
    "Jefe, {saludo}. Le habla Jarvis, su conciencia financiera con voz de locutor.",
    "{saludo}, jefe. Otra vez usted. Bueno, va.",
    "{saludo}, jefe. Lo extrañé. Mentira, estuve ocupado, pero va el resumen.",
]

SALUDOS = {"mañana": ["Buenos días", "Buen día", "Buenos días, madrugador"],
           "tarde": ["Buenas tardes", "Buena tarde", "Muy buenas tardes"],
           "noche": ["Buenas noches", "Buena noche", "Buenas noches, trasnochado"]}

LANZAMIENTO = [
    "Faltan {dias} días para el lanzamiento. Tic tac, jefe.",
    "Quedan {dias} días para lanzar. Ya se siente la presión, ¿o nomás soy yo?",
    "{dias} días para el lanzamiento. Ni modo, ya no hay para dónde hacerse.",
    "Cuenta regresiva: {dias} días para el lanzamiento. Que no le gane el nervio.",
    "En {dias} días sale Quincy al ruedo. Usted tranquilo, yo nervioso por los dos.",
]
LANZAMIENTO_MANANA = [
    "Mañana es el lanzamiento, jefe. Ya ni modo de echarse para atrás.",
    "Mañana se lanza Quincy. Duerma bien, que mañana sí hay chamba de la buena.",
    "Mañana es el gran día. Planche la camisa, aunque sea para el reel.",
]
LANZAMIENTO_HOY = [
    "Hoy es el lanzamiento. Publique el reel y mande los WhatsApp, que no se publican con la mente.",
    "Hoy lanzamos, jefe. Si no publica el reel, el lanzamiento es nomás en su cabeza.",
    "Día de lanzamiento. Hoy no se vale decir 'al rato lo subo'.",
]
AGUINALDO = [
    "Y {dias} días para la fecha del aguinaldo: temporada alta.",
    "Faltan {dias} días para el aguinaldo. Es nuestro Mundial, jefe.",
    "{dias} días para el aguinaldo: medio México va a buscar cuánto le toca. Que nos encuentren.",
]

VISITAS_SIN_TOKEN = [
    "Visitas no le puedo decir: sigue sin aparecer el token de Cloudflare. Ese es pendiente suyo, jefe.",
    "De visitas, ni idea: sin el token de Cloudflare estoy más ciego que usted sin lentes.",
    "Las visitas son un misterio, jefe. El token de Cloudflare sigue en su lista de 'luego lo hago'.",
    "No veo visitas porque alguien no ha puesto el token de Cloudflare. No digo nombres. Fue usted.",
]
VISITAS_ERROR = [
    "Las visitas no las pude leer esta vez; Cloudflare anda de payaso.",
    "Cloudflare no me contestó. Ha de andar en su hora de comida.",
]
VISITAS_OK = [
    "Lleva {v24} visitas en 24 horas y {v7} en la semana.",
    "Números: {v24} visitas hoy, {v7} en la semana.",
    "En 24 horas entraron {v24} personas, y {v7} en la semana. Ahí la llevamos.",
    "{v24} visitas en el día y {v7} en la semana. No es Netflix, pero tampoco es su blog de la secu.",
]
VISITAS_CERO = [
    "Cero visitas. Ni su jefa entró. A compartir, huevón.",
    "Cero. Nadita. Ni los bots, jefe. Hay que moverle.",
    "Cero visitas. El sitio está más solo que usted un viernes.",
]
PAGINA_TOP = ["La más vista fue {pagina}.", "La consentida del día: {pagina}.", "Lo que más pegó: {pagina}."]
FUENTES = ["Llegan sobre todo de {fuentes}.", "La gente viene de {fuentes}.", "El tráfico sale de {fuentes}."]

SITIO_MAL = [
    "Aguas: no abre {paginas}. Ya debería estar alguien encima.",
    "Ojo, jefe: {paginas} no abre. Échele un ojo o mande a alguien.",
]

PASE_INTRO = [
    "Ya los puse a chambear. Jalaron {n}.",
    "Pase de lista: {n} se pusieron a jalar.",
    "Sus compadres trabajaron: {n} reportaron chamba.",
    "Hoy jalaron {n}. Los demás, según ellos, en horario.",
    "{n} de sus empleados se reportaron. Milagro. Va lo más jugoso.",
    "Se pusieron las pilas {n}. Va lo que hicieron.",
]
PASE_NADIE = [
    "Los huevones no han reportado nada desde ayer. Andan en horario, según ellos.",
    "Nadie ha reportado desde ayer. O están chambeando calladitos, o están dormidos. Apuesto a lo segundo.",
    "Silencio total en la bitácora. Ni modo, hoy les toca descanso. A usted no.",
]
# Cómo se presenta cada línea. {hecho} viene en primera persona desde la bitácora ("revisé…").
PASE_LINEA = [
    "{nombre}: {hecho}",
    "Dice {nombre}: {hecho}",
    "{nombre} reporta: {hecho}",
    "{nombre}, en sus palabras: {hecho}",
    "De parte de {nombre}: {hecho}",
]
APODOS = {
    "Director": ["el Director", "el jefe de los huevones", "el Director, alias el que manda cuando usted no"],
    "Producto y diseño": ["Producto", "el diseñador mamón", "el de Producto, el que todo lo quiere bonito"],
    "SEO": ["SEO", "el que le ruega a Google", "el de SEO, el que le habla bonito a Google"],
    "Contenido": ["Contenido", "su influencer de planta", "el de Contenido, el tiktoker"],
    "Ley y datos": ["el licenciado", "el de Ley y datos", "el abogado de la casa"],
    "Monetización": ["el de la lana", "el que sueña con su primer peso", "el de Monetización, el interesado"],
    "Marca": ["Marca", "el vigilante del IMPI", "el de Marca, el celoso del nombre"],
}

TAREA = [
    "A usted le toca: {tarea}",
    "Su tarea, jefe: {tarea}",
    "Y usted, ¿qué? Pues: {tarea}",
    "Lo que sigue esperándolo a usted: {tarea}",
    "Pendiente del jefe, que ya huele a viejo: {tarea}",
]

SIGUE = [
    "Sigue {quien}, {cuando}.",
    "El próximo en chambear: {quien}, {cuando}.",
    "Al rato le toca a {quien}, {cuando}. Andan jalando.",
    "Turno de {quien}, {cuando}. Va con todo, dice.",
]

CIERRES = [
    "Es todo, jefe. Maneje con cuidado, que usted no tiene respaldo.",
    "Cambio y fuera.",
    "Eso es todo. Ahora sí, ponga su música.",
    "Fin del reporte. Aplausos opcionales.",
    "Listo, jefe. Ya puede seguir cantando en el tráfico.",
    "Ahí se lo dejo. Nos vemos a la otra subida.",
    "Y eso sería todo. Si alguien pregunta, sí tiene empleados. Digitales, pero empleados.",
    "Es cuanto. Ellos no piden aguinaldo; usted sí debería calcular el suyo.",
    "Fin. Ya ni el Director cree que hoy haga su pendiente, pero yo sí. Poquito.",
    "Ahí está el chisme. No se distraiga, que el semáforo ya cambió.",
    "Se acabó. Recuerde: en este negocio, el cuello de botella es usted. Con cariño.",
    "Eso es todo, jefe. Ojos en el camino, no en las visitas.",
    "Reporte terminado. Cero comerciales, cien por ciento sarcasmo.",
    "Hasta aquí. Si se le olvidó algo, se lo repito la próxima vez que se suba. Con gusto. Bueno, sin tanto.",
    "Y colorín colorado, sus pendientes no se han acabado.",
    "Ya, jefe. Siga manejando, que la chamba la hacen ellos.",
    "Listo. Tony Stark tenía a Jarvis; usted me tiene a mí. Ni modo, fue lo que alcanzó.",
    "Eso es todo. Cuide la camioneta, que el negocio todavía no paga otra.",
]
