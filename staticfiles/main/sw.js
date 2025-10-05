// Service Worker - Offline desteği ve push notifications
const CACHE_NAME = 'rumep-v1.0.0';
const urlsToCache = [
  '/',
  '/static/main/css/modern.css',
  '/static/main/js/realtime.js',
  '/offline/',
  '/static/main/manifest.json'
];

// Install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache açıldı');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache'de varsa döndür
        if (response) {
          return response;
        }
        
        // Network'ten getir
        return fetch(event.request).catch(() => {
          // Offline sayfasını göster
          if (event.request.destination === 'document') {
            return caches.match('/offline/');
          }
        });
      })
  );
});

// Activate event
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Eski cache siliniyor:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Push notification event
self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'Yeni bir bildiriminiz var!',
    icon: '/static/main/icons/icon-192x192.png',
    badge: '/static/main/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Görüntüle',
        icon: '/static/main/icons/checkmark.png'
      },
      {
        action: 'close',
        title: 'Kapat',
        icon: '/static/main/icons/xmark.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Rumep', options)
  );
});

// Notification click event
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Background sync
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  // Offline'da yapılan işlemleri senkronize et
  return fetch('/api/sync-offline-data/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      timestamp: Date.now()
    })
  });
}