/**
 * Service Worker for ABC Assessment PWA.
 * Cache-first strategy for static assets; network fallback with dynamic caching.
 */

var CACHE_NAME = 'abc-assessment-v3';

var PRECACHE_URLS = [
    './',
    './index.html',
    './personalization.js',
    './personalization-section-16.js',
    './submit-assessment-enhanced.js',
    './offline-storage.js',
    'https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js',
    'https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.1.0/dist/chartjs-plugin-annotation.min.js'
];

// Install: precache core assets
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(PRECACHE_URLS);
        }).then(function() {
            return self.skipWaiting();
        })
    );
});

// Activate: clean up old cache versions
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(name) {
                    return name.startsWith('abc-assessment-') && name !== CACHE_NAME;
                }).map(function(name) {
                    return caches.delete(name);
                })
            );
        }).then(function() {
            return self.clients.claim();
        })
    );
});

// Fetch: cache-first, then network, caching new responses
self.addEventListener('fetch', function(event) {
    // Only handle GET requests
    if (event.request.method !== 'GET') return;

    event.respondWith(
        caches.match(event.request).then(function(cachedResponse) {
            if (cachedResponse) {
                return cachedResponse;
            }
            return fetch(event.request).then(function(networkResponse) {
                // Only cache successful responses from http(s)
                if (networkResponse && networkResponse.status === 200 &&
                    (event.request.url.startsWith('http://') || event.request.url.startsWith('https://'))) {
                    var responseToCache = networkResponse.clone();
                    caches.open(CACHE_NAME).then(function(cache) {
                        cache.put(event.request, responseToCache);
                    });
                }
                return networkResponse;
            }).catch(function() {
                // If both cache and network fail, return a simple offline message
                // (only for navigation requests)
                if (event.request.mode === 'navigate') {
                    return new Response(
                        '<html><body><h1>Offline</h1><p>The ABC Assessment is not available offline. Please check your connection.</p></body></html>',
                        { headers: { 'Content-Type': 'text/html' } }
                    );
                }
            });
        })
    );
});
