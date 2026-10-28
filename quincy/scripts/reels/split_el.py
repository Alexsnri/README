"""Split an ElevenLabs reel voiceover into per-scene WAVs at the N-1 longest pauses."""
import sys, os, re, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reels_def as D
HERE = os.path.dirname(os.path.abspath(__file__)); EL = os.path.join(HERE, 'el'); BUILD = os.path.join(HERE, 'build')
SR = 44100
for rid in sys.argv[1:]:
    mp3 = os.path.join(EL, rid + '.mp3'); lines = [s[0] for s in D.R[rid]]; n = len(lines)
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', mp3, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    log = subprocess.run(['ffmpeg', '-hide_banner', '-i', mp3, '-af', 'silencedetect=noise=-38dB:d=0.3', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(v) for v in re.findall(r'silence_start: ([\d.]+)', log)]; en = [float(v) for v in re.findall(r'silence_end: ([\d.]+)', log)]
    merged = []
    for s_, e_ in zip(st, en):
        if merged and s_ - merged[-1][1] < 0.06:
            merged[-1][1] = e_
        else:
            merged.append([s_, e_])
    gaps = [(e - s, s, e) for s, e in merged if s > 0.2 and e < len(x) / SR - 0.2]
    cuts = sorted(sorted(gaps, reverse=True)[:n - 1], key=lambda g: g[1])
    if len(cuts) != n - 1:
        sys.exit(f'{rid}: expected {n-1} pauses, found {len(cuts)}')
    weakest = min(c[0] for c in cuts); strong_sentence = sorted(gaps, reverse=True)[n - 1][0] if len(gaps) >= n else 0
    bounds = [0.0] + [(s + e) / 2 for _, s, e in cuts] + [len(x) / SR]
    for i in range(n):
        seg = x[int(bounds[i] * SR):int(bounds[i + 1] * SR)]
        idx = np.where(np.abs(seg) > 10 ** (-40 / 20))[0]
        seg = seg[max(0, idx[0] - int(0.03 * SR)):min(len(seg), idx[-1] + int(0.08 * SR))]
        p = os.path.join(BUILD, f'{rid}-s{i}.wav')
        with wave.open(p, 'w') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(seg, -1, 1) * 32767).astype(np.int16).tobytes())
        open(p + '.txt', 'w', encoding='utf-8').write(lines[i])
    print(f'{rid}: {n} escenas, pausa de escena más corta {weakest:.2f}s vs pausa de frase más larga {strong_sentence:.2f}s', 'OK' if weakest > strong_sentence + 0.15 else 'REVISAR')
