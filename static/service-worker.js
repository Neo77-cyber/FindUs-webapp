// service-worker.js - SIMPLE VERSION
const CACHE_NAME = 'findus-v1';
const OFFLINE_URL = '/offline/';  // Your offline page URL

// Files to cache immediately
const urlsToCache = [
  '/',
  '/static/assets/css/colors.css',
  '/static/assets/css/style.css',
  '/static/assets/css/search.css',
  '/static/assets/css/results.css',
  '/static/icons/192.png',
  '/static/icons/512.png',
  OFFLINE_URL  // Cache the offline page itself
];

// INSTALL: Cache essential files
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
      .then(() => self.skipWaiting())
  );
});

// ACTIVATE: Clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== CACHE_NAME) {
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => self.clients.claim())
  );
});

// FETCH: Serve from cache, network, or show offline page
self.addEventListener('fetch', event => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        // If in cache, return it
        if (cachedResponse) {
          return cachedResponse;
        }

        // Otherwise fetch from network
        return fetch(event.request)
          .then(networkResponse => {
            // Cache successful responses (optional)
            if (networkResponse.ok) {
              const clone = networkResponse.clone();
              caches.open(CACHE_NAME)
                .then(cache => cache.put(event.request, clone));
            }
            return networkResponse;
          })
          .catch(() => {
            // NETWORK FAILED
            // If it's a page navigation, show offline page
            if (event.request.mode === 'navigate') {
              return caches.match(OFFLINE_URL)
                .then(offlinePage => offlinePage || new Response('You are offline'));
            }
            
            // For other requests (images, CSS, etc.), return error
            return new Response('Offline', {
              status: 408,
              headers: { 'Content-Type': 'text/plain' }
            });
          });
      })
  );
});