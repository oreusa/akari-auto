/* 11/2 オーナー「全部」→ ホーム画面に置けるように（PWA）。
   ページはいつもネットから新しいものを出す。電波がない時だけ、前に開いたページを出す。
   数える所（/c /stats /wx）や他のサイトにはさわらない。 */
var C="ln-v1";
self.addEventListener("install",function(){self.skipWaiting();});
self.addEventListener("activate",function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k!==C;}).map(function(k){return caches.delete(k);}));}).then(function(){return self.clients.claim();}));});
self.addEventListener("fetch",function(e){var r=e.request;if(r.method!=="GET"||r.mode!=="navigate")return;var u=new URL(r.url);if(u.origin!==location.origin||/^\/(c|wx|koe-send)(\/|$)/.test(u.pathname))return;
e.respondWith(fetch(r).then(function(res){if(res&&res.ok){var cp=res.clone();caches.open(C).then(function(c){c.put(r,cp);});}return res;}).catch(function(){return caches.match(r).then(function(m){return m||caches.match("/");});}));});
