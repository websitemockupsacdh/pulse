// Preview build only: answers /api calls from a bundled snapshot of demo data.
import snap from "./snapshot.json";
/* eslint-disable @typescript-eslint/no-explicit-any */
const S = snap as any;
const HOURS: Record<string, number> = { "1h": 1, "6h": 6, "24h": 24, "7d": 168 };
const RETIRED_TITLES = new Set(S.feed.filter((item: any) => ["social", "video"].includes(item.kind)).map((item: any) => item.title));
const within = (iso: string, w?: string | null) => !w || !HOURS[w] || Date.now() - new Date(iso + (iso.endsWith("Z") || iso.includes("+") ? "" : "Z")).getTime() < HOURS[w] * 3.6e6;
const json = (d: unknown) => new Response(JSON.stringify(d), { headers: { "content-type": "application/json" } });

export function installMock() {
  const real = window.fetch;
  window.fetch = async (input: RequestInfo | URL) => {
    const url = new URL(typeof input === "string" ? input : input.toString(), location.origin);
    if (!url.pathname.startsWith("/api")) return real(input);
    const p = url.pathname.slice(4), q = (k: string) => url.searchParams.get(k);
    if (p === "/sources") return json(S.sources);
    if (p === "/home") {
      const base = S.home[q("region") ?? "PH"] ?? S.home.PH;
      const sections = base.sections.filter((section: any) => !["social", "video", "sports_ent"].includes(section.key))
        .map((section: any) => section.topics ? { ...section, topics: section.topics.filter((topic: any) => !RETIRED_TITLES.has(topic.title)) } : section);
      const keys = new Set(sections.map((section: any) => section.key));
      for (const [key, title] of [["weather", "Weather and disasters"], ["sports", "Sports"], ["science", "Science and technology"],
        ["entertainment", "Entertainment and showbiz"], ["kpop", "K-pop"], ["jpop", "J-pop"], ["ppop", "P-pop"], ["prc", "PRC exam updates"]]) {
        if (!keys.has(key)) sections.push({ key, title, items: S.feed.filter((item: any) => item.category === key && !["social", "video"].includes(item.kind)).slice(0, 5) });
      }
      return json({ ...base, sections });
    }
    if (p === "/trending") return json(S.topics.filter((t: any) => !RETIRED_TITLES.has(t.title) && (!q("region") || t.region === q("region")) && (!q("status") || t.status === q("status")) && (!q("category") || t.category === q("category"))));
    if (p === "/feed") return json(S.feed.filter((i: any) => !["social", "video"].includes(i.kind) && (!q("kind") || i.kind === q("kind")) && (!q("category") || i.category === q("category")) && (!q("platform") || i.platform === q("platform")) && (!q("region") || i.region === q("region")) && (!q("live") || i.live_status === q("live")) && within(i.published_at, q("window"))));
    if (p === "/search") {
      const terms = (q("q") ?? "").toLowerCase().replace(/"/g, "").split(/\s+/).filter(Boolean);
      const items = S.feed.filter((i: any) => !["social", "video"].includes(i.kind) && terms.every((t) => (i.title + " " + i.snippet).toLowerCase().includes(t)) && (!q("kind") || i.kind === q("kind")) && (!q("region") || i.region === q("region")) && within(i.published_at, q("window")));
      return json({ total: items.length, items, topics: S.topics.filter((t: any) => !RETIRED_TITLES.has(t.title) && terms.length && terms.every((x) => t.title.toLowerCase().includes(x))).slice(0, 6) });
    }
    if (p.startsWith("/topics/")) { const e = S.explorer[p.slice(8)]; return e ? json(e) : new Response("{}", { status: 404 }); }
    if (p === "/stream") return new Promise<Response>(() => {});
    return new Response("{}", { status: 404 });
  };
  (window as any).EventSource = undefined; // no live stream in the static preview
}
