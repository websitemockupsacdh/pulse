import { Bell, BellOff } from "lucide-react";
import { useEffect, useState } from "react";
import { get, send } from "../lib/api";

const CRITERIA = [
  ["national", "National news"], ["politics", "Politics"], ["business", "Business"],
  ["international", "International"], ["health", "Health & safety"], ["technology", "Technology"],
  ["sports", "Sports"], ["weather", "Weather & disasters"], ["science", "Science"],
  ["entertainment", "Entertainment"], ["kpop", "K-pop"], ["jpop", "J-pop"], ["ppop", "P-pop"],
  ["prc", "PRC exam updates"], ["gaming", "Gaming"], ["education", "Education"],
  ["lifestyle", "Lifestyle"], ["environment", "Environment"],
];
const STORAGE_KEY = "pulse-notification-criteria";

type Criteria = { categories: string[]; keywords: string[] };
type PushKey = { public_key: string };
type SubscribeResult = { subscribed: boolean };

function decodeKey(value: string) {
  const base64 = value.replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(base64 + "=".repeat((4 - base64.length % 4) % 4));
  return Uint8Array.from(raw, (char) => char.charCodeAt(0));
}

export default function Notifications() {
  const [open, setOpen] = useState(false);
  const [available, setAvailable] = useState(false);
  const [enabled, setEnabled] = useState(false);
  const [categories, setCategories] = useState<string[]>([]);
  const [keywordsText, setKeywordsText] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setAvailable("serviceWorker" in navigator && "PushManager" in window && "Notification" in window);
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const criteria = JSON.parse(saved) as Criteria;
        if (Array.isArray(criteria.categories)) setCategories(criteria.categories);
        if (Array.isArray(criteria.keywords)) setKeywordsText(criteria.keywords.join(", "));
      }
    } catch {
      localStorage.removeItem(STORAGE_KEY);
    }
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.getRegistration("/").then(async (registration) => {
        if (registration) setEnabled(Boolean(await registration.pushManager.getSubscription()));
      }).catch(() => setMessage("Could not check this device's notification status."));
    }
  }, []);

  const toggleCategory = (category: string) => {
    setCategories((current) => current.includes(category)
      ? current.filter((value) => value !== category)
      : [...current, category]);
  };

  const criteria = (): Criteria => ({
    categories,
    keywords: [...new Set(keywordsText.split(",").map((word) => word.trim()).filter(Boolean))].slice(0, 10),
  });

  const enable = async () => {
    setBusy(true);
    setMessage("");
    try {
      const selected = criteria();
      if (!selected.categories.length && !selected.keywords.length) {
        throw new Error("Choose a topic or add a keyword first.");
      }
      if (!available) throw new Error("Push notifications are not supported by this browser.");
      const key = await get<PushKey>("/notifications/public-key");
      const permission = Notification.permission === "granted" ? "granted" : await Notification.requestPermission();
      if (permission !== "granted") throw new Error("Allow notifications in your browser settings to continue.");
      const registration = await navigator.serviceWorker.register("/sw.js");
      const subscription = await registration.pushManager.getSubscription() ?? await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: decodeKey(key.public_key),
      });
      await send<SubscribeResult>("/notifications/subscribe", "POST", {
        endpoint: subscription.endpoint,
        keys: subscription.toJSON().keys ?? {},
        ...selected,
      });
      localStorage.setItem(STORAGE_KEY, JSON.stringify(selected));
      setEnabled(true);
      setMessage("Notifications are on for this device.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not enable notifications.");
    } finally {
      setBusy(false);
    }
  };

  const disable = async () => {
    setBusy(true);
    setMessage("");
    try {
      const registration = await navigator.serviceWorker.getRegistration("/");
      const subscription = await registration?.pushManager.getSubscription();
      if (subscription) {
        await send<SubscribeResult>("/notifications/subscribe", "DELETE", { endpoint: subscription.endpoint });
        await subscription.unsubscribe();
      }
      setEnabled(false);
      setMessage("Notifications are off for this device.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not disable notifications.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="relative shrink-0">
      <button type="button" className="btn-quiet notification-trigger" aria-expanded={open} aria-label="Notification settings"
        onClick={() => setOpen((value) => !value)}>
        {enabled ? <Bell className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
        <span className="hidden sm:inline">{enabled ? "Alerts on" : "Alerts"}</span>
      </button>
      {open && (
        <section className="glass-panel notification-panel" aria-label="Notification preferences">
          <div className="flex items-start justify-between gap-3">
            <div><p className="tick">Push notifications</p><h2 className="mt-1 text-xl">Choose what to follow</h2></div>
            <button type="button" className="text-sm underline" onClick={() => setOpen(false)}>Close</button>
          </div>
          {!available && <p className="mt-3 text-sm text-muted">This browser does not support web push.</p>}
          <fieldset className="mt-4 grid grid-cols-2 gap-2 text-sm">
            <legend className="mb-2 col-span-2 text-xs text-muted">Alerts match any selected topic or keyword.</legend>
            {CRITERIA.map(([key, title]) => (
              <label key={key} className="flex items-center gap-2">
                <input type="checkbox" checked={categories.includes(key)} onChange={() => toggleCategory(key)} />
                {title}
              </label>
            ))}
          </fieldset>
          <label className="mt-4 block text-sm">
            Keywords <span className="text-muted">(comma-separated)</span>
            <input value={keywordsText} onChange={(event) => setKeywordsText(event.target.value)} maxLength={400}
              placeholder="e.g. Gilas, typhoon, board exam"
              className="mt-1 w-full rounded-lg border border-rule bg-white/70 px-3 py-2 text-sm" />
          </label>
          <p className="mt-2 text-xs text-muted">On iPhone, add PULSE to your Home Screen to receive push alerts. Availability also depends on server push configuration.</p>
          <div className="mt-4 flex gap-2">
            <button type="button" className="btn" disabled={busy || !available} onClick={enable}>{busy ? "Saving…" : "Save & enable"}</button>
            {enabled && <button type="button" className="btn-quiet" disabled={busy} onClick={disable}>Turn off</button>}
          </div>
          {message && <p className="mt-3 text-sm text-muted" role="status">{message}</p>}
        </section>
      )}
    </div>
  );
}
