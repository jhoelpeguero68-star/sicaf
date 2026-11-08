// Service Worker PWA SICAF Campo
const CACHE_NAME = 'sicaf-offline-v1';
const ASSETS = [
  '/',
  '/mobile.html',
  '/manifest.json',
  '/img/logo.jpg',
  'https://cdn.tailwindcss.com',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.map((k) => { if (k !== CACHE_NAME) return caches.delete(k); })
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  if (e.request.method === 'GET') {
    e.respondWith(
      caches.match(e.request).then((res) => res || fetch(e.request).catch(() => caches.match('/mobile.html')))
    );
  }
});
