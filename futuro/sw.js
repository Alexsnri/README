// Futuro Yo: funciona sin conexión. Red primero (tasas y versiones nuevas), caché si no hay internet.
const CACHE = "futuro-yo-v2";
const CORE = [
  "./", "index.html", "empresas.html", "manifest.webmanifest", "css/app.css",
  "js/core.js", "js/avatar.js", "js/aging.js", "js/sim.js", "js/habits.js", "js/reto.js", "js/share.js", "js/app.js",
  "img/icon.svg", "img/icon-192.png", "data/rates.json"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  e.respondWith(
    fetch(e.request)
      .then((res) => { if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(e.request, copy)); } return res; })
      .catch(() => caches.match(e.request, { ignoreSearch: true }).then((r) => r || caches.match("index.html")))
  );
});
