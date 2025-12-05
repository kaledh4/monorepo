
const CACHE_NAME = 'the-map-1764922483772';
const ASSETS_TO_CACHE = [
  "./",
  "./index.html",
  "./manifest.json",
  "./app.js",
  "./icons/favicon.ico",
  "./icons/icon-192.png",
  "./icons/icon-192x192.png",
  "./icons/icon-192x192.svg",
  "./icons/icon-256x256.png",
  "./icons/icon-256x256.svg",
  "./icons/icon-384x384.png",
  "./icons/icon-384x384.svg",
  "./icons/icon-512.png",
  "./icons/icon-512x512.png",
  "./icons/icon-512x512.svg",
  "./interactive.css",
  "./service-worker.js",
  "./static/app.js",
  "./static/icons/favicon.ico",
  "./static/icons/icon-192.png",
  "./static/icons/icon-192x192.png",
  "./static/icons/icon-192x192.svg",
  "./static/icons/icon-256x256.png",
  "./static/icons/icon-256x256.svg",
  "./static/icons/icon-384x384.png",
  "./static/icons/icon-384x384.svg",
  "./static/icons/icon-512.png",
  "./static/icons/icon-512x512.png",
  "./static/icons/icon-512x512.svg",
  "./static/interactive.css",
  "./static/manifest.json",
  "./static/style.css",
  "./static/sw.js",
  "./style.css",
  "./sw.js"
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS_TO_CACHE))
      .catch((error) => {
        console.error('Failed to cache assets:', error);
      })
  );
  self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached response if found
        if (response) {
          return response;
        }
        // Otherwise fetch from network
        return fetch(event.request).then((response) => {
          // Don't cache non-successful responses
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }
          
          // Clone the response
          const responseToCache = response.clone();
          
          // Cache the fetched response for future use
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
          
          return response;
        });
      })
      .catch(() => {
        // Return a custom offline page if available
        return caches.match('./index.html');
      })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});
