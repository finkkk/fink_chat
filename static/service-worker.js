const CACHE_NAME = "fink-chat-cache-v1";
const urlsToCache = [
  "/",
  "/home",
  "/static/icon.ico",
  "/static/icon_192.webp",
  "/static/icon_512.webp"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) =>
      cache.addAll(urlsToCache)
    ).catch(err => console.error("缓存失败：", err))
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => response || fetch(event.request))
  );
});
