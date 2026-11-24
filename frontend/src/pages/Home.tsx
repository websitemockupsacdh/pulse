import { Search as SearchIcon } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ErrorBox, Empty, ItemList, Loading, Section, TopicIndex, TopicPreview } from "../components/ui";
import { useApi } from "../lib/api";
import { ago } from "../lib/format";
import type { Home as HomeT, HomeSection, Topic } from "../lib/types";

const REGIONS = [["PH", "Philippines"], ["INTL", "International"]];

export default function Home() {
  const [region, setRegion] = useState("PH");
  const { data, error, loading } = useApi<HomeT>("/home", { region });
  const nav = useNavigate();
  const [q, setQ] = useState("");
  const [hover, setHover] = useState<Topic | null>(null);

  const sec = (k: string) => data?.sections.find((s) => s.key === k);
  const top = sec("trending");

  return (
    <>
      <div className="grid gap-6 pb-7 pt-5 md:grid-cols-[45fr_55fr]">
        <div>
          <h1 className="text-5xl md:text-6xl">What the Philippines is talking about, with the sources attached.</h1>
          <p className="mt-4 max-w-md text-lg text-muted">News and official updates, organized by topic. Every story links to its publisher.</p>
          <form onSubmit={(e) => { e.preventDefault(); nav(`/search?q=${encodeURIComponent(q)}`); }} role="search" className="mt-8 flex max-w-md">
            <label htmlFor="q" className="sr-only">Search PULSE</label>
            <input id="q" value={q} onChange={(e) => setQ(e.target.value)} placeholder='Try: "typhoon" or artificial intelligence Philippines'
              className="min-w-0 flex-1 border border-rule bg-stone px-4 py-2.5 text-sm placeholder:text-muted" />
            <button className="btn" aria-label="Search"><SearchIcon className="h-4 w-4" />Search</button>
          </form>
          <div className="mt-4 flex gap-2" role="group" aria-label="Region">
            {REGIONS.map(([v, l]) => <button key={v} className="chip" aria-pressed={region === v} onClick={() => setRegion(v)}>{l}</button>)}
          </div>
          {data && <p className="tick mt-6">Updated {ago(data.generated_at)}</p>}
        </div>
        <div>
          <p className="tick mb-2">Top topics right now</p>
          {top?.topics ? <TopicIndex topics={top.topics.slice(0, 6)} /> : loading ? <Loading /> : null}
        </div>
      </div>

      {error && <ErrorBox msg={error} />}
      {loading && <Loading />}

      {data && (
        <>
          <BreakingStrip s={sec("breaking")} />
          <Section title="Top trending topics" aside={<Link className="text-sm underline" to="/trending">All trends</Link>}>
            <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
              <TopicIndex topics={top?.topics ?? []} onHover={setHover} />
              <div className="hidden lg:block"><TopicPreview t={hover ?? top?.topics?.[0] ?? null} /></div>
            </div>
          </Section>
          <Section title={sec("rising")?.title ?? "Fastest rising"}>
            {sec("rising")?.topics?.length ? <TopicIndex topics={sec("rising")!.topics!} /> :
              <Empty>No topic is above the rising threshold right now. Thresholds are set in the backend configuration.</Empty>}
          </Section>
          <Section title="Daily briefing">
            <Empty>The AI briefing layer is not connected. Once it is, this section will show a short summary where every statement links to the articles it came from. Nothing is summarized without a source.</Empty>
          </Section>
          {data.sections.filter((s) => !["breaking", "trending", "rising", "briefing"].includes(s.key)).map((s) => <GenericSection key={s.key} s={s} />)}
        </>
      )}
    </>
  );
}

function BreakingStrip({ s }: { s?: HomeSection }) {
  if (!s?.items?.length) return null;
  const it = s.items[0];
  return (
    <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1 border-y rule py-3">
      <span className="tick text-ink">Latest</span>
      <a href={it.url} target="_blank" rel="noopener noreferrer" className="font-serif text-lg tracking-tightest hover:underline">{it.title}</a>
      <span className="tick">{it.publisher} · {ago(it.published_at)}</span>
    </div>
  );
}

function GenericSection({ s }: { s: HomeSection }) {
  return <Section title={s.title}><ItemList items={s.items ?? []} empty="Nothing collected here yet." /></Section>;
}
