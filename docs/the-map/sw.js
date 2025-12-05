const CACHE_NAME = 'the-map-v1';
const ASSETS_TO_CACHE = [
  '/EconomicCompass/',
  '/EconomicCompass/static/style.css',
  '/EconomicCompass/static/interactive.css',
  '/EconomicCompass/static/app.js',
  '/EconomicCompass/static/manifest.json',
  '/EconomicCompass/static/icons/icon-192x192.png',
  '/EconomicCompass/static/icons/icon-256x256.png',
  '/EconomicCompass/static/icons/icon-384x384.png',
  '/EconomicCompass/static/icons/icon-512x512.png'
];

// Install event - cache assets
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching assets');
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('Service Worker: Clearing old cache');
            return caches.delete(cache);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  // Skip for OpenRouter API requests
  if (event.request.url.includes('openrouter.ai')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request).then((fetchResponse) => {
          // Cache new resources if they are valid and part of our app
          if (!fetchResponse || fetchResponse.status !== 200 || fetchResponse.type !== 'basic') {
            return fetchResponse;
          }

          const responseToCache = fetchResponse.clone();

          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });

          return fetchResponse;
        });
      })
      .catch(() => {
        // Offline fallback
        if (event.request.destination === 'document') {
          return caches.match('/EconomicCompass/');
        }
      })
  );
});

// Background sync for updates
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-updates') {
    event.waitUntil(syncUpdates());
  }
});

async function syncUpdates() {
  console.log('Service Worker: Syncing updates...');
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage({
      type: 'SYNC_UPDATES',
      timestamp: Date.now()
    });
  });
}

// Handle messages from the app
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});