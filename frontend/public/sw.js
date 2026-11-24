self.addEventListener("push", (event) => {
  if (!event.data) return;
  const payload = event.data.json();
  event.waitUntil(self.registration.showNotification(payload.title || "PULSE update", {
    body: payload.publisher ? `New update from ${payload.publisher}` : "A new update matches your alert settings.",
    icon: "/acdhlogo.png",
    data: { url: payload.url || "/" },
  }));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = event.notification.data && event.notification.data.url;
  if (!url) return;
  event.waitUntil(clients.openWindow(url));
});
