// FidaMano PWA Service Worker - Cache First Strategy
// VERSION: 1.0.0 - Increment this when deploying updates to force cache refresh
const CACHE_VERSION = '1.0.0';
const CACHE_NAME = `fidamano-${CACHE_VERSION}`;
const STATIC_ASSETS = [
  '/',
  '/static/assets/css/colors.css',
  '/static/assets/css/style.css',
  '/static/assets/css/service-details.css',
  '/static/assets/css/services-details-2.css',
  '/static/assets/js/main.js',
  '/static/icons/192.png',
  '/static/icons/512.png',
  '/offline'
];

// Install - Cache static assets
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
      .catch((err) => console.log('Cache failed:', err))
  );
});

// Activate - Clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});

// Offline page HTML
const OFFLINE_HTML = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Offline - FidaMano</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #077f46;
      color: white;
      height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
      padding: 20px;
    }
    .icon { font-size: 64px; margin-bottom: 20px; }
    h1 { font-size: 28px; margin-bottom: 16px; font-weight: 600; }
    p { font-size: 18px; margin-bottom: 32px; opacity: 0.9; }
    button {
      background: white;
      color: #077f46;
      border: none;
      padding: 14px 32px;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.2s;
    }
    button:hover { transform: scale(1.05); }
  </style>
</head>
<body>
  <div class="icon">📶</div>
  <h1>Sei Offline</h1>
  <p>Controlla la tua connessione internet</p>
  <button onclick="window.location.reload()">Riprova</button>
  <script>
    window.addEventListener('online', () => window.location.reload());
  </script>
</body>
</html>`;

// Fetch - Cache first strategy
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;
  
  // Skip non-http requests
  if (!event.request.url.startsWith('http')) return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      // Return cached version or fetch new
      if (cachedResponse) {
        // Update cache in background
        fetch(event.request)
          .then((response) => {
            if (response.ok) {
              caches.open(CACHE_NAME).then((cache) => {
                cache.put(event.request, response.clone());
              });
            }
          })
          .catch(() => {});
        return cachedResponse;
      }

      // Fetch and cache
      return fetch(event.request)
        .then((response) => {
          if (!response || response.status !== 200) {
            return response;
          }
          
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
          
          return response;
        })
        .catch(() => {
          // Return offline page for navigation requests
          if (event.request.mode === 'navigate') {
            return new Response(OFFLINE_HTML, {
              headers: { 'Content-Type': 'text/html' }
            });
          }
        });
    })
  );
});

// Listen for skipWaiting message from client
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
});