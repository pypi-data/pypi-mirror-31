importScripts('workbox-sw.prod.v2.1.3.js');

/**
 * DO NOT EDIT THE FILE MANIFEST ENTRY
 *
 * The method precache() does the following:
 * 1. Cache URLs in the manifest to a local cache.
 * 2. When a network request is made for any of these URLs the response
 *    will ALWAYS comes from the cache, NEVER the network.
 * 3. When the service worker changes ONLY assets with a revision change are
 *    updated, old cache entries are left as is.
 *
 * By changing the file manifest manually, your users may end up not receiving
 * new versions of files because the revision hasn't changed.
 *
 * Please use workbox-build or some other tool / approach to generate the file
 * manifest which accounts for changes to local files and update the revision
 * accordingly.
 */
const fileManifest = [
  {
    "url": "vendor.bundle.js",
    "revision": "fac070a168919f2f154ee19d11537223"
  },
  {
    "url": "view.bundle.js",
    "revision": "79cb96b45f7428192063f4d47df80cb7"
  },
  {
    "url": "view.legacy.bundle.js",
    "revision": "46b268810cb10d85d6acbb59a8b5392f"
  }
];

const workboxSW = new self.WorkboxSW({
  "skipWaiting": true,
  "clientsClaim": true
});
workboxSW.precache(fileManifest);
workboxSW.router.registerRoute(/\/dataset\/(\w+)\/stages/, workboxSW.strategies.staleWhileRevalidate({}), 'GET');
workboxSW.router.registerRoute(/\/dataset\/(\w+)\/record(.*)/, workboxSW.strategies.staleWhileRevalidate({}), 'GET');
