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
        "desc": "Calcula tu aguinaldo 2026 con la Ley Federal del Trabajo: mínimo 15 días de salario, proporcional si entraste este año, cuánto está libre de ISR y la fecha límite de pago.",
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
<p>El aguinaldo está libre de ISR hasta 30 veces la UMA diaria. Con la UMA de 2026 ($117.31) son <b>$3,519.30</b>. Lo que pase de esa cantidad sí paga ISR.</p>""",
        "faq": [
            ("¿Cuánto me toca de aguinaldo en 2026?", "Mínimo 15 días de salario. Con un sueldo de $15,000 al mes son $7,500 si trabajaste todo el año."),
            ("¿Cuándo me tienen que pagar el aguinaldo?", "Antes del 20 de diciembre, según el artículo 87 de la Ley Federal del Trabajo."),
            ("Si entré a trabajar a mitad de año, ¿me toca aguinaldo?", "Sí, la parte proporcional a los días que trabajaste en el año."),
            ("¿El aguinaldo paga impuestos?", "Está exento de ISR hasta 30 UMA ($3,519.30 en 2026). Lo que pase de esa cantidad paga ISR."),
        ],
    },
    "finiquito": {
        "title": "Calculadora de finiquito y liquidación 2026",
        "h1": "Calculadora de finiquito y liquidación 2026",
        "desc": "Calcula tu finiquito si renuncias o tu liquidación si te despiden sin causa: aguinaldo y vacaciones proporcionales, prima vacacional, prima de antigüedad e indemnización de 3 meses, con valores 2026.",
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
        "desc": "Tabla de vacaciones dignas 2026 (artículo 76 de la Ley Federal del Trabajo): 12 días el primer año, 14, 16, 18, 20 y luego 2 más cada 5 años. Calcula tus días y tu prima vacacional.",
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
        "title": "PTU 2027: cuánto te toca de reparto de utilidades y cuándo",
        "h1": "Reparto de utilidades (PTU)",
        "desc": "Calcula el tope de tu PTU: 3 meses de salario o el promedio de tus últimos 3 años, lo que más te convenga. Fechas límite: 30 de mayo (empresas) y 29 de junio (personas físicas).",
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
}

RELATED = [("aguinaldo", "Aguinaldo 2026"), ("finiquito", "Finiquito y liquidación"), ("vacaciones", "Vacaciones dignas"), ("ptu", "PTU"), ("tanda", "Tandas"), ("quincena", "Cuánto gastar al día")]

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
<meta property="og:image" content="{site}img/og.png">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{ld}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@600;800&family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
<link rel="stylesheet" href="../css/app.css">
<style>
/* Layout: a calculator page for search. The calculator sits beside the explanation on wide screens and on top on phones. */
body{{padding-bottom:0}}
.calc-hero{{padding-block:34px 10px;display:grid;gap:12px;max-width:46rem}}
.calc-hero h1{{font-size:clamp(1.9rem,5vw,3rem);line-height:1.05;font-weight:800;letter-spacing:-.03em}}
.calc-hero p{{color:var(--mut);font-size:1.08rem}}
.calc{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;align-items:start;margin-top:18px}}
@media (max-width:820px){{.calc{{grid-template-columns:minmax(0,1fr)}}}}
.calc-big{{font:800 clamp(2rem,6vw,3rem)/1 var(--f-display);color:var(--sun)}}
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
    <p class="eyebrow">Calculadora gratuita · Ley Federal del Trabajo · 2026</p>
    <h1>{h1}</h1>
    <p>{intro}</p>
  </section>
  <div class="calc">
    <form class="card" onsubmit="return false" aria-label="Tus datos">{form}</form>
    <div class="card" aria-live="polite">{out}</div>
  </div>
  <article class="article">
    {body}
    <h2>Preguntas frecuentes</h2>
    {faq_html}
    <div class="cta-band">
      <div><h2>Todo esto y más, todos los días</h2><p class="mut" style="margin:6px 0 0">Tu límite de gasto diario, tus derechos, tus tandas y tu futuro. Gratis y sin registro.</p></div>
      <a class="btn btn-sun" href="../app.html#{app}">Abrir Quincy</a>
    </div>
    <h2>Otras calculadoras</h2>
    <nav class="related" aria-label="Otras calculadoras">{related}</nav>
    <p class="small mut" style="margin-top:24px">Herramienta educativa con el mínimo de ley y valores de 2026 (salario mínimo de CONASAMI y UMA de INEGI). No es asesoría legal ni fiscal. Fuente: <a href="https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf" target="_blank" rel="noopener">Ley Federal del Trabajo</a>.</p>
  </article>
</main>
<footer><div class="wrap"><p><b>Quincy</b> · Lo que te toca, cuándo te toca y cuánto te queda.</p></div></footer>
<script src="../js/core.js"></script>
<script src="../js/ley.js"></script>
<script>
(() => {{
const $ = (id) => document.getElementById(id);
const today = (() => {{ const t = new Date(); return new Date(t.getFullYear(), t.getMonth(), t.getDate(), 12); }})();
const parse = (s) => {{ const m = /^(\\d{{4}})-(\\d{{2}})-(\\d{{2}})$/.exec(s || ""); return m ? new Date(+m[1], +m[2] - 1, +m[3], 12) : null; }};
const iso = (d) => `${{d.getFullYear()}}-${{String(d.getMonth() + 1).padStart(2, "0")}}-${{String(d.getDate()).padStart(2, "0")}}`;
{js}
document.querySelectorAll("input,select").forEach((el) => el.addEventListener("input", run));
run();
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
                              related=related, app=p["app"], js=p["js"])
        d = ROOT / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(out, encoding="utf-8")
        print("ok", slug)


if __name__ == "__main__":
    build()
