export type Item = {
  id: number; title: string; snippet: string; url: string; kind: string; platform: string; category: string;
  region: string; author: string; publisher: string; published_at: string;
  engagement: Record<string, number> | null; // null means the source did not supply it
  live_status: "live" | "upcoming" | "completed" | null; severity: string | null; syndicated: boolean; topic_slug: string | null;
};
export type Topic = {
  slug: string; title: string; category: string; region: string; first_detected_at: string; last_updated_at: string;
  item_count: number; source_count: number; velocity: number; status: "emerging" | "rising" | "active" | "declining" | "archived"; summary: string;
};
export type HomeSection = { key: string; title: string; items?: Item[]; topics?: Topic[] };
export type Home = { region: string; generated_at: string; sections: HomeSection[] };
export type SourceInfo = { slug: string; name: string; kind: string; region: string; url: string; enabled: boolean; last_status: string; last_run_at: string | null };
export type Explorer = {
  topic: Topic; briefing: { text: string | null; citations: string[]; note: string | null };
  timeline: { at: string; title: string; publisher: string; url: string }[];
  ph_news: Item[]; international: Item[]; social: Item[]; videos: Item[]; live: Item[]; official: Item[];
  conflicts: { claim: string; sources: string[] }[]; related_topics: Topic[]; sources: [string, string][];
};
