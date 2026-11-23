import { useState } from "react";
import { ErrorBox, Loading, PageHead, TopicIndex, TopicPreview } from "../components/ui";
import { useApi } from "../lib/api";
import type { Topic } from "../lib/types";

const WINDOWS = [["", "Any time"], ["1h", "1 hour"], ["6h", "6 hours"], ["24h", "24 hours"], ["7d", "7 days"]];
const STATUSES = ["emerging", "rising", "active", "declining", "archived"];
const CATS = ["", "national", "business", "technology", "sports", "entertainment", "international", "weather"];

export default function Trending() {
  const [region, setRegion] = useState("PH");
  const [window, setWindow] = useState("");
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");
  const [hover, setHover] = useState<Topic | null>(null);
  const { data, error, loading } = useApi<Topic[]>("/trending", { region: region || undefined, window, status, category, limit: "60" });

  const Group = ({ label, children }: { label: string; children: React.ReactNode }) => (
    <fieldset className="flex flex-wrap items-center gap-2"><legend className="sr-only">{label}</legend><span className="tick w-20">{label}</span>{children}</fieldset>
  );
  return (
    <>
      <PageHead title="Trending" lede="Topics ranked by how fast new items arrive from different publishers. Status comes from measured velocity and thresholds you can configure." />
      <div className="mb-8 space-y-3 border-y rule py-4">
        <Group label="Region">{[["PH", "Philippines"], ["INTL", "International"], ["", "Both"]].map(([v, l]) => <button key={l} className="chip" aria-pressed={region === v} onClick={() => setRegion(v)}>{l}</button>)}</Group>
        <Group label="Window">{WINDOWS.map(([v, l]) => <button key={l} className="chip" aria-pressed={window === v} onClick={() => setWindow(v)}>{l}</button>)}</Group>
        <Group label="Status">{["", ...STATUSES].map((v) => <button key={v} className="chip capitalize" aria-pressed={status === v} onClick={() => setStatus(v)}>{v || "All"}</button>)}</Group>
        <Group label="Category">{CATS.map((v) => <button key={v} className="chip capitalize" aria-pressed={category === v} onClick={() => setCategory(v)}>{v || "All"}</button>)}</Group>
        <p className="text-xs text-muted">National, regional and city filters appear once sources supply reliable location data.</p>
      </div>
      {error && <ErrorBox msg={error} />}
      {loading ? <Loading /> : (
        <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
          <TopicIndex topics={data ?? []} onHover={setHover} />
          <div className="hidden lg:block"><TopicPreview t={hover ?? data?.[0] ?? null} /></div>
        </div>
      )}
    </>
  );
}
