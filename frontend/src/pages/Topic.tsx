import { Link, useParams } from "react-router-dom";
import { Empty, ErrorBox, ItemList, Loading, Section, StatusTag, TopicIndex } from "../components/ui";
import { useApi } from "../lib/api";
import { ago, stamp } from "../lib/format";
import type { Explorer } from "../lib/types";

export default function TopicPage() {
  const { slug } = useParams();
  const { data: d, error, loading } = useApi<Explorer>(`/topics/${slug}`);
  if (error) return <div className="py-10"><ErrorBox msg={error} /></div>;
  if (loading || !d) return <Loading />;
  const t = d.topic;
  return (
    <article>
      <header className="pb-8 pt-10">
        <div className="flex items-center gap-3"><StatusTag status={t.status} /><span className="tick">{t.category} · {t.region}</span></div>
        <h1 className="mt-3 max-w-4xl text-4xl md:text-6xl">{t.title}</h1>
        <dl className="mt-6 grid max-w-2xl grid-cols-2 gap-y-2 font-mono text-xs md:grid-cols-4">
          <div><dt className="text-muted">First detected</dt><dd>{ago(t.first_detected_at)}</dd></div>
          <div><dt className="text-muted">Updated</dt><dd>{ago(t.last_updated_at)}</dd></div>
          <div><dt className="text-muted">Items</dt><dd>{t.item_count}</dd></div>
          <div><dt className="text-muted">Publishers</dt><dd>{t.source_count}</dd></div>
        </dl>
      </header>

      <Section title="AI briefing">
        {d.briefing.text ? (
          <div className="max-w-2xl"><p className="text-lg">{d.briefing.text}</p>
            <p className="tick mt-3">AI-written. Check the sources below.</p>
            <ul className="mt-2 text-sm">{d.briefing.citations.map((c) => <li key={c}><a className="underline" href={c} target="_blank" rel="noopener noreferrer">{c}</a></li>)}</ul></div>
        ) : <Empty>{d.briefing.note}</Empty>}
      </Section>

      <Section title="Timeline of developments">
        {d.timeline.length ? (
          <ol className="border-l rule">
            {d.timeline.map((e) => (
              <li key={e.url} className="relative pb-5 pl-6">
                <span className="absolute -left-[5px] top-2 h-2.5 w-2.5 bg-ink" aria-hidden />
                <p className="tick">{stamp(e.at)} · {e.publisher}</p>
                <a href={e.url} target="_blank" rel="noopener noreferrer" className="font-serif text-lg tracking-tightest hover:underline">{e.title}</a>
              </li>
            ))}
          </ol>
        ) : <Empty>No items yet.</Empty>}
      </Section>

      <Section title="Official statements"><ItemList items={d.official} empty="No official statement collected for this topic." /></Section>
      <Section title="Related Philippine news"><ItemList items={d.ph_news} /></Section>
      <Section title="International coverage"><ItemList items={d.international} empty="No international coverage collected." /></Section>
      <Section title="Conflicting reports and unresolved claims">
        {d.conflicts.length ? <ul>{d.conflicts.map((c) => <li key={c.claim}>{c.claim}</li>)}</ul> :
          <Empty>No conflicts have been identified. This does not confirm that the sources agree. It means the comparison step has not flagged a difference.</Empty>}
      </Section>
      <Section title="Related topics">{d.related_topics.length ? <TopicIndex topics={d.related_topics} /> : <Empty>No related topics found.</Empty>}</Section>
      <Section title="Original source directory">
        <ul className="font-mono text-xs">{d.sources.map(([n, u]) => <li key={u} className="border-b rule py-2"><span className="mr-3 text-muted">{n}</span><a href={u} className="underline" target="_blank" rel="noopener noreferrer">{u}</a></li>)}</ul>
        <p className="mt-6"><Link to="/trending" className="btn-quiet">Back to trending</Link></p>
      </Section>
    </article>
  );
}
