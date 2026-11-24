import { useSearchParams } from "react-router-dom";
import { useState } from "react";
import { Empty, ErrorBox, ItemList, Loading, PageHead, TopicIndex } from "../components/ui";
import { useApi } from "../lib/api";
import type { Item, Topic } from "../lib/types";

type Res = { total: number; items: Item[]; topics: Topic[] };
const KINDS = [["", "Everything"], ["news", "News"], ["official", "Official"]];

export default function Search() {
  const [sp, setSp] = useSearchParams();
  const q = sp.get("q") ?? "";
  const [draft, setDraft] = useState(q);
  const [kind, setKind] = useState("");
  const [sort, setSort] = useState("relevance");
  const [window, setWindow] = useState("");
  const [region, setRegion] = useState("");
  const { data, error, loading } = useApi<Res>("/search", { q: q || undefined, kind, sort, window, region });

  return (
    <>
      <PageHead title="Search" lede="Search across news, official bulletins and topic collections. Use quotation marks for an exact phrase." />
      <form role="search" onSubmit={(e) => { e.preventDefault(); setSp({ q: draft }); }} className="flex max-w-2xl">
        <label htmlFor="sq" className="sr-only">Search</label>
        <input id="sq" value={draft} onChange={(e) => setDraft(e.target.value)} className="min-w-0 flex-1 border border-rule bg-stone px-4 py-3" />
        <button className="btn">Search</button>
      </form>
      <div className="my-6 space-y-3 border-y rule py-4">
        <div className="flex flex-wrap gap-2">{KINDS.map(([v, l]) => <button key={l} className="chip" aria-pressed={kind === v} onClick={() => setKind(v)}>{l}</button>)}</div>
        <div className="flex flex-wrap gap-2">
          {[["", "Any time"], ["24h", "24 hours"], ["7d", "7 days"]].map(([v, l]) => <button key={l} className="chip" aria-pressed={window === v} onClick={() => setWindow(v)}>{l}</button>)}
          <span className="mx-2 w-px bg-rule" />
          {[["", "Anywhere"], ["PH", "Philippines"], ["INTL", "International"]].map(([v, l]) => <button key={l} className="chip" aria-pressed={region === v} onClick={() => setRegion(v)}>{l}</button>)}
          <span className="mx-2 w-px bg-rule" />
          {[["relevance", "Relevance"], ["recent", "Most recent"], ["popularity", "Popularity"]].map(([v, l]) => <button key={v} className="chip" aria-pressed={sort === v} onClick={() => setSort(v)}>{l}</button>)}
        </div>
      </div>
      {error && <ErrorBox msg={error} />}
      {loading ? <Loading /> : data && (
        <>
          {data.topics.length > 0 && <><h2 className="mb-3 text-2xl">Related topics</h2><TopicIndex topics={data.topics} /><div className="h-8" /></>}
          <p className="tick mb-2">{data.total} results</p>
          {data.total === 0 ? <Empty>Nothing matched. Try fewer words or remove a filter.</Empty> : <ItemList items={data.items} />}
        </>
      )}
    </>
  );
}
