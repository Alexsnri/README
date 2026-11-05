// Network only: the dashboard always shows live data. It only exists so it can be installed as an app on the phone.
self.addEventListener("install", e => self.skipWaiting());
self.addEventListener("activate", e => self.clients.claim());
self.addEventListener("fetch", () => {});
