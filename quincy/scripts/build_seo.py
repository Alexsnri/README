"""Genera las páginas de calculadoras para buscadores (quincy/<tema>/index.html).

Cada página tiene su calculadora, explicación con la ley, preguntas frecuentes con datos
estructurados y un enlace a la app. Correr después de cambiar textos:  python quincy/scripts/build_seo.py
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://alexsnri.github.io/README/quincy/"

FIELD = '<div class="field"><label for="{id}">{label}</label>{input}{hint}</div>'


def field(id_, label, input_, hint=""):
    return FIELD.format(id=id_, label=label, input=input_, hint=f"<small>{hint}</small>" if hint else "")


def num(id_, value, mn=0, mx=10000000):
    return f'<input type="number" inputmode="numeric" id="{id_}" value="{value}" min="{mn}" max="{mx}">'


PAGES = {
    "aguinaldo": {
        "title": "Calculadora de aguinaldo 2026: cuánto te toca y cuándo",
        "h1": "Calculadora de aguinaldo 2026",
        "desc": "Calcula tu aguinaldo 2026 según la Ley Federal del Trabajo: mínimo 15 días, proporcional si entraste este año, cuánto está libre de ISR y cuándo te lo pagan.",
        "intro": "Pon tu sueldo y tu fecha de ingreso. Te decimos cuánto te toca, cuánto está libre de ISR y cuántos días faltan para que te lo paguen.",
        "app": "derechos",
        "form": field("c-sal", "Sueldo mensual (antes de impuestos)", num("c-sal", 15000)) +
                field("c-start", "¿Cuándo entraste a trabajar ahí?", '<input type="date" id="c-start" value="2023-03-01">') +
                field("c-dias", "Días de aguinaldo de tu contrato", num("c-dias", 15, 15, 120), "La ley pide mínimo 15."),
        "out": '<p class="eyebrow">Tu aguinaldo</p><b class="calc-big mono" id="o-main">$0</b><p id="o-note"></p><p class="small mut" id="o-tax"></p>',
        "js": """
function run(){const sd=+$('c-sal').value/30, st=parse($('c-start').value)||new Date(2023,2,1), d=+$('c-dias').value||15;
const ag=FY.ley.aguinaldo({sd,start:st,at:today,dias:Math.max(15,d)}), left=FY.ley.diffDays(today,ag.deadline);
$('o-main').textContent=FY.fmt(ag.amount);
$('o-note').innerHTML=(ag.full?`Son ${d} días de salario.`:`Proporcional a ${ag.days} días trabajados este año.`)+(left>=0?` Te lo deben pagar a más tardar el <b>19 de diciembre</b>: faltan <b class="sun">${left} días</b>.`:` El de este año ya se debió pagar.`);
$('o-tax').textContent=`Libre de ISR hasta ${FY.fmt(ag.exento)} (30 UMA). ${ag.gravado>0?`Sobre ${FY.fmt(ag.gravado)} te retienen ISR.`:'No te deben retener ISR.'}`;}""",
        "body": """
<h2>Cómo se calcula el aguinaldo</h2>
<p>El artículo 87 de la Ley Federal del Trabajo dice que el aguinaldo es de <b>al menos 15 días de salario</b> y se paga <b>antes del 20 de diciembre</b>. Si no trabajaste el año completo, te toca la parte proporcional a los días que trabajaste.</p>
<p>La fórmula es: <b>salario diario × días de aguinaldo × días trabajados en el año ÷ 365</b>. El salario diario es tu sueldo mensual entre 30.</p>
<h2>Ejemplos con 15 días</h2>
<div class="tbl"><table><thead><tr><th>Sueldo mensual</th><th>Aguinaldo (año completo)</th></tr></thead><tbody>
<tr><td>Salario mínimo 2026 ($315.04 al día)</td><td class="mono">$4,726</td></tr>
<tr><td>$12,000</td><td class="mono">$6,000</td></tr>
<tr><td>$15,000</td><td class="mono">$7,500</td></tr>
<tr><td>$20,000</td><td class="mono">$10,000</td></tr>
<tr><td>$30,000</td><td class="mono">$15,000</td></tr>
</tbody></table></div>
<h2>¿Cuánto del aguinaldo paga ISR?</h2>
<p>El aguinaldo está libre de ISR hasta 30 veces la UMA diaria. Con la UMA de 2026 ($117.31) son <b>$3,519.30</b>. Lo que pase de esa cantidad sí paga ISR.</p>
<h2>¿Ya sabes cuánto te toca? Ponlo a rendir</h2>
<p>Antes de que se te vaya en las posadas, mira cuánto ganarías si lo guardas unos meses en CETES o en una cuenta con rendimiento, ya con ISR e inflación: <a href="../aguinaldo-a-rendir/">¿Dónde pongo mi aguinaldo a rendir?</a></p>""",
        "faq": [
            ("¿Cuánto me toca de aguinaldo en 2026?", "Mínimo 15 días de salario. Con un sueldo de $15,000 al mes son $7,500 si trabajaste todo el año."),
            ("¿Cuándo me tienen que pagar el aguinaldo?", "Antes del 20 de diciembre, según el artículo 87 de la Ley Federal del Trabajo."),
            ("Si entré a trabajar a mitad de año, ¿me toca aguinaldo?", "Sí, la parte proporcional a los días que trabajaste en el año."),
            ("¿El aguinaldo paga impuestos?", "Está exento de ISR hasta 30 UMA ($3,519.30 en 2026). Lo que pase de esa cantidad paga ISR."),
            ("Si renuncio o me despiden antes de diciembre, ¿me pagan el aguinaldo?", "Sí. Te toca la parte proporcional a los días que trabajaste en el año y te la deben pagar junto con tu finiquito."),
            ("¿Me toca aguinaldo si trabajo por honorarios?", "No, el aguinaldo es para quien tiene una relación de trabajo. Si en los hechos tienes jefe, horario y sueldo fijo, podrías tener derecho: pregunta gratis en PROFEDET."),
            ("¿Qué hago si no me pagan el aguinaldo?", "Pídelo por escrito a tu patrón. Si no te lo paga, PROFEDET te orienta y te representa gratis para reclamarlo."),
        ],
    },
    "finiquito": {
        "title": "Calculadora de finiquito y liquidación 2026",
        "h1": "Calculadora de finiquito y liquidación 2026",
        "desc": "Calcula tu finiquito si renuncias o tu liquidación si te despiden: aguinaldo y vacaciones proporcionales, prima vacacional, de antigüedad e indemnización 2026.",
        "intro": "Si renuncias te toca tu finiquito. Si te despiden sin causa justificada, además te toca una indemnización. Calcula el mínimo de ley.",
        "app": "derechos",
        "form": field("c-sal", "Sueldo mensual (antes de impuestos)", num("c-sal", 15000)) +
                field("c-start", "Fecha de ingreso", '<input type="date" id="c-start" value="2021-06-01">') +
                field("c-end", "Fecha de salida", '<input type="date" id="c-end">') +
                field("c-mot", "Motivo", '<select id="c-mot"><option value="despido">Me despidieron sin causa</option><option value="renuncia">Renuncié</option></select>') +
                field("c-zona", "Zona", '<select id="c-zona"><option value="general">Resto del país</option><option value="frontera">Zona Libre de la Frontera Norte</option></select>') +
                field("c-pend", "Vacaciones que no tomaste", num("c-pend", 0, 0, 365)),
        "out": '<p class="eyebrow" id="o-label">Tu liquidación</p><b class="calc-big mono" id="o-main">$0</b><div class="tbl"><table><tbody id="o-lines"></tbody></table></div><p class="small" id="o-note"></p>',
        "js": """
$('c-end').value=iso(today);
function run(){const sd=+$('c-sal').value/30, st=parse($('c-start').value)||new Date(2021,5,1); let en=parse($('c-end').value)||today; if(en<st)en=st;
const r=FY.ley.salida({sd,start:st,end:en,motivo:$('c-mot').value,zona:$('c-zona').value,vacPendientes:+$('c-pend').value||0});
$('o-label').textContent=r.despido?'Tu liquidación (mínimo de ley)':'Tu finiquito';
$('o-main').textContent=FY.fmt(r.total);
$('o-lines').innerHTML=r.lines.filter(l=>l.amount>0.5).map(l=>`<tr><td>${l.label}<small>${l.note}</small></td><td class="mono">${FY.fmt(l.amount)}</td></tr>`).join('');
$('o-note').innerHTML=r.despido?`En algunos casos (art. 50) aplican además <b>20 días por año</b>: ${FY.fmt(r.veinte)}. Tienes <b>2 meses</b> para reclamar; la asesoría de PROFEDET es gratuita.`:'La prima de antigüedad por renuncia solo aplica con 15 años o más.';}""",
        "body": """
<h2>Finiquito: lo que te toca siempre</h2>
<p>Sin importar por qué termina tu trabajo, te deben pagar: los días trabajados que no te han pagado, el <b>aguinaldo proporcional</b>, las <b>vacaciones</b> que no tomaste y su <b>prima vacacional</b> (mínimo 25%).</p>
<h2>Liquidación: si te despiden sin causa justificada</h2>
<ul>
<li><b>Indemnización de 3 meses</b> de salario integrado (art. 48 LFT).</li>
<li><b>Prima de antigüedad</b>: 12 días por cada año trabajado, con un salario tope de 2 salarios mínimos (art. 162). En 2026 el tope es de $630.08 al día ($881.74 en la frontera norte).</li>
<li>En algunos casos, <b>20 días por año</b> trabajado (art. 50).</li>
</ul>
<h2>No firmes una renuncia que no escribiste</h2>
<p>Si te despiden, tienes <b>2 meses</b> para reclamar (art. 518). La Procuraduría Federal de la Defensa del Trabajo (PROFEDET) te asesora gratis.</p>""",
        "faq": [
            ("¿Qué me toca si renuncio?", "Tu finiquito: días sin pagar, aguinaldo proporcional, vacaciones no tomadas y prima vacacional. La prima de antigüedad solo si llevas 15 años o más."),
            ("¿Qué me toca si me despiden sin causa?", "Tu finiquito más 3 meses de salario integrado y la prima de antigüedad de 12 días por año. En algunos casos, 20 días por año."),
            ("¿Cuánto tiempo tengo para reclamar un despido?", "2 meses desde el despido (artículo 518 de la Ley Federal del Trabajo)."),
            ("¿Quién me puede asesorar gratis?", "La Procuraduría Federal de la Defensa del Trabajo (PROFEDET)."),
        ],
    },
    "vacaciones": {
        "title": "Vacaciones dignas 2026: tabla de días y prima vacacional",
        "h1": "¿Cuántos días de vacaciones te tocan?",
        "desc": "Tabla de vacaciones dignas 2026 (art. 76 LFT): 12 días el primer año y 2 más cada año hasta 20; luego 2 más cada 5 años. Calcula tus días y tu prima vacacional.",
        "intro": "Desde 2023, con la reforma de \"vacaciones dignas\", te tocan al menos 12 días al cumplir tu primer año. Calcula los tuyos y tu prima vacacional.",
        "app": "derechos",
        "form": field("c-sal", "Sueldo mensual", num("c-sal", 15000)) +
                field("c-start", "Fecha de ingreso", '<input type="date" id="c-start" value="2022-02-15">') +
                field("c-prima", "Prima vacacional %", num("c-prima", 25, 25, 200), "La ley pide mínimo 25%."),
        "out": '<p class="eyebrow">Tus vacaciones</p><b class="calc-big mono" id="o-main">0 días</b><p id="o-note"></p><p class="small mut" id="o-next"></p>',
        "js": """
function run(){const sd=+$('c-sal').value/30, st=parse($('c-start').value)||new Date(2022,1,15), pr=(+$('c-prima').value||25)/100;
const v=FY.ley.vacaciones({sd,start:st,at:today,prima:pr});
$('o-main').textContent=v.years>=1?`${v.days} días`:'Aún no';
$('o-note').innerHTML=v.years>=1?`Llevas ${v.years} ${v.years===1?'año':'años'}. Tu prima vacacional es de <b class="sun">${FY.fmt(v.prima)}</b>.`:'Al cumplir tu primer año te tocan 12 días.';
$('o-next').textContent=`En tu próximo aniversario (${v.nextDate.toLocaleDateString('es-MX',{day:'numeric',month:'long',year:'numeric'})}) te tocarán ${v.nextDays} días.`;}""",
        "body": """
<h2>Tabla de vacaciones dignas</h2>
<div class="tbl"><table><thead><tr><th>Años trabajados</th><th>Días de vacaciones</th></tr></thead><tbody>
<tr><td>1</td><td class="mono">12</td></tr><tr><td>2</td><td class="mono">14</td></tr><tr><td>3</td><td class="mono">16</td></tr>
<tr><td>4</td><td class="mono">18</td></tr><tr><td>5</td><td class="mono">20</td></tr><tr><td>6 a 10</td><td class="mono">22</td></tr>
<tr><td>11 a 15</td><td class="mono">24</td></tr><tr><td>16 a 20</td><td class="mono">26</td></tr><tr><td>21 a 25</td><td class="mono">28</td></tr>
<tr><td>26 a 30</td><td class="mono">30</td></tr><tr><td>31 a 35</td><td class="mono">32</td></tr>
</tbody></table></div>
<h2>Prima vacacional</h2>
<p>Además del sueldo de tus días de vacaciones, te toca una prima de <b>al menos 25%</b> de ese sueldo (art. 80). Las vacaciones no se pueden cambiar por dinero mientras sigas trabajando ahí (art. 79).</p>""",
        "faq": [
            ("¿Cuántos días de vacaciones me tocan con un año trabajado?", "12 días, desde la reforma de vacaciones dignas que entró en vigor el 1 de enero de 2023."),
            ("¿Cuánto es la prima vacacional?", "Mínimo 25% del salario de tus días de vacaciones (artículo 80 de la LFT)."),
            ("¿Me pueden pagar las vacaciones para no tomarlas?", "No mientras sigas en el trabajo (artículo 79). Si te vas, te las pagan en tu finiquito."),
        ],
    },
    "ptu": {
        "title": "PTU 2027: cuánto te toca de reparto de utilidades",
        "h1": "Reparto de utilidades (PTU)",
        "desc": "Calcula el tope de tu PTU: 3 meses de salario o el promedio de tus últimos 3 años. Fecha límite: 30 de mayo (empresas) y 29 de junio (personas físicas).",
        "intro": "Si tu empresa tuvo utilidades, reparte el 10% entre sus trabajadores. Calcula el máximo que te pueden dar y cuándo te lo deben pagar.",
        "app": "derechos",
        "form": field("c-sal", "Sueldo mensual", num("c-sal", 15000)) +
                field("c-prom", "Promedio de PTU de tus últimos 3 años (opcional)", num("c-prom", 0)),
        "out": '<p class="eyebrow">Máximo de tu PTU</p><b class="calc-big mono" id="o-main">$0</b><p id="o-note"></p>',
        "js": """
function run(){const sd=+$('c-sal').value/30, p=FY.ley.ptu({sd,at:today,promedio:+$('c-prom').value||0});
$('o-main').textContent=FY.fmt(p.tope);
$('o-note').innerHTML=`3 meses de salario son ${FY.fmt(p.tresMeses)}. Fecha límite: <b>${p.empresas.toLocaleDateString('es-MX',{day:'numeric',month:'long',year:'numeric'})}</b> si tu patrón es empresa y <b>${p.personas.toLocaleDateString('es-MX',{day:'numeric',month:'long',year:'numeric'})}</b> si es persona física. Libre de ISR hasta ${FY.fmt(p.exento)} (15 UMA).`;}""",
        "body": """
<h2>Cómo se reparte la PTU</h2>
<p>Las empresas reparten el <b>10%</b> de su utilidad fiscal. La mitad se reparte según los días que trabajó cada persona en el año y la otra mitad según su salario.</p>
<h2>El tope desde 2021</h2>
<p>Lo que recibes no puede pasar de <b>3 meses de tu salario</b> o del <b>promedio de lo que recibiste en los últimos 3 años</b>, lo que te convenga más (art. 127, fracción VIII).</p>""",
        "faq": [
            ("¿Cuándo se paga la PTU?", "A más tardar el 30 de mayo si tu patrón es empresa, y el 29 de junio si es persona física."),
            ("¿Cuál es el tope de la PTU?", "3 meses de salario o el promedio de lo recibido en los últimos 3 años, lo que más le convenga al trabajador."),
            ("¿A todos les toca PTU?", "Solo si la empresa tuvo utilidades. Hay excepciones, como empresas de nueva creación en su primer año."),
        ],
    },
    "tanda": {
        "title": "Calculadora de tandas: qué número te conviene",
        "h1": "¿Qué número de la tanda te conviene?",
        "desc": "Calcula cuánto gana o pierde cada número de una tanda comparado con invertir en CETES. Organiza tu tanda con ruleta, calendario y recordatorios para WhatsApp.",
        "intro": "En una tanda, los primeros números reciben un préstamo sin intereses y los últimos ahorran sin rendimiento. Mira cuánto vale cada turno.",
        "app": "tanda",
        "form": field("c-n", "Personas", num("c-n", 10, 2, 30)) +
                field("c-a", "Cada quien pone", num("c-a", 1000, 1)) +
                field("c-f", "¿Cada cuándo?", '<select id="c-f"><option value="24">Cada quincena</option><option value="52">Cada semana</option><option value="12">Cada mes</option></select>'),
        "out": '<p class="eyebrow">Cada turno contra CETES</p><div class="tbl"><table><tbody id="o-lines"></tbody></table></div><p class="small" id="o-note"></p>',
        "js": """
function run(){const n=Math.max(2,Math.min(30,+$('c-n').value||10)), A=+$('c-a').value||1000, r=Math.pow(1+FY.RATES.cetes/100,1/(+$('c-f').value))-1;
let paid=0; for(let j=1;j<=n;j++) paid+=A*Math.pow(1+r,n-j);
const rows=[]; for(let k=1;k<=n;k++){const v=n*A*Math.pow(1+r,n-k)-paid; rows.push(`<tr><td>Turno ${k}</td><td class="mono ${v>=0?'ok-t':'bad-t'}">${v>=0?'+':'−'}${FY.fmt(Math.abs(v))}</td></tr>`);}
$('o-lines').innerHTML=rows.join('');
$('o-note').textContent=`Cada turno recibe ${FY.fmt(n*A)}. Con CETES al ${FY.RATES.cetes.toFixed(2)}% anual.`;}""",
        "body": """
<h2>Las tandas son de las formas de ahorro más usadas en México</h2>
<p>Alrededor de <b>1 de cada 5 adultos</b> participa en tandas, según la Encuesta Nacional de Inclusión Financiera 2024. Funcionan por confianza: cada quien pone lo mismo y cada turno alguien se lleva todo.</p>
<h2>Organízala sin pleitos</h2>
<p>En Quincy sorteas los turnos con una ruleta, mandas el calendario al grupo de WhatsApp con un enlace y cada quien ve cuándo le toca y pone sus recordatorios de pago.</p>""",
        "faq": [
            ("¿Qué número de la tanda conviene más?", "Los primeros: reciben el dinero antes, como un préstamo sin intereses. Los últimos ahorran sin rendimiento."),
            ("¿Cuánto pierde el último número?", "Lo que habría ganado invirtiendo cada aportación. En una tanda de 10 personas con $1,000 por quincena, unos $114 con CETES al 6.23%."),
            ("¿La tanda es segura?", "Depende de la confianza en el grupo: si alguien deja de pagar, nadie lo cubre."),
        ],
    },
    "quincena": {
        "title": "¿Cuánto puedo gastar al día para llegar a la quincena?",
        "h1": "¿Cuánto puedes gastar hoy?",
        "desc": "Calcula tu límite de gasto diario para llegar a tu siguiente quincena: lo que te llega, menos tus pagos fijos y tu ahorro, entre los días que faltan.",
        "intro": "Un solo número: lo que puedes gastar hoy para llegar completo a tu siguiente pago.",
        "app": "hoy",
        "form": field("c-in", "Lo que te llega cada quincena", num("c-in", 8000)) +
                field("c-fix", "Pagos fijos de la quincena", num("c-fix", 3500), "Renta, servicios, deudas…") +
                field("c-sav", "Lo que apartas para ahorrar", num("c-sav", 500)) +
                field("c-spent", "Lo que ya gastaste esta quincena", num("c-spent", 0)),
        "out": '<p class="eyebrow">Hoy puedes gastar</p><b class="calc-big mono ok-t" id="o-main">$0</b><p id="o-note"></p>',
        "js": """
function run(){const d=today.getDate(), last=new Date(today.getFullYear(),today.getMonth()+1,0).getDate();
const next=d===last?new Date(today.getFullYear(),today.getMonth()+1,15):d>=15?new Date(today.getFullYear(),today.getMonth(),last):new Date(today.getFullYear(),today.getMonth(),15);
const n=Math.max(1,FY.ley.diffDays(today,next)), left=(+$('c-in').value||0)-(+$('c-fix').value||0)-(+$('c-sav').value||0)-(+$('c-spent').value||0);
$('o-main').textContent=FY.fmt(Math.max(0,left/n));
$('o-note').textContent=left>0?`Faltan ${n} ${n===1?'día':'días'} para tu quincena (${next.toLocaleDateString('es-MX',{day:'numeric',month:'long'})}). Si hoy gastas menos, mañana tienes más.`:'Tus pagos fijos y gastos ya se comieron tu quincena: revisa tus pagos fijos.';}""",
        "body": """
<h2>Por qué un número al día funciona</h2>
<p>Los presupuestos con muchas categorías se abandonan. Un límite diario es fácil de recordar: si hoy gastas menos, lo que sobra se reparte en los días que faltan.</p>
<h2>Págate primero</h2>
<p>Aparta tu ahorro el día que te pagan, antes de gastar. Así tu límite diario ya lo toma en cuenta.</p>""",
        "faq": [
            ("¿Cómo calculo cuánto puedo gastar al día?", "Resta a lo que te llega tus pagos fijos, tu ahorro y lo que ya gastaste, y divídelo entre los días que faltan para tu siguiente pago."),
            ("¿Qué días se paga la quincena?", "Normalmente el 15 y el último día de cada mes."),
            ("¿Necesito registrarme?", "No. Quincy funciona sin registro y tus datos se quedan en tu teléfono."),
        ],
    },
    "aguinaldo-a-rendir": {
        "title": "¿Dónde pongo mi aguinaldo a rendir? Comparativa 2026",
        "h1": "¿Dónde pongo mi aguinaldo a rendir?",
        "desc": "Calcula cuánto te daría tu aguinaldo en CETES o en una cuenta con rendimiento, después de ISR e inflación, y compara qué tan protegido está tu dinero.",
        "eyebrow": "Calculadora gratuita · CETES, bancos y SOFIPOs · 2026",
        "intro": "Antes de que se te vaya en las posadas: pon tu aguinaldo, la tasa que te ofrecen y el plazo. Te decimos cuánto ganas de verdad, ya con impuestos e inflación.",
        "app": "futuro",
        "form": field("c-monto", "¿Cuánto vas a poner a rendir?", num("c-monto", 7500)) +
                field("c-tasa", "Tasa anual que te ofrecen (%)", '<input type="number" inputmode="decimal" id="c-tasa" value="6.23" min="0" max="30" step="0.01">', 'Viene puesta la de CETES a 28 días. Si una app te ofrece otra, ponla aquí.') +
                field("c-meses", "¿Cuánto tiempo lo vas a dejar?", '<select id="c-meses"><option value="1">1 mes</option><option value="3">3 meses</option><option value="6">6 meses</option><option value="12" selected>1 año</option><option value="24">2 años</option></select>'),
        "out": '<p class="eyebrow">Al final tendrías</p><b class="calc-big mono ok-t" id="o-main">$0</b><p id="o-note"></p><p class="small mut" id="o-real"></p><p class="small mut" id="o-src"></p><div id="ref-slot" class="related" hidden></div>',
        "js": """
const tasa=$('c-tasa'); tasa.addEventListener('input',()=>{tasa.dataset.touched='1';});
let inf=FY.RATES.inflacion;
function run(){const m=Math.max(0,+$('c-monto').value||0), t=Math.max(0,+tasa.value||0)/100, n=+$('c-meses').value||12, y=n/12;
const bruto=m*(Math.pow(1+t/12,n)-1), isr=m*0.009*y, neto=Math.max(0,bruto-isr), pierde=m*(1-1/Math.pow(1+inf/100,y)), real=(m+neto)/Math.pow(1+inf/100,y)-m;
$('o-main').textContent=FY.fmt(m+neto);
$('o-note').innerHTML=`Ganas <b>${FY.fmt(neto)}</b> en ${n===12?'un año':n===24?'dos años':n===1?'un mes':n+' meses'}, ya con la retención de ISR (unos ${FY.fmt(isr)}).`;
$('o-real').textContent=(real>=0?`Contra la inflación (${inf.toFixed(2)}% al año) le ganas ${FY.fmt(real)} en pesos de hoy.`:`Ojo: con esta tasa la inflación (${inf.toFixed(2)}% al año) te gana por ${FY.fmt(-real)} en pesos de hoy.`)+` Bajo el colchón, tus ${FY.fmt(m)} valdrían ${FY.fmt(m-pierde)} de hoy.`;}
fetch('../data/rates.json',{cache:'no-cache'}).then((r)=>r.ok?r.json():null).then((d)=>{if(!d||typeof d.cetes28!=='number')return;
if(!tasa.dataset.touched)tasa.value=d.cetes28; if(typeof d.inflacion==='number')inf=d.inflacion;
$('o-src').textContent=`CETES 28 días: ${d.cetes28.toFixed(2)}% · ${d.cetes28_fuente||'Banxico'}. Inflación: ${d.inflacion_fuente||'INEGI'}.`; run();}).catch(()=>{});
FY.referidos($('ref-slot'));""",
        "body": """
<h2>Primero lo primero</h2>
<ul>
<li><b>¿Debes en tu tarjeta?</b> Págala antes de invertir. Ninguna inversión te da lo que te cobra una tarjeta de crédito de intereses.</li>
<li><b>¿Tienes un colchón para emergencias?</b> Aparta primero el equivalente a uno a tres meses de gastos donde lo puedas sacar el mismo día.</li>
<li><b>Lo que sobre, ponlo a rendir.</b> Dejarlo en una cuenta que no paga nada es perder poco a poco contra la inflación.</li>
</ul>
<h2>Las opciones, comparadas sin letra chiquita</h2>
<p>Ordenamos por lo que más te conviene a ti: qué tan protegido está tu dinero, qué tan fácil lo sacas y cuánto rinde. Quincy no cobra comisión de ninguna de estas opciones.</p>
<style>.opts{display:grid;gap:10px;margin-top:12px}.opts .card{display:grid;gap:6px}.opts h3{margin:0;font-size:1.02rem;color:var(--sun)}.opts p{margin:0;font-size:.94rem}</style>
<div class="opts">
<div class="card"><h3>1. CETES en cetesdirecto</h3><p><b>Quién responde:</b> Es deuda del Gobierno de México</p><p><b>Cuándo lo sacas:</b> Al vencer el plazo (28 días o más). El fondo BONDDIA de la misma plataforma se retira cualquier día hábil.</p><p><b>Ojo con:</b> Desde $100, sin comisiones. La tasa cambia en cada subasta semanal.</p></div>
<div class="card"><h3>2. Banco (cuenta o apartado con rendimiento)</h3><p><b>Quién responde:</b> Seguro del IPAB: hasta 400 mil UDIS por persona y por banco (unos 3.5 millones de pesos con la UDI de octubre de 2026)</p><p><b>Cuándo lo sacas:</b> Casi siempre al momento.</p><p><b>Ojo con:</b> Las tasas más altas suelen tener tope de saldo, condiciones (usar la tarjeta, recibir tu nómina) y fecha de fin.</p></div>
<div class="card"><h3>3. SOFIPO (sociedad financiera popular)</h3><p><b>Quién responde:</b> Fondo de Protección: hasta 25 mil UDIS por persona (unos 220 mil pesos con la UDI de octubre de 2026)</p><p><b>Cuándo lo sacas:</b> Al momento o al vencer el plazo.</p><p><b>Ojo con:</b> Pueden pagar más, pero la protección es mucho menor. Revisa que esté autorizada por la CNBV.</p></div>
<div class="card"><h3>4. Billetera digital (IFPE)</h3><p><b>Quién responde:</b> Ningún seguro de depósitos</p><p><b>Cuándo lo sacas:</b> Al momento.</p><p><b>Ojo con:</b> Cómoda para pagar, pero tu saldo no tiene el seguro del IPAB.</p></div>
<div class="card"><h3>5. Colchón o cuenta sin rendimiento</h3><p><b>Quién responde:</b> Nadie</p><p><b>Cuándo lo sacas:</b> Al momento.</p><p><b>Ojo con:</b> La inflación le quita valor cada mes.</p></div>
</div>
<h2>Cómo revisar una oferta antes de meter tu dinero</h2>
<ul>
<li><b>Que esté regulada.</b> Búscala en el registro de instituciones financieras de la <a href="https://www.gob.mx/condusef" target="_blank" rel="noopener">CONDUSEF</a> y en el padrón de la <a href="https://www.gob.mx/cnbv" target="_blank" rel="noopener">CNBV</a>. Si no aparece, no es opción.</li>
<li><b>Mira la GAT real</b>, no solo la tasa grande del anuncio. La GAT real ya descuenta la inflación estimada.</li>
<li><b>Lee el tope y las condiciones.</b> Un "hasta 15%" puede aplicar solo a los primeros miles de pesos o solo si cumples algo cada mes.</li>
<li><b>No pongas todo en un solo lugar</b> si pasas del tope de protección.</li>
<li><b>Rendimientos pasados no garantizan los futuros.</b> Las tasas cambian: la que ves hoy puede bajar el mes que entra.</li>
</ul>
<h2>¿Y los impuestos?</h2>
<p>En 2026 los bancos, SOFIPOs y cetesdirecto te retienen ISR de <b>0.90% al año sobre el capital</b> que tienes invertido, según el artículo 24 de la Ley de Ingresos de la Federación 2026 (DOF, 7 de noviembre de 2025). La calculadora ya lo descuenta. Si tus ingresos por intereses son pocos, esa retención puede ser todo el impuesto que pagas por ellos.</p>
<p>Ojo: para 2027 Hacienda propuso bajarla a 0.68%. Todavía no es ley; cuando se publique en el DOF actualizamos la calculadora.</p>""",
        "faq": [
            ("¿Dónde pongo mi aguinaldo a rendir?", "Primero paga deudas caras y aparta un fondo de emergencia. Lo que sobre puede ir a CETES en cetesdirecto (desde $100, deuda del gobierno) o a una cuenta con rendimiento de un banco protegido por el IPAB. Revisa siempre tope, condiciones y que la institución esté regulada."),
            ("¿Cuánto me da CETES por mi aguinaldo?", "Depende de la tasa de la subasta de esa semana. Con la calculadora de esta página pones tu aguinaldo y el plazo, y ves cuánto ganas ya con la retención de ISR y la inflación."),
            ("¿Mi dinero está protegido en una SOFIPO?", "Sí, pero menos que en un banco: el Fondo de Protección cubre hasta 25 mil UDIS por persona. En un banco, el IPAB cubre hasta 400 mil UDIS por persona y por banco."),
            ("¿Qué es la GAT?", "La Ganancia Anual Total. La GAT nominal es lo que rinde tu dinero en un año; la GAT real le resta la inflación estimada. Compara siempre la GAT real."),
            ("¿Me cobran impuestos por los intereses?", "Sí. En 2026 te retienen ISR de 0.90% anual sobre el capital invertido, según la Ley de Ingresos de la Federación 2026."),
        ],
        "fuente": 'Herramienta educativa, no es asesoría financiera ni una recomendación personalizada. Rendimientos pasados no garantizan rendimientos futuros. Fuentes: tasa de CETES de las subastas de <a href="https://www.banxico.org.mx" target="_blank" rel="noopener">Banxico</a>, inflación del <a href="https://www.inegi.org.mx" target="_blank" rel="noopener">INEGI</a>, seguro de depósitos del <a href="https://www.gob.mx/ipab" target="_blank" rel="noopener">IPAB</a>, <a href="https://www.fondodeproteccion.mx/" target="_blank" rel="noopener">Fondo de Protección de SOFIPOs</a> y Ley de Ingresos de la Federación 2026, art. 24 (DOF, 7 de noviembre de 2025).',
    },
}

RELATED = [("aguinaldo", "Aguinaldo 2026"), ("aguinaldo-a-rendir", "Pon tu aguinaldo a rendir"), ("finiquito", "Finiquito y liquidación"), ("vacaciones", "Vacaciones dignas"), ("ptu", "PTU"), ("tanda", "Tandas"), ("quincena", "Cuánto gastar al día")]

EYEBROW = "Calculadora gratuita · Ley Federal del Trabajo · 2026"
FUENTE = 'Herramienta educativa con el mínimo de ley y valores de 2026 (salario mínimo de CONASAMI y UMA de INEGI). No es asesoría legal ni fiscal. Fuente: <a href="https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf" target="_blank" rel="noopener">Ley Federal del Trabajo</a>.'

# Compartir en 1 toque (Producto): qué manda cada calculadora por WhatsApp y qué dice su tarjeta para historias.
# Cada valor es una función JS que corre dentro de la página (tiene $, today y parse) y devuelve
# { wa: texto sin enlace, card: {kicker, big, line, sub}, name, wrapped?: () => [tarjetas] }.
SHARE = {
    "aguinaldo": """() => { const sd=+$('c-sal').value/30, st=parse($('c-start').value)||new Date(2023,2,1), d=Math.max(15,+$('c-dias').value||15);
const ag=FY.ley.aguinaldo({sd,start:st,at:today,dias:d}), left=FY.ley.diffDays(today,ag.deadline);
return {wa:`Ya sé cuánto me toca de aguinaldo${left>=0?` y faltan ${left} días para cobrarlo`:''}. ¿Y a ti cuánto te toca? Calcúlalo en 10 segundos:`,
card:{kicker:`Mi aguinaldo ${ag.deadline.getFullYear()}`,big:FY.fmt(ag.amount),line:left>=0?`y faltan ${left} días para cobrarlo`:'ya me tocó',sub:'Por ley, a más tardar el 19 de diciembre.'},
name:'mi-aguinaldo',wrapped:()=>FY.compartir.aguinaldoWrapped(ag,left)}; }""",
    "finiquito": """() => ({wa:'Calculé lo mínimo que me toca por ley si dejo mi trabajo. Calcula lo tuyo:',
card:{kicker:$('o-label').textContent,big:$('o-main').textContent,line:'lo mínimo que me toca por ley',sub:'Ley Federal del Trabajo, valores 2026.'},name:'mi-finiquito'})""",
    "vacaciones": """() => { const v=$('o-main').textContent, ok=/días/.test(v);
return {wa:ok?`Me tocan ${v} de vacaciones por ley. ¿Cuántos te tocan a ti?`:'Ya sé cuántos días de vacaciones me tocan por ley. ¿Y a ti?',
card:{kicker:'Mis vacaciones',big:ok?v:'12 días',line:ok?'de vacaciones pagadas por ley':'al cumplir mi primer año',sub:'Vacaciones dignas, artículo 76 de la LFT.'},name:'mis-vacaciones'}; }""",
    "ptu": """() => ({wa:'Ya sé hasta cuánto me puede tocar de reparto de utilidades. ¿Y a ti?',
card:{kicker:'Mi PTU, hasta',big:$('o-main').textContent,line:'si mi empresa tuvo utilidades',sub:'Tope: 3 meses de salario o el promedio de 3 años.'},name:'mi-ptu'})""",
    "tanda": """() => { const c=document.querySelector('#o-lines td.mono');
return {wa:'¿Qué número de la tanda te conviene? Mira cuánto gana o pierde cada turno contra CETES:',
card:{kicker:'En la tanda, el turno 1',big:c?c.textContent:'+$0',line:'le gana a invertir en CETES',sub:'Los primeros reciben un préstamo sin intereses.',tone:'tide'},name:'mi-tanda'}; }""",
    "quincena": """() => ({wa:'Ya sé cuánto puedo gastar hoy para llegar a la quincena. ¿Y tú?',
card:{kicker:'Hoy puedo gastar',big:$('o-main').textContent,line:'y llego completo a la quincena',sub:'Si hoy gasto menos, mañana tengo más.',tone:'tide'},name:'mi-limite-de-hoy'})""",
    "aguinaldo-a-rendir": """() => ({wa:'Calculé cuánto me daría mi aguinaldo si lo pongo a rendir, ya con ISR e inflación. Haz tu cuenta:',
card:{kicker:'Si pongo mi aguinaldo a rendir',big:$('o-main').textContent,line:'tendría al final del plazo',sub:'Ya con la retención de ISR.',tone:'tide'},name:'mi-aguinaldo-a-rendir'})""",
}

# Recordatorio en el calendario que ofrece cada página (las demás: la próxima quincena).
REMIND = {
    "aguinaldo": ("Fecha límite del aguinaldo", "() => { const y=today.getMonth()===11&&today.getDate()>19?today.getFullYear()+1:today.getFullYear(); return {title:'Fecha límite de mi aguinaldo',date:new Date(y,11,19),alarmDays:3,name:'aguinaldo'}; }"),
    "aguinaldo-a-rendir": ("Fecha límite del aguinaldo", "() => { const y=today.getMonth()===11&&today.getDate()>19?today.getFullYear()+1:today.getFullYear(); return {title:'Me pagan el aguinaldo: ponerlo a rendir',date:new Date(y,11,19),alarmDays:1,name:'aguinaldo'}; }"),
    "ptu": ("Fecha límite de la PTU", "() => { const p=FY.ley.ptu({sd:1,at:today}); return {title:'Fecha límite de la PTU',date:p.empresas,alarmDays:3,name:'ptu'}; }"),
}
REMIND_DEFAULT = ("Mi próxima quincena", "() => { const d=today.getDate(), last=new Date(today.getFullYear(),today.getMonth()+1,0).getDate(); const n=d===last?new Date(today.getFullYear(),today.getMonth()+1,15):d>=15?new Date(today.getFullYear(),today.getMonth(),last):new Date(today.getFullYear(),today.getMonth(),15); return {title:'Hoy es quincena',date:n,alarmDays:0,name:'quincena'}; }")

# Arriba de la calculadora: cuenta regresiva en vivo en las páginas de temporada.
HERO_EXTRA = {
    "aguinaldo": "() => { const y=today.getMonth()===11&&today.getDate()>19?today.getFullYear()+1:today.getFullYear(); FY.compartir.countdown($('cd'), new Date(y,11,20), 'Faltan para la fecha límite, 19 de diciembre'); }",
}

TEMPLATE = """<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} | Quincy</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#07121a">
<link rel="canonical" href="{url}">
<link rel="icon" href="../img/icon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_MX">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:site_name" content="Quincy">
<meta property="og:image" content="{site}img/og/{slug}.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{h1}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{ld}</script>
<link rel="preload" href="../fonts/unbounded.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../fonts/figtree.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../css/app.css">
<style>
/* Layout: a calculator page for search. The calculator sits beside the explanation on wide screens and on top on phones. */
body{{padding-bottom:0}}
body{{background:radial-gradient(90% 60% at 85% -10%,#173c4f 0,rgba(7,18,26,0) 60%),var(--night) no-repeat}}
.calc-hero{{padding-block:34px 6px;display:grid;gap:12px;max-width:52rem}}
.calc-hero h1{{font-size:clamp(2rem,5.6vw,3.6rem);line-height:1;font-weight:800;letter-spacing:-.04em}}
.calc-hero > p{{color:var(--mut);font-size:1.08rem;max-width:44rem}}
.calc{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;align-items:start;margin-top:18px}}
@media (max-width:820px){{.calc{{grid-template-columns:minmax(0,1fr)}}}}
.calc .card{{border-radius:22px;padding:22px}}
.calc .out{{position:sticky;top:76px;background:linear-gradient(140deg,rgba(255,181,71,.12),rgba(90,214,200,.05) 55%),var(--deep);border-color:rgba(255,181,71,.4);box-shadow:0 30px 70px -40px rgba(255,181,71,.45)}}
@media (max-width:820px){{.calc .out{{position:static}}}}
.calc input[type=number],.calc input[type=date],.calc select{{min-height:48px;border-radius:14px}}
.calc-big{{font:800 clamp(2.4rem,7vw,3.6rem)/1 var(--f-display);color:var(--sun);letter-spacing:-.03em}}
.share-slot{{margin-top:6px}}
.cd{{min-height:96px}}
/* Celular: lo de arriba más compacto para que el campo y el resultado se vean pronto; barra fija con el resultado mientras no está a la vista. */
.peek{{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:30;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 16px;border-radius:18px;background:rgba(11,27,37,.96);border:1px solid rgba(255,181,71,.55);box-shadow:0 18px 40px -12px rgba(0,0,0,.8);color:var(--fg);text-decoration:none;min-height:56px}}
.peek span{{font:600 .7rem/1.2 var(--f-data);letter-spacing:.1em;text-transform:uppercase;color:var(--mut)}}
.peek b{{font:800 1.35rem/1 var(--f-display);color:var(--sun);margin-left:auto}}
.peek i{{font-style:normal;color:var(--tide);font-weight:700;font-size:.9rem}}
@media (min-width:821px){{.peek{{display:none}}}}
@media (max-width:640px){{
  .calc-hero{{padding-block:16px 2px;gap:8px}}
  .calc-hero .eyebrow{{font-size:.62rem;letter-spacing:.08em}}
  .calc-hero > p{{font-size:.98rem;line-height:1.45}}
  .cd{{min-height:74px}}
  .cd-grid{{margin-top:4px}}
  .cd-grid span{{padding:6px 2px 5px}}
  .cd-grid b{{font-size:1.15rem}}
  .calc{{margin-top:12px}}
  .calc .card{{padding:16px}}
  .ref-hello{{padding:8px 8px 8px 12px;gap:8px}}
  .ref-hello p{{font-size:.9rem;flex-basis:180px}}
  .ref-hello .ref-x{{width:40px;height:40px}}
}}
.follow{{margin-top:16px;padding:22px;border-radius:var(--r);border:1px solid var(--line-hi);background:var(--deep);display:grid;gap:12px}}
.follow h2{{margin:0;font-size:1.2rem}}
.calc-big.ok-t{{color:var(--ok)}}
.article{{max-width:46rem;margin-top:30px}}
.article h2{{font-size:1.3rem;margin-top:30px}}
.article p,.article ul{{color:var(--mut);margin:12px 0 0}}
.article p b,.article li b{{color:var(--fg)}}
.article .tbl{{margin-top:12px}}
.article th{{text-align:left;font:600 .72rem/1.2 var(--f-data);color:var(--mut);letter-spacing:.08em;text-transform:uppercase;padding:6px 0;border-bottom:1px solid var(--line-hi)}}
.related{{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}}
.cta-band{{margin-top:36px;padding:22px;border-radius:var(--r);border:1px solid var(--sun);background:linear-gradient(120deg,rgba(255,181,71,.16),rgba(90,214,200,.08));display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap}}
.cta-band h2{{margin:0;font-size:1.2rem}}
</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="logo" href="../"><i></i><span>quincy<b>.</b></span></a>
    <a class="btn btn-sun btn-sm" style="margin-left:auto" href="../app.html#{app}">Abrir la app</a>
  </div>
</header>
<main class="wrap">
  <section class="calc-hero">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p>{intro}</p>
    {hero_extra}
  </section>
  <div class="calc">
    <form class="card" onsubmit="return false" aria-label="Tus datos">{form}</form>
    <div class="card out" id="resultado" aria-live="polite">{out}<div id="share" class="share-slot"></div></div>
  </div>
  <article class="article">
    {body}
    <h2>Preguntas frecuentes</h2>
    {faq_html}
    <div class="cta-band">
      <div><h2>Todo esto y más, todos los días</h2><p class="mut" style="margin:6px 0 0">Tu límite de gasto diario, tus derechos, tus tandas y tu futuro. Gratis y sin registro.</p></div>
      <a class="btn btn-sun" href="../app.html#{app}">Abrir Quincy</a>
    </div>
    <div class="follow" id="avisame">
      <div><h2>Que no se te pase</h2><p class="mut" style="margin:6px 0 0">Ponlo en tu calendario y síguenos: cada semana, dinero claro en 30 segundos.</p></div>
      <div class="row"><button class="btn btn-ghost btn-sm" type="button" id="rem">{remind_label}</button><a class="btn btn-ghost btn-sm" href="https://www.instagram.com/quincy_app/" target="_blank" rel="noopener">Instagram @quincy_app</a><a class="btn btn-ghost btn-sm" href="https://www.tiktok.com/@quincyapp" target="_blank" rel="noopener">TikTok @quincyapp</a><a class="btn btn-ghost btn-sm" id="wa-canal" href="#" target="_blank" rel="noopener" hidden>Canal de WhatsApp</a></div>
    </div>
    <h2>Otras calculadoras</h2>
    <nav class="related" aria-label="Otras calculadoras">{related}</nav>
    <p class="small mut" style="margin-top:24px">{fuente}</p>
  </article>
</main>
<footer><div class="wrap"><p><b>Quincy</b> · Lo que te toca, cuándo te toca y cuánto te queda.</p></div></footer>
<script src="../js/core.js"></script>
<script src="../js/ley.js"></script>
<script src="../js/compartir.js"></script>
<script>
(() => {{
const $ = (id) => document.getElementById(id);
const today = (() => {{ const t = new Date(); return new Date(t.getFullYear(), t.getMonth(), t.getDate(), 12); }})();
const parse = (s) => {{ const m = /^(\\d{{4}})-(\\d{{2}})-(\\d{{2}})$/.exec(s || ""); return m ? new Date(+m[1], +m[2] - 1, +m[3], 12) : null; }};
const iso = (d) => `${{d.getFullYear()}}-${{String(d.getMonth() + 1).padStart(2, "0")}}-${{String(d.getDate()).padStart(2, "0")}}`;
{js}
document.querySelectorAll("input,select").forEach((el) => el.addEventListener("input", run));
run();
FY.compartir.bar($("share"), {share});
FY.compartir.welcome(document.querySelector(".calc-hero"), ".calc input, .calc select");
// Barra fija con el resultado en vivo mientras la tarjeta del resultado no se ve (celular).
if ($("o-main") && "IntersectionObserver" in window) {{
  const out = $("resultado"), peek = document.createElement("a");
  peek.className = "peek"; peek.href = "#resultado"; peek.hidden = true;
  peek.innerHTML = `<span></span><b></b><i>Ver ↓</i>`;
  peek.firstChild.textContent = (out.querySelector(".eyebrow") || {{ textContent: "Resultado" }}).textContent;
  document.body.appendChild(peek);
  const sync = () => {{ peek.children[1].textContent = $("o-main").textContent; }};
  new MutationObserver(sync).observe($("o-main"), {{ childList: true, characterData: true, subtree: true }}); sync();
  new IntersectionObserver(([e]) => {{ peek.hidden = e.isIntersecting || e.boundingClientRect.top < 0; }}, {{ threshold: 0.35 }}).observe(out);
  peek.addEventListener("click", (e) => {{ e.preventDefault(); out.scrollIntoView({{ behavior: FY.reduced ? "auto" : "smooth", block: "center" }}); }});
}}
{hero_js}
$("rem").addEventListener("click", () => {{ const r = ({remind})(); FY.compartir.ics(Object.assign({{ desc: `Calcula cuánto te toca: ${{FY.compartir.link("recordatorio")}}` }}, r)); }});
if (FY.CONFIG.AVISOS.whatsappCanal) {{ $("wa-canal").hidden = false; $("wa-canal").href = FY.CONFIG.AVISOS.whatsappCanal; }}
}})();
</script>
</body>
</html>
"""


def build():
    for slug, p in PAGES.items():
        url = f"{SITE}{slug}/"
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "WebApplication", "name": p["h1"], "url": url, "applicationCategory": "FinanceApplication", "operatingSystem": "Web", "inLanguage": "es-MX",
             "offers": {"@type": "Offer", "price": "0", "priceCurrency": "MXN"}, "description": p["desc"]},
            {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Quincy", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": p["h1"], "item": url}]}]}
        faq_html = "".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in p["faq"])
        related = "".join(f'<a class="chip-btn" href="../{s}/">{html.escape(n)}</a>' for s, n in RELATED if s != slug)
        out = TEMPLATE.format(title=html.escape(p["title"]), desc=html.escape(p["desc"]), url=url, site=SITE, ld=json.dumps(ld, ensure_ascii=False),
                              h1=html.escape(p["h1"]), intro=html.escape(p["intro"]), form=p["form"], out=p["out"], body=p["body"], faq_html=faq_html,
                              related=related, app=p["app"], js=p["js"],
                              eyebrow=html.escape(p.get("eyebrow", EYEBROW)), fuente=p.get("fuente", FUENTE), slug=slug,
                              share=SHARE[slug], remind_label=REMIND.get(slug, REMIND_DEFAULT)[0], remind=REMIND.get(slug, REMIND_DEFAULT)[1],
                              hero_extra='<div class="cd" id="cd"></div>' if slug in HERO_EXTRA else "",
                              hero_js=f"({HERO_EXTRA[slug]})();" if slug in HERO_EXTRA else "")
        d = ROOT / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(out, encoding="utf-8")
        print("ok", slug)


if __name__ == "__main__":
    build()
