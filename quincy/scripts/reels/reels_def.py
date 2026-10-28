"""Quincy · animated reels with voiceover.

Each scene has a voiceover line. Elements appear when the voice says their keyword (K('palabra')).
Builds, per reel: build/<id>.html (frames), build/<id>.json (timeline: vo clips, sfx events, duration).
"""
import json, os, subprocess, sys, wave, math

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build'); os.makedirs(BUILD, exist_ok=True)
VOICE = os.path.join(os.path.dirname(HERE), 'tts', 'es_MX-claude-high.onnx')
ENGINE = open(os.path.join(HERE, 'engine.html'), encoding='utf-8').read()
LEN_SCALE = '0.9'


def tts(text, path):
    meta = path + '.txt'
    if not (os.path.exists(path) and os.path.exists(meta) and open(meta, encoding='utf-8').read() == text):
        subprocess.run([sys.executable, '-m', 'piper', '-m', VOICE, '-f', path, '--length-scale', LEN_SCALE, '--sentence-silence', '0.12'],
                       input=text.encode(), check=True, capture_output=True)
        open(path + '.txt', 'w', encoding='utf-8').write(text)
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


TICK = '<div class="tick"><svg viewBox="0 0 24 24" fill="none" stroke="#07121a" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div>'


class Ctx:
    """Helpers available inside a scene: K() times, E() events."""
    def __init__(self, t0, vo, dur, events):
        self.t0, self.vo, self.dur, self.events = t0, vo.lower(), dur, events

    def K(self, word, plus=0.0):
        i = self.vo.find(word.lower())
        if i < 0:
            raise KeyError(f'"{word}" not in VO: {self.vo}')
        return round(self.t0 + 0.2 + (i / max(1, len(self.vo))) * self.dur * 0.97 + plus, 3)

    def T(self, x):
        return round(self.t0 + x, 3)

    def E(self, t, kind, **kw):
        self.events.append(dict(t=round(t, 3), kind=kind, **kw)); return t


def a(t, anim='up', d=None, extra=''):
    return f'data-in="{t}" data-a="{anim}"' + (f' data-d="{d}"' if d else '') + (f' {extra}' if extra else '')


def words(t, html, cls='h-xl', step=0.08, anim='up'):
    return f'<div class="{cls} words" data-w="{t}" data-ws="{step}" data-wa="{anim}">{html}</div>'


def count(c, t, a_, b_, fmt='int', d=1.1, pre='', suf='', cls='num'):
    c.E(t, 'ticks', d=d); c.E(t + d, 'ding')
    return f'<div class="{cls}" {a(t, "pop")} data-count="{a_},{b_}" data-ct="{t}" data-cd="{d}" data-fmt="{fmt}" data-pre="{pre}" data-suf="{suf}">{pre}{a_}{suf}</div>'


def cta(c, line, sub='Link en bio'):
    t = c.T(0.15)
    c.E(c.K('quincy') if 'quincy' in c.vo else t + 1.0, 'ding')
    return f'''<div class="cta">
  <div class="logo" {a(t, 'pop')}><i></i><span>quincy<b>.</b></span></div>
  {words(t + 0.35, line, 'h-m', 0.07)}
  <div class="btn" {a(t + 1.1, 'pop', extra=f'data-pulse="{t + 1.6}"')}>{sub}</div>
  <div class="small" {a(t + 1.4, 'up')}>Gratis · sin registro · sin bancos</div>
</div>'''


# ---------------------------------------------------------------- scenes per reel
# Each scene: (voiceover, min_seconds, builder(ctx) -> html, extra_class)

R = {}

R['00-conoce-quincy'] = [
    ('Esta app te dice lo que te toca, cuándo te toca y cuánto te queda.', 3.0, lambda c: f'''
      <div class="chip" {a(c.T(0.02), 'left', 0.3)}>Te presento</div>
      {words(c.T(0.1), 'La app que te dice <b>lo que te toca</b>', step=0.07)}
      <div class="t" {a(c.K('cuánto te queda'))}>…cuándo te toca y <b>cuánto te queda.</b></div>''', ''),
    ('Te da un solo número al día: lo que puedes gastar hoy para llegar a la quincena.', 3.5, lambda c: f'''
      <div class="h-m" {a(c.T(0.1))}>Un solo número al día</div>
      <div style="position:relative;width:620px;height:620px;align-self:center" {a(c.T(0.2), 'pop')}>
        <svg viewBox="0 0 440 440" width="620" height="620" style="position:absolute;inset:0;transform:rotate(-90deg)"><circle cx="220" cy="220" r="190" fill="none" stroke="#1e3a4a" stroke-width="34"/><circle cx="220" cy="220" r="190" fill="none" stroke="#86e3a8" stroke-width="34" stroke-linecap="round" stroke-dasharray="1193.8" data-len="1193.8" data-draw="{c.K('número')}" data-to="0.62" style="stroke-dashoffset:1193.8"/></svg>
        <div style="position:absolute;inset:0;display:grid;place-content:center;text-align:center;gap:6px"><div class="small">Hoy puedes gastar</div>{count(c, c.K('número'), 0, 250, 'money', 1.2, cls='num mid')}</div>
      </div>''', ''),
    ('Calcula tu aguinaldo, tus vacaciones y tu reparto de utilidades con la ley de dos mil veintiséis.', 4.0, lambda c: f'''
      <div class="chip sun" {a(c.T(0.05), 'left', 0.3)}>Con la ley de 2026</div>
      <div class="card" {a(c.K('aguinaldo'), 'right')}><div class="small">Aguinaldo</div>{count(c, c.K('aguinaldo', .2), 0, 6000, 'money', 1.0, cls='h-l')}</div>
      <div class="card" {a(c.K('vacaciones'), 'right')}><div class="small">Vacaciones</div><div class="h-l">12 días <span class="t">+ prima</span></div></div>
      <div class="card" {a(c.K('reparto'), 'right')}><div class="small">Reparto de utilidades</div><div class="h-l">hasta 3 meses</div></div>''', 'top'),
    ('Y organiza tu tanda con ruleta, sin pleitos.', 2.8, lambda c: f'''
      <div style="align-self:center" {a(c.T(0.05), 'pop')}>{wheel_svg('w0', 560)}</div>
      {words(c.K('tanda'), 'Tandas <b>sin pleitos</b>', 'h-l')}''', ''),
    ('Es gratis, sin registro y sin bancos.', 2.4, lambda c: f'''
      <div class="h-xl" {a(c.K('gratis'), 'pop', extra=f'data-shake="{c.K("gratis", .3)}"')}><b>Gratis.</b></div>
      <div class="h-xl" {a(c.K('sin registro'), 'pop')}>Sin registro.</div>
      <div class="h-xl" {a(c.K('sin bancos'), 'pop')}>Sin bancos.</div>''', ''),
    ('Encuéntrala en el link de nuestro perfil. Quincy.', 3.4, lambda c: cta(c, 'Síguenos para más <b>trucos de quincena</b>'), ''),
]

R['01-aguinaldo-ley'] = [
    ('Tu aguinaldo no es un regalo. Es ley.', 2.6, lambda c: f'''
      <div class="chip" {a(c.T(0.02), 'left', 0.3)}>Aguinaldo 2026</div>
      {words(c.T(0.08), 'Tu aguinaldo <b>no es un regalo</b>', step=0.08)}
      <div class="h-l" {a(c.K('es ley'), 'pop', extra=f'data-shake="{c.K("es ley", .25)}"')}>Es <b>ley.</b></div>''', ''),
    ('Te toca mínimo quince días de salario.', 3.0, lambda c: f'''
      <div class="t" {a(c.T(0.05))}>Te toca mínimo</div>
      <div class="row" style="align-items:flex-end">{count(c, c.K('quince'), 0, 15, 'int', 0.9)}<div class="h-m" {a(c.K('días'))} style="padding-bottom:30px">días de<br>salario</div></div>
      <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:14px;width:640px">{''.join(f'<div style="height:96px;border-radius:16px;background:#ffb547" {a(c.K("quince", 0.06 * i), "pop", 0.3)}></div>' for i in range(15))}</div>''', ''),
    ('Si ganas doce mil pesos al mes, son cuatrocientos al día. Por quince días: seis mil pesos.', 5.0, lambda c: f'''
      <div class="chip sun" {a(c.T(0.05), 'left', 0.3)}>Ejemplo</div>
      <div class="card">
        <div class="eq" {a(c.K('doce mil'), 'left')}><span>Sueldo al mes</span><span>$12,000</span></div>
        <div class="eq" {a(c.K('cuatrocientos'), 'left')}><span>÷ 30 = al día</span><span>$400</span></div>
        <div class="eq" {a(c.K('por quince'), 'left')}><span>× 15 días</span><span>× 15</span></div>
        <div class="eq total" {a(c.K('seis mil'), 'up')}><span>Tu aguinaldo</span>{count(c, c.K('seis mil'), 0, 6000, 'money', 0.9, cls='')}</div>
      </div>''', ''),
    ('Y te lo tienen que pagar antes del veinte de diciembre.', 3.2, lambda c: f'''
      {words(c.T(0.05), 'Te lo tienen que pagar <b>antes del</b>', 'h-l', 0.07)}
      <div style="position:relative;align-self:center;width:440px" {a(c.K('veinte'), 'drop', 0.5)}>
        <div style="background:#f3f5f4;border-radius:40px;overflow:hidden;text-align:center;box-shadow:0 30px 80px rgba(0,0,0,.5)">
          <div style="background:#ff8574;color:#fff;font:800 64px/1 Unbounded;padding:28px">DIC</div>
          <div style="font:800 240px/1.1 Unbounded;color:#07121a;padding:10px 0 30px">20</div></div>
        <svg viewBox="0 0 500 500" style="position:absolute;inset:-70px;width:580px;height:580px;pointer-events:none"><ellipse cx="250" cy="270" rx="230" ry="215" fill="none" stroke="#ffb547" stroke-width="14" stroke-linecap="round" stroke-dasharray="1400" data-len="1400" data-draw="{c.K('diciembre')}" data-dd="0.7" style="stroke-dashoffset:1400"/></svg>
      </div>''', ''),
    ('¿Entraste este año? Te toca la parte proporcional.', 3.0, lambda c: f'''
      {words(c.T(0.05), '¿Entraste <b>este año</b>?', 'h-l')}
      <div class="t" {a(c.K('proporcional'))}>Te toca la parte proporcional:</div>
      <div style="height:64px;border-radius:99px;background:#1e3a4a;overflow:hidden" {a(c.K('proporcional'))}><div class="grow" style="height:100%;background:linear-gradient(90deg,#5ad6c8,#ffb547)" data-grow="{c.K('proporcional', .2)}" data-to="0.583" data-gd="1.0"></div></div>
      <div class="pill" {a(c.K('proporcional', .9))}>7 meses trabajados → 8.75 días</div>''', ''),
    ('Calcula el tuyo gratis en Quincy. Y mándaselo a quien todavía no sabe cuánto le toca.', 4.0, lambda c: cta(c, 'Mándaselo a quien <b>no sabe cuánto le toca</b>', 'Calcula el tuyo · link en bio'), ''),
]

R['02-renuncias'] = [
    ('¿Vas a renunciar? No pierdes tu aguinaldo.', 2.6, lambda c: f'''
      <div class="chip" {a(c.T(0.02), 'left', 0.3)}>Finiquito</div>
      {words(c.T(0.08), '¿Renuncias? <b>No pierdes tu aguinaldo</b>', step=0.08)}''', ''),
    ('Tu finiquito incluye los días que no te han pagado, tu aguinaldo proporcional, las vacaciones que no tomaste y su prima vacacional.', 6.0, lambda c: f'''
      <div class="h-m" {a(c.T(0.05))}>Tu finiquito incluye:</div>
      {''.join(f'<div class="row" {a(c.K(k), "left")}><span {a(c.K(k), "pop")}>{TICK}</span><div class="item">{txt}</div></div>' for k, txt in [('días que no', 'Días trabajados que no te han pagado'), ('aguinaldo proporcional', 'Aguinaldo proporcional'), ('vacaciones que', 'Vacaciones que no tomaste'), ('su prima', 'Prima vacacional (25% o más)')])}''', ''),
    ('Si ganas quince mil pesos y renuncias el treinta de noviembre, solo de aguinaldo te tocan casi seis mil novecientos pesos.', 5.5, lambda c: f'''
      <div class="chip sun" {a(c.T(0.05), 'left', 0.3)}>Ejemplo</div>
      <div class="h-m" {a(c.K('quince mil'))}>Ganas <b>$15,000</b> y renuncias el <b>30 de noviembre</b></div>
      <div class="t" {a(c.K('solo de aguinaldo'))}>Solo de aguinaldo te tocan:</div>
      {count(c, c.K('casi seis'), 0, 6863, 'money', 1.2, cls='num mid')}
      <div class="small" {a(c.K('casi seis', 1.0))}>15 días × 334/365 × $500 al día</div>''', ''),
    ('Pídelo por escrito y revisa todo antes de firmar.', 2.8, lambda c: f'''
      {words(c.T(0.05), 'Pídelo <b>por escrito</b>', 'h-xl')}
      {words(c.K('revisa'), 'y revisa todo <b>antes de firmar.</b>', 'h-l')}''', ''),
    ('Calcula tu finiquito gratis en Quincy. Guárdalo, por si acaso.', 3.4, lambda c: cta(c, 'Guárdalo <b>por si acaso</b>', 'Calcula tu finiquito · link en bio'), ''),
]

R['03-aguinaldo-isr'] = [
    ('¿Por qué tu aguinaldo llega incompleto?', 2.6, lambda c: f'''
      <div class="chip" {a(c.T(0.02), 'left', 0.3)}>Aguinaldo e ISR</div>
      {words(c.T(0.08), '¿Por qué tu aguinaldo <b>llega incompleto</b>?', step=0.08)}''', ''),
    ('Los primeros tres mil quinientos diecinueve pesos no pagan impuesto.', 3.6, lambda c: f'''
      <div class="t" {a(c.T(0.05))}>Los primeros</div>
      {count(c, c.K('tres mil'), 0, 3519.30, 'money2', 1.3, cls='num sm')}
      <div class="h-m" {a(c.K('no pagan'), 'pop')}><b>no pagan</b> impuesto</div>
      <div class="pill" {a(c.K('impuesto', .3))}>30 × UMA 2026 ($117.31)</div>''', ''),
    ('Si tu aguinaldo es de diez mil, solo lo que pasa de esa cantidad paga I S R.', 4.5, lambda c: f'''
      <div class="h-m" {a(c.T(0.05))}>Aguinaldo de <b>$10,000</b></div>
      <div style="display:flex;height:150px;border-radius:28px;overflow:hidden;background:#1e3a4a" {a(c.T(0.2))}>
        <div class="grow" style="width:35.2%;background:#86e3a8;display:grid;place-items:center;font:800 40px Figtree;color:#07121a" data-grow="{c.K('diez mil')}">$3,519</div>
        <div class="grow" style="width:64.8%;background:#ffb547;display:grid;place-items:center;font:800 40px Figtree;color:#1a1206" data-grow="{c.K('solo lo que')}">$6,481</div></div>
      <div class="row" style="justify-content:space-between"><div class="t" {a(c.K('diez mil', .4))}><b style="color:#86e3a8">Exento</b></div><div class="t" {a(c.K('paga i s r'), 'pop')}><b style="color:#ffb547">Solo esto paga ISR</b></div></div>''', ''),
    ('No es un robo. Es el impuesto, y solo sobre una parte.', 3.0, lambda c: f'''
      {words(c.T(0.05), 'No es robo:', 'h-xl')}
      {words(c.K('es el impuesto'), '<b>es ISR</b>, y solo sobre una parte.', 'h-l')}''', ''),
    ('Guárdalo para diciembre y calcula el tuyo en Quincy.', 3.4, lambda c: cta(c, 'Guárdalo para <b>diciembre</b>', 'Calcula el tuyo · link en bio'), ''),
]

TANDA = [115, 89, 64, 38, 12, -13, -38, -64, -89, -114]
R['04-tanda-numero'] = [
    ('¿En la tanda pides el número uno o el diez?', 2.6, lambda c: f'''
      <div class="chip" {a(c.T(0.02), 'left', 0.3)}>Tandas</div>
      {words(c.T(0.08), '¿Pides el <b>número 1</b> o el <b>10</b>?', step=0.09)}''', ''),
    ('Imagina una tanda de diez personas que ponen mil pesos cada quincena.', 3.6, lambda c: f'''
      <div style="position:relative;width:640px;height:640px;align-self:center">
        {''.join(f'<div style="position:absolute;left:{320 + 260 * math.cos(i / 10 * 2 * math.pi - math.pi / 2) - 52:.0f}px;top:{320 + 260 * math.sin(i / 10 * 2 * math.pi - math.pi / 2) - 52:.0f}px;width:104px;height:104px;border-radius:50%;background:{"#ffb547" if i in (0, 9) else "#11283a"};border:4px solid #5ad6c8;display:grid;place-items:center;font:800 40px Unbounded;color:{"#1a1206" if i in (0, 9) else "#fff"}" {a(c.K("diez personas", 0.07 * i), "pop", 0.3)}>{i + 1}</div>' for i in range(10))}
        <div style="position:absolute;inset:0;display:grid;place-content:center;text-align:center" {a(c.K('mil pesos'), 'pop')}><div class="h-m">$1,000</div><div class="small">cada quincena</div></div>
      </div>''', ''),
    ('Comparado con invertir en cetes, el número uno gana unos ciento quince pesos. El último pierde lo mismo.', 5.6, lambda c: f'''
      <div class="small" {a(c.T(0.05))}>Ganancia o pérdida de cada número frente a CETES (6.23%)</div>
      <div style="position:relative;height:620px;display:grid;grid-template-columns:repeat(10,1fr);gap:14px;align-items:center">
        <div style="position:absolute;left:0;right:0;top:310px;height:4px;background:#2c5468"></div>
        {''.join(f'<div style="position:relative;height:620px"><div class="{"growy" if v > 0 else ""}" style="position:absolute;left:0;right:0;{"bottom:310px" if v > 0 else "top:314px"};height:{abs(v) / 115 * 260:.0f}px;border-radius:10px;background:{"#86e3a8" if v > 0 else "#ff8574"};transform-origin:{"bottom" if v > 0 else "top"}" data-grow="{c.K("comparado", 0.12 * i)}"></div><div style="position:absolute;left:-10px;right:-10px;top:592px;text-align:center;font:700 30px JetBrains Mono;color:#a9c0c8">{i + 1}</div></div>' for i, v in enumerate(TANDA))}
      </div>
      <div class="row" style="justify-content:space-between"><div class="h-m" {a(c.K('ciento quince'), 'pop')} style="color:#86e3a8">#1 +$115</div><div class="h-m" {a(c.K('pierde'), 'pop')} style="color:#ff8574">#10 −$114</div></div>''', 'top'),
    ('El primero recibe un préstamo sin intereses. El último presta su dinero gratis.', 4.0, lambda c: f'''
      <div class="card" {a(c.K('el primero'), 'left')} style="border-color:#86e3a8"><div class="h-m" style="color:#86e3a8">El #1</div><div class="item">recibe un <b>préstamo sin intereses</b></div></div>
      <div class="card" {a(c.K('el último'), 'right')} style="border-color:#ff8574"><div class="h-m" style="color:#ff8574">El #10</div><div class="item">presta su dinero <b>gratis</b></div></div>''', ''),
    ('Etiqueta a quien organiza tu tanda y calcula la tuya en Quincy.', 3.6, lambda c: cta(c, 'Etiqueta a quien <b>organiza tu tanda</b>', 'Calcula la tuya · link en bio'), ''),
]

R['05-te-despiden'] = [
    ('¿Te despidieron sin causa? No firmes nada todavía.', 2.8, lambda c: f'''
      <div class="chip" {a(c.T(0.02), 'left', 0.3)}>Liquidación</div>
      {words(c.T(0.08), '¿Te despidieron? <b>No firmes nada todavía</b>', step=0.08)}''', ''),
    ('Por ley te tocan tres meses de salario, doce días por cada año trabajado y tu finiquito completo.', 5.4, lambda c: f'''
      <div class="h-m" {a(c.T(0.05))}>Por ley te toca:</div>
      <div class="card" {a(c.K('tres meses'), 'left')}><div class="h-l"><b>3 meses</b></div><div class="t">de salario integrado</div></div>
      <div class="card" {a(c.K('doce días'), 'left')}><div class="h-l">+ <b>12 días</b> por año</div><div class="t">prima de antigüedad</div></div>
      <div class="card" {a(c.K('finiquito'), 'left')}><div class="h-l">+ tu <b>finiquito</b></div><div class="t">aguinaldo, vacaciones y prima</div></div>''', ''),
    ('Tienes dos meses para reclamar.', 2.6, lambda c: f'''
      <div class="t" {a(c.T(0.05))}>Tienes</div>
      <div class="row" style="align-items:flex-end">{count(c, c.K('dos meses'), 0, 2, 'int', 0.6)}<div class="h-l" {a(c.K('dos meses', .3))} style="padding-bottom:26px">meses</div></div>
      <div class="h-m" {a(c.K('reclamar'), 'pop', extra=f'data-shake="{c.K("reclamar", .3)}"')}>para <b>reclamar.</b></div>''', ''),
    ('Y la Profedet te asesora gratis.', 2.4, lambda c: f'''
      <div class="t" {a(c.T(0.05))}>Asesoría gratis:</div>
      <div class="h-xl" {a(c.K('profedet'), 'zoom', 0.5)}><b>PROFEDET</b></div>
      <div class="small" {a(c.K('gratis'))}>Procuraduría Federal de la Defensa del Trabajo</div>''', ''),
    ('Calcula tu liquidación en Quincy y mándaselo a quien lo necesite.', 3.6, lambda c: cta(c, 'Mándaselo a <b>quien lo necesite</b>', 'Calcula tu liquidación · link en bio'), ''),
]

NAMES = ['Ana', 'Beto', 'Caro', 'Tía Lupe', 'Memo', 'Jess', 'Lalo', 'Mamá']


def wheel_svg(wid, size):
    cols = ['#ffb547', '#5ad6c8', '#ff8574', '#86e3a8']
    segs = []
    for i, n in enumerate(NAMES):
        a0, a1 = (i * 45 - 90) * math.pi / 180, ((i + 1) * 45 - 90) * math.pi / 180
        x0, y0, x1, y1 = 200 + 190 * math.cos(a0), 200 + 190 * math.sin(a0), 200 + 190 * math.cos(a1), 200 + 190 * math.sin(a1)
        am = (i * 45 + 22.5 - 90) * math.pi / 180
        segs.append(f'<path d="M200 200 L{x0:.1f} {y0:.1f} A190 190 0 0 1 {x1:.1f} {y1:.1f} Z" fill="{cols[i % 4]}" stroke="#07121a" stroke-width="4"/>'
                    f'<text x="{200 + 120 * math.cos(am):.1f}" y="{200 + 120 * math.sin(am):.1f}" transform="rotate({i * 45 + 22.5} {200 + 120 * math.cos(am):.1f} {200 + 120 * math.sin(am):.1f})" text-anchor="middle" dominant-baseline="middle" font-family="Figtree" font-weight="800" font-size="24" fill="#07121a">{n}</text>')
    return (f'<div style="position:relative;width:{size}px;height:{size}px"><svg id="{wid}" viewBox="0 0 400 400" width="{size}" height="{size}">{"".join(segs)}<circle cx="200" cy="200" r="26" fill="#07121a" stroke="#eaf3f4" stroke-width="5"/></svg>'
            f'<svg viewBox="0 0 40 40" style="position:absolute;left:50%;top:-18px;width:70px;height:70px;transform:translateX(-50%)"><path d="M20 36 L6 8 H34 Z" fill="#eaf3f4" stroke="#07121a" stroke-width="2"/></svg></div>')


R['06-ruleta-tanda'] = [
    ('Se acabaron los pleitos por el número de la tanda.', 2.8, lambda c: f'''
      <div class="chip" {a(c.T(0.02), 'left', 0.3)}>Tandas</div>
      {words(c.T(0.08), 'Se acabaron los pleitos por <b>el número</b>', step=0.08)}''', ''),
    ('Gira la ruleta y que la suerte decida los turnos.', 5.2, lambda c: (c.E(c.K('gira'), 'spin', d=3.6), c.E(c.K('gira', 3.7), 'ding'), f'''
      <div style="align-self:center" {a(c.T(0.05), 'pop')} data-spin="{c.K('gira')}" data-target="3">{wheel_svg('w6', 720)}</div>
      <div class="h-l" style="text-align:center" {a(c.K('gira', 3.8), 'pop')}>Turno 1: <b>Tía Lupe</b></div>''')[-1], ''),
    ('Cada quien ve cuándo paga y cuándo cobra.', 3.2, lambda c: f'''
      <div class="card" style="gap:14px">{''.join(f'<div class="eq" style="font-size:44px" {a(c.T(0.15 + 0.16 * i), "left", 0.3)}><span>{i + 1}. {n}</span><span>{d}</span></div>' for i, (n, d) in enumerate(zip(['Tía Lupe', 'Jess', 'Ana', 'Memo', 'Mamá', 'Lalo', 'Caro', 'Beto'], ['15 nov', '30 nov', '15 dic', '31 dic', '15 ene', '31 ene', '15 feb', '28 feb'])))}</div>''', ''),
    ('Y lo mandas al grupo de WhatsApp en un toque.', 2.8, lambda c: f'''
      <div class="small" {a(c.T(0.05))}>Grupo: Tanda de la oficina</div>
      <div style="align-self:flex-end;max-width:820px;background:#1f5c4a;color:#fff;border-radius:40px 40px 8px 40px;padding:36px 42px;font:600 46px/1.35 Figtree;box-shadow:0 20px 60px rgba(0,0,0,.4)" {a(c.K('whatsapp'), 'pop')}>Ya quedaron los turnos de la tanda. Mira cuándo te toca → <span style="color:#86e3a8">quincy/tanda</span></div>
      <div class="h-m" {a(c.K('toque'))}>Cada quien ve <b>su fecha.</b></div>''', ''),
    ('Organiza la tuya gratis en Quincy.', 3.2, lambda c: cta(c, 'Organiza la tuya <b>gratis</b>'), ''),
]

R['07-hoy-puedes-gastar'] = [
    ('La regla que me salvó la quincena.', 2.6, lambda c: f'''
      <div class="chip" {a(c.T(0.02), 'left', 0.3)}>Tu quincena</div>
      {words(c.T(0.08), 'La regla que me <b>salvó la quincena</b>', step=0.09)}''', ''),
    ('Lo que te llega, menos tus pagos fijos y tu ahorro, entre los días que faltan.', 4.6, lambda c: f'''
      <div class="card">
        <div class="eq" {a(c.K('lo que te llega'), 'left')}><span>Te llega</span><span>$8,000</span></div>
        <div class="eq" {a(c.K('pagos fijos'), 'left')}><span>− pagos fijos</span><span>$3,500</span></div>
        <div class="eq" {a(c.K('tu ahorro'), 'left')}><span>− tu ahorro</span><span>$500</span></div>
        <div class="eq total" {a(c.K('entre'), 'up')}><span>÷ 16 días</span><span>$4,000</span></div>
      </div>''', ''),
    ('Ese es tu número de hoy: doscientos cincuenta pesos.', 3.0, lambda c: f'''
      <div class="h-m" style="text-align:center" {a(c.T(0.05))}>Hoy puedes gastar</div>
      <div style="position:relative;width:620px;height:620px;align-self:center" {a(c.T(0.1), 'pop')}>
        <svg viewBox="0 0 440 440" width="620" height="620" style="position:absolute;inset:0;transform:rotate(-90deg)"><circle cx="220" cy="220" r="190" fill="none" stroke="#1e3a4a" stroke-width="34"/><circle cx="220" cy="220" r="190" fill="none" stroke="#86e3a8" stroke-width="34" stroke-linecap="round" stroke-dasharray="1193.8" data-len="1193.8" data-draw="{c.K('doscientos')}" data-to="1" style="stroke-dashoffset:1193.8"/></svg>
        <div style="position:absolute;inset:0;display:grid;place-content:center">{count(c, c.K('doscientos'), 0, 250, 'money', 1.0, cls='num mid')}</div>
      </div>''', ''),
    ('Si hoy gastas solo ciento cincuenta, mañana puedes gastar más.', 3.4, lambda c: f'''
      <div class="row" {a(c.K('ciento cincuenta'), 'left')}><div class="pill">Hoy gastas $150</div></div>
      <div class="t" {a(c.K('mañana'))}>Mañana puedes gastar</div>
      {count(c, c.K('mañana'), 250, 256, 'money', 0.9)}
      <div class="h-m" {a(c.K('más'), 'pop')}>Si gastas menos, <b>mañana tienes más.</b></div>''', ''),
    ('¿Cuál es tu número de hoy? Calcúlalo en Quincy.', 3.2, lambda c: cta(c, '¿Cuál es <b>tu número de hoy</b>?', 'Calcúlalo · link en bio'), ''),
]

R['08-faltan-18-dias'] = [
    ('Faltan dieciocho días para tu aguinaldo.', 2.8, lambda c: f'''
      <div class="chip" {a(c.T(0.02), 'left', 0.3)}>Cuenta regresiva</div>
      {count(c, c.T(0.05), 30, 18, 'int', 1.4)}
      <div class="h-l" {a(c.K('días'))}>días para tu <b>aguinaldo</b></div>''', ''),
    ('Antes de gastarlo: paga lo que te cobra intereses, aparta para la cuesta de enero y págate primero.', 6.0, lambda c: f'''
      <div class="h-m" {a(c.T(0.05))}>Antes de gastarlo:</div>
      {''.join(f'<div class="card" {a(c.K(k), "left")}><div class="row"><div class="h-l" style="color:#ffb547;min-width:70px">{n}</div><div class="item">{txt}</div></div></div>' for n, k, txt in [(1, 'paga lo que', 'Paga lo que te cobra intereses'), (2, 'aparta', 'Aparta para la cuesta de enero'), (3, 'págate', 'Págate primero: ahorra una parte')])}''', ''),
    ('El límite es el diecinueve de diciembre. Si no te lo pagan, la Profedet te asesora gratis.', 4.6, lambda c: f'''
      {words(c.T(0.05), 'El límite es el <b>19 de diciembre.</b>', 'h-l', 0.08)}
      <div class="t" {a(c.K('si no te lo pagan'))}>Si no te lo pagan, <b>PROFEDET</b> te asesora gratis.</div>''', ''),
    ('Compártelo con tu equipo y calcula el tuyo en Quincy.', 3.4, lambda c: cta(c, 'Compártelo con <b>tu equipo</b>', 'Calcula el tuyo · link en bio'), ''),
]

CUSTOM = {
    '06-ruleta-tanda': '''window.custom = (t) => { document.querySelectorAll('[data-spin]').forEach((el) => { const t0 = +el.dataset.spin, k = +el.dataset.target; const p = inout((t - t0) / 3.6); const end = 5 * 360 + (360 - (k * 45 + 22.5)); el.querySelector('svg').style.transform = `rotate(${p * end}deg)`; }); };''',
    '00-conoce-quincy': '''window.custom = (t) => { const el = document.getElementById('w0'); if (el) el.style.transform = `rotate(${t * 70}deg)`; };''',
}


def build(rid):
    scenes = R[rid]
    events, vo, html, punch = [], [], [], []
    t0 = 0.0
    for i, (line, mn, fn, cls) in enumerate(scenes):
        wav = os.path.join(BUILD, f'{rid}-s{i}.wav')
        d = tts(line, wav)
        last = i == len(scenes) - 1
        length = max(mn, 0.2 + d + (1.6 if last else 0.45))
        c = Ctx(t0, line, d, events)
        inner = fn(c)
        out = '' if last else f' data-out="{t0 + length - 0.3:.3f}"'
        html.append(f'<div class="scene {cls}" data-in="{t0:.3f}" data-a="fade" data-d="0.2"{out}>{inner}</div>')
        vo.append(dict(t=round(t0 + 0.2, 3), wav=wav, d=round(d, 3)))
        events.append(dict(t=round(t0, 3), kind='impact' if i == 0 else 'whoosh'))
        if i: punch.append(round(t0, 3))
        t0 += length
    dur = round(t0, 3)
    for m in __import__('re').finditer(r'data-in="([\d.]+)" data-a="(pop|drop|zoom)"', ''.join(html)):
        events.append(dict(t=float(m.group(1)), kind='pop'))
    page = (ENGINE.replace('/*DUR*/', str(dur)).replace('/*PUNCH*/', json.dumps(punch)).replace('/*SCENES*/', '\n'.join(html))
            .replace('/*CUSTOM*/', CUSTOM.get(rid, '')))
    open(os.path.join(BUILD, f'{rid}.html'), 'w', encoding='utf-8').write(page)
    json.dump(dict(id=rid, dur=dur, vo=vo, events=sorted(events, key=lambda e: e['t'])), open(os.path.join(BUILD, f'{rid}.json'), 'w'), indent=1)
    return dur


if __name__ == '__main__':
    ids = sys.argv[1:] or list(R)
    for rid in ids:
        print(rid, f'{build(rid):.1f}s')
