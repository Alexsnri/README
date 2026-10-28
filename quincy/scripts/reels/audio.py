"""Quincy reel audio: original music bed + synced SFX + voiceover with ducking. Writes build/<id>-mix.wav"""
import json, sys, os, wave, math
import numpy as np
from scipy import signal

SR = 44100
rng = np.random.default_rng(11)
HERE = os.path.dirname(os.path.abspath(__file__)); BUILD = os.path.join(HERE, 'build')

def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
def env_adsr(n, a, r, sus=1.0):
    e = np.ones(n) * sus; ka = min(n, int(a * SR)); kr = min(n, int(r * SR))
    if ka: e[:ka] = np.linspace(0, 1, ka) * sus
    if kr: e[-kr:] *= np.linspace(1, 0, kr)
    return e
def lp(x, f, o=2): b, a = signal.butter(o, f / (SR / 2), 'low'); return signal.lfilter(b, a, x)
def hp(x, f, o=2): b, a = signal.butter(o, f / (SR / 2), 'high'); return signal.lfilter(b, a, x)
def bp(x, f1, f2, o=2): b, a = signal.butter(o, [f1 / (SR / 2), f2 / (SR / 2)], 'band'); return signal.lfilter(b, a, x)
def saw(f, n, det=0.0):
    t = np.arange(n) / SR; ph = (t * f * (1 + det)) % 1.0; return 2 * ph - 1
def add(buf, x, t, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if i < len(buf) and j > i: buf[i:j] += x[:j - i] * g
def reverb(x, secs=1.2, wet=0.18):
    n = int(secs * SR); ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 6, n)); ir = lp(ir, 5000); ir /= np.sqrt(np.sum(ir ** 2))
    return x * (1 - wet) + signal.fftconvolve(x, ir)[:len(x)] * wet

# --- music: vi–IV–I–V in C at 100 BPM (Am F C G), warm pad + pluck arp + bass + soft drums
BPM = 100; BEAT = 60 / BPM; BAR = BEAT * 4
CHORDS = [[57, 60, 64], [53, 57, 60], [48, 55, 60, 64], [55, 59, 62]]  # Am F C G
ROOTS = [45, 41, 48, 43]

def music(dur):
    n = int((dur + 2) * SR); pad = np.zeros(n); pl = np.zeros(n); bass = np.zeros(n); drums = np.zeros(n); kick_env = np.zeros(n)
    bars = int(math.ceil(dur / BAR)) + 1
    for b in range(bars):
        t0 = b * BAR; ch = CHORDS[b % 4]; root = ROOTS[b % 4]; m = int(BAR * SR)
        x = sum(saw(midi(k), m, d) for k in ch for d in (-0.004, 0.0, 0.005)) / (len(ch) * 3)
        add(pad, lp(x, 2600) * env_adsr(m, 0.35, 0.5), t0, 1.1)
        arp = ch + [ch[1] + 12]
        for s in range(8):
            k = arp[[0, 1, 2, 3, 2, 1, 2, 3][s]] + 12; ln = int(0.5 * SR); tt = np.arange(ln) / SR
            y = (np.sin(2 * np.pi * midi(k) * tt) + 0.35 * np.sin(4 * np.pi * midi(k) * tt) + 0.12 * np.sin(6 * np.pi * midi(k) * tt)) * np.exp(-tt * 7)
            add(pl, y, t0 + s * BEAT / 2, 0.42 if s % 2 == 0 else 0.30)
        for bt in (0, 1.5, 2, 3.5):
            ln = int(BEAT * 0.9 * SR); tt = np.arange(ln) / SR
            y = np.tanh(2.2 * np.sin(2 * np.pi * midi(root - 12 + (12 if bt == 3.5 else 0)) * tt)) * env_adsr(ln, 0.01, 0.15)
            add(bass, y, t0 + bt * BEAT, 0.26 if bt in (0, 2) else 0.16)
        for bt in (0, 2, 2.75):
            ln = int(0.4 * SR); tt = np.arange(ln) / SR; f = 48 + 110 * np.exp(-tt * 30)
            y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9); add(drums, y, t0 + bt * BEAT, 0.5 if bt != 2.75 else 0.28)
            add(kick_env, np.exp(-tt * 7), t0 + bt * BEAT, 1.0)
        for bt in (1, 3):
            ln = int(0.22 * SR); y = bp(rng.standard_normal(ln), 1200, 5200) * np.exp(-np.arange(ln) / SR * 22); add(drums, y, t0 + bt * BEAT, 0.36)
        for s in range(8):
            ln = int(0.05 * SR); y = hp(rng.standard_normal(ln), 7000) * np.exp(-np.arange(ln) / SR * 90)
            add(drums, y, t0 + s * BEAT / 2 + (0.02 if s % 2 else 0), 0.16 if s % 2 else 0.09)
    duck = 1 - 0.55 * np.clip(kick_env, 0, 1)
    mix = reverb(pad * duck + pl, 1.6, 0.25) + bass * duck + drums
    mix = mix[:int(dur * SR)]
    fade = int(1.2 * SR); mix[-fade:] *= np.linspace(1, 0, fade); mix[:int(0.03 * SR)] *= np.linspace(0, 1, int(0.03 * SR))
    return mix / (np.max(np.abs(mix)) + 1e-9)

# --- SFX
def whoosh(d=0.5):
    n = int(d * SR); x = rng.standard_normal(n); out = np.zeros(n); y = 0.0
    cut = 300 + 5000 * np.sin(np.linspace(0, np.pi, n)) ** 2
    for i in range(n):
        a = 1 - math.exp(-2 * math.pi * cut[i] / SR); y += a * (x[i] - y); out[i] = y
    return out * np.sin(np.linspace(0, np.pi, n)) ** 1.5
def pop():
    n = int(0.09 * SR); tt = np.arange(n) / SR; f = 520 * np.exp(tt * 9)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 38)
def tick():
    n = int(0.018 * SR); tt = np.arange(n) / SR; return (np.sin(2 * np.pi * 3200 * tt) * 0.6 + hp(rng.standard_normal(n), 4000) * 0.4) * np.exp(-tt * 260)
def ding():
    n = int(1.1 * SR); tt = np.arange(n) / SR
    return sum(g * np.sin(2 * np.pi * f * tt) * np.exp(-tt * k) for f, g, k in ((1568, 1, 4), (2352, .5, 6), (3136, .3, 8), (4704, .15, 12)))
def impact():
    n = int(1.2 * SR); tt = np.arange(n) / SR; f = 38 + 90 * np.exp(-tt * 12)
    return np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2)) + lp(rng.standard_normal(n), 2500) * np.exp(-tt * 9) * 0.35

def read_wav(p):
    with wave.open(p) as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    return signal.resample_poly(x, SR, sr) if sr != SR else x

def mix(rid):
    J = json.load(open(os.path.join(BUILD, rid + '.json'))); dur = J['dur']; n = int(dur * SR)
    vo = np.zeros(n)
    for v in J['vo']:
        x = read_wav(v['wav']); x = hp(x, 90); x = x / (np.max(np.abs(x)) + 1e-9) * 0.89; add(vo, x, v['t'])
    # voice presence: gentle compression + slight brightness
    vo = np.tanh(vo * 1.25) / np.tanh(1.25)
    sfx = np.zeros(n)
    for e in J['events']:
        k, t = e['kind'], e['t']
        if k == 'impact': add(sfx, impact(), t, 0.55)
        elif k == 'whoosh': add(sfx, whoosh(0.5), max(0, t - 0.2), 0.32)
        elif k == 'pop': add(sfx, pop(), t, 0.16)
        elif k == 'ding': add(sfx, ding(), t, 0.12)
        elif k == 'ticks':
            d = e.get('d', 1); tt = t
            while tt < t + d: add(sfx, tick(), tt, 0.10); tt += 0.065
        elif k == 'spin':
            d = e.get('d', 3.6); end = 5 * 360 + 202.5; last = 0
            for i in range(int(d * 200)):
                x = i / (d * 200); p = 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2; seg = int(p * end // 45)
                if seg != last: add(sfx, tick(), t + x * d, 0.22); last = seg
    mus = music(dur)
    # duck music under the voice
    envv = np.abs(vo); envv = signal.lfilter([1 - 0.9995], [1, -0.9995], envv); envv = envv / (np.max(envv) + 1e-9)
    g = 1 - 0.58 * np.clip(envv * 4, 0, 1); g = signal.lfilter([1 - 0.9997], [1, -0.9997], g)
    out = vo * 1.0 + mus[:n] * 0.30 * g + sfx
    stereo = np.stack([out, out], 1)
    stereo /= max(1.0, np.max(np.abs(stereo)) / 0.95)
    p = os.path.join(BUILD, rid + '-mix.wav')
    with wave.open(p, 'w') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((stereo * 32767).astype(np.int16).tobytes())
    return p

if __name__ == '__main__':
    for rid in sys.argv[1:]:
        print(mix(rid))
