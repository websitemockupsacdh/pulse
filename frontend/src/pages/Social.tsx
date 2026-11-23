import { useState } from "react";
import { Empty, ErrorBox, ItemList, Loading, PageHead } from "../components/ui";
import { useApi } from "../lib/api";
import type { Item, SourceInfo } from "../lib/types";

const PLATFORMS = [["x", "X"], ["threads", "Threads"], ["facebook", "Facebook"], ["instagram", "Instagram"], ["tiktok", "TikTok"], ["reddit", "Reddit"]];

export default function Social() {
  const [p, setP] = useState("reddit");
  const { data, error, loading } = useApi<Item[]>("/feed", { kind: "social", platform: p, limit: "50" });
  const { data: sources } = useApi<SourceInfo[]>("/sources");
  const src = sources?.find((s) => s.slug === p);
  return (
    <>
      <PageHead title="Social Radar" lede="Public conversations, one platform at a time. Each platform needs its own authorized access. Where we do not have it, the page says so instead of filling the gap." />
      <div className="mb-6 flex flex-wrap gap-2 border-y rule py-4" role="group" aria-label="Platform">
        {PLATFORMS.map(([v, l]) => <button key={v} className="chip" aria-pressed={p === v} onClick={() => setP(v)}>{l}</button>)}
      </div>
      {error && <ErrorBox msg={error} />}
      {loading ? <Loading /> : data?.length ? <ItemList items={data} showEngagement /> : (
        <Empty>
          {src && !src.enabled ? "This platform is not connected." : null}
          {src?.last_status.startsWith("error") ? ` Adapter status: ${src.last_status.replace("error: ", "")}.` : " No public posts collected yet."}
          {" "}Engagement counts show as "Not provided by source" unless the platform returns them. They are never shown as zero.
        </Empty>
      )}
    </>
  );
}
