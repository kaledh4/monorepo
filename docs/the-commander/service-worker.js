
const CACHE_NAME = 'the-commander-1764921899229';
const ASSETS_TO_CACHE = [
  "./",
  "./index.html",
  "./manifest.json",
  "./.gitignore",
  "./app-unified.js",
  "./app.js",
  "./data/latest.json",
  "./favicon.ico",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icons8-ai-48.png",
  "./icons/icons8-coin-64.png",
  "./icons/icons8-commander-of-the-canadian-navy-48.png",
  "./icons/icons8-library-48.png",
  "./icons/icons8-map-48.png",
  "./icons/icons8-shield-48.png",
  "./icons/icons8-strategy-48.png",
  "./index-unified.html",
  "./scripts/generate-brief.js",
  "./service-worker.js",
  "./static/icons/favicon.ico",
  "./static/icons/icon-192x192.png",
  "./static/icons/icon-512x512.png",
  "./styles.css",
  "./styles_enhanced.css",
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
