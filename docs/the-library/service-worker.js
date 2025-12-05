
const CACHE_NAME = 'the-library-1764922579370';
const ASSETS_TO_CACHE = [
  "./",
  "./index.html",
  "./manifest.json",
  "./.gitignore",
  "./app-unified.js",
  "./app.js",
  "./dist/index.html",
  "./dist/vite.svg",
  "./eslint.config.js",
  "./favicon.ico",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./index-unified.html",
  "./public/vite.svg",
  "./src/App.css",
  "./src/App.tsx",
  "./src/assets/react.svg",
  "./src/index.css",
  "./src/main.tsx",
  "./static/icons/favicon.ico",
  "./static/icons/icon-192x192.png",
  "./static/icons/icon-512x512.png",
  "./tsconfig.app.json",
  "./tsconfig.json",
  "./tsconfig.node.json",
  "./vite.config.ts",
  "./vite.svg"
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
