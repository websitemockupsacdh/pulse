import { useState } from "react";
import { ErrorBox, ItemList, Loading, PageHead } from "../components/ui";
import { useApi } from "../lib/api";
import type { Item } from "../lib/types";

type Cfg = { title: string; lede: string; categories: [string, string][]; kind?: string; note?: string };
const ALL: [string, string] = ["", "All"];

export const CATEGORY_PAGES: Record<string, Cfg> = {
  news: { title: "News", lede: "Philippine and international publishers in one list. Each item shows who published it and when.", kind: "news",
    categories: [ALL, ["national", "National"], ["politics", "Politics and Government"], ["business", "Business and Economy"], ["weather", "Weather and Environment"], ["health", "Health and Public Safety"], ["technology", "Technology and Science"], ["international", "International"]] },
  sports: { title: "Sports", lede: "Local and international coverage. Schedules, results and standings appear only where a connected source provides them.",
    categories: [ALL], note: "Sport-by-sport filters (basketball, volleyball, boxing and others) turn on when a sports data source is connected." },
  science: { title: "Science & Technology", lede: "Research and technology coverage. Preprints, press releases and media reports are labelled separately once research sources are connected.",
    categories: [ALL, ["technology", "Technology"], ["science", "Science"]] },
  entertainment: { title: "Entertainment", lede: "Film, music, television and celebrity coverage from connected sources.", categories: [ALL] },
  business: { title: "Business & Economy", lede: "Markets, prices and policy.", categories: [ALL] },
  gaming: { title: "Gaming", lede: "Games and esports.", categories: [ALL] },
  international: { title: "International Affairs", lede: "Developments abroad that matter to the Philippines.", categories: [ALL] },
  education: { title: "Education", lede: "Schools, universities and policy.", categories: [ALL] },
  lifestyle: { title: "Lifestyle", lede: "Food, travel, health and culture.", categories: [ALL] },
  environment: { title: "Environment", lede: "Climate, conservation and pollution.", categories: [ALL] },
};
const FIXED_CAT: Record<string, string> = { sports: "sports", entertainment: "entertainment", business: "business", gaming: "gaming",
  international: "international", education: "education", lifestyle: "lifestyle", environment: "environment" };

export default function Category({ page }: { page: string }) {
  const cfg = CATEGORY_PAGES[page];
  const [cat, setCat] = useState("");
  const [window, setWindow] = useState("");
  const { data, error, loading } = useApi<Item[]>("/feed", { kind: cfg.kind, category: FIXED_CAT[page] ?? (cat || undefined), window, limit: "60" });
  return (
    <>
      <PageHead title={cfg.title} lede={cfg.lede} />
      <div className="mb-6 flex flex-wrap gap-2 border-y rule py-4">
        {cfg.categories.length > 1 && cfg.categories.map(([v, l]) => <button key={l} className="chip" aria-pressed={cat === v} onClick={() => setCat(v)}>{l}</button>)}
        <span className="mx-2 hidden w-px bg-rule md:block" />
        {[["", "Any time"], ["24h", "24 hours"], ["7d", "7 days"]].map(([v, l]) => <button key={l} className="chip" aria-pressed={window === v} onClick={() => setWindow(v)}>{l}</button>)}
      </div>
      {cfg.note && <p className="mb-4 text-sm text-muted">{cfg.note}</p>}
      {error && <ErrorBox msg={error} />}
      {loading ? <Loading /> : <ItemList items={data ?? []} />}
    </>
  );
}
