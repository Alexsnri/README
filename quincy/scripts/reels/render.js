// node render.js <buildDir> <id> [--stills t1,t2,...] [--out file.mp4]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const [dir, id] = process.argv.slice(2, 4);
const args = process.argv.slice(4);
const stills = args.includes('--stills') ? args[args.indexOf('--stills') + 1].split(',').map(Number) : null;
const out = args.includes('--out') ? args[args.indexOf('--out') + 1] : `${dir}/${id}-video.mp4`;
const FPS = 30;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  const errs = []; p.on('pageerror', (e) => errs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + dir + '/' + id + '.html'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
  const dur = await p.evaluate(() => window.DUR);
  if (stills) {
    for (const t of stills) { await p.evaluate((t) => window.render(t), t); await p.screenshot({ path: `${dir}/${id}-still-${t}.jpg`, type: 'jpeg', quality: 80 }); }
  } else {
    const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
    const n = Math.ceil(dur * FPS);
    for (let i = 0; i < n; i++) {
      await p.evaluate((t) => window.render(t), i / FPS);
      const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    }
    ff.stdin.end(); await new Promise((r) => ff.on('close', r));
  }
  console.log(id, dur, 'errors', errs.length ? errs : 'none');
  await b.close();
})();
