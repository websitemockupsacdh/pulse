import { ExternalLink } from "lucide-react";
import { Link } from "react-router-dom";
import { ago, num, stamp } from "../lib/format";
import type { Item, Topic } from "../lib/types";

export function Section({ title, children, aside }: { title: string; children: React.ReactNode; aside?: React.ReactNode }) {
  return (
    <section className="border-t rule py-8">
      <div className="mb-5 flex items-baseline justify-between gap-4">
        <h2 className="text-2xl md:text-3xl">{title}</h2>
        {aside}
      </div>
      {children}
    </section>
  );
}

export function PageHead({ title, lede }: { title: string; lede?: string }) {
  return (
    <header className="pb-8 pt-10">
      <h1 className="max-w-3xl text-4xl md:text-6xl">{title}</h1>
      {lede && <p className="mt-4 max-w-2xl text-lg text-muted">{lede}</p>}
    </header>
  );
}

export const Unavailable = ({ what = "Not provided by source" }: { what?: string }) => (
  <span className="font-mono text-xs text-muted" title="The platform did not supply this value">{what}</span>
);

const STATUS: Record<string, string> = {
  emerging: "border-ink text-ink", rising: "border-clay text-clay", active: "border-rule text-ink",
  declining: "border-rule text-muted", archived: "border-rule text-muted",
};
export const StatusTag = ({ status }: { status: Topic["status"] }) => (
  <span className={`border px-1.5 py-0.5 font-mono text-[11px] uppercase tracking-wider ${STATUS[status]}`}>{status}</span>
);

export const LiveTag = ({ s }: { s: Item["live_status"] }) =>
  s ? <span className="border border-ink px-1.5 py-0.5 font-mono text-[11px] uppercase tracking-wider">{s === "live" ? "Live now" : s}</span> : null;

export function Empty({ children }: { children: React.ReactNode }) {
  return <p className="border border-dashed rule p-6 text-sm text-muted">{children}</p>;
}
export const Loading = () => <p className="py-10 font-mono text-sm text-muted" role="status">Loading</p>;
export const ErrorBox = ({ msg }: { msg: string }) => (
  <p className="border border-clay p-4 text-sm" role="alert">Could not load this page. {msg}. The API may be offline.</p>
);

/** One row: headline links out to the original. Attribution is always present. */
export function ItemRow({ it, showEngagement }: { it: Item; showEngagement?: boolean }) {
  const views = it.engagement?.viewCount ?? it.engagement?.score;
  return (
    <li className="grid gap-1 border-b rule py-4 md:grid-cols-[1fr_auto] md:gap-8">
      <div>
        <div className="mb-1 flex flex-wrap items-center gap-2 tick">
          <span>{it.publisher}</span><span>·</span><time dateTime={it.published_at}>{ago(it.published_at)}</time>
          {it.syndicated && <span>· Syndicated</span>}
          {it.severity && <span>· {it.severity}</span>}
          <LiveTag s={it.live_status} />
        </div>
        <a href={it.url} target="_blank" rel="noopener noreferrer" className="group font-serif text-xl leading-snug tracking-tightest hover:underline">
          {it.title}<ExternalLink aria-label="opens original" className="ml-1.5 inline h-3.5 w-3.5 text-muted" />
        </a>
        {it.snippet && <p className="mt-1 max-w-2xl text-sm text-muted">{it.snippet}</p>}
        <p className="mt-1 text-xs text-muted" title={stamp(it.published_at)}>
          {it.author && <>By {it.author}. </>}Read the full item at {it.publisher}.
        </p>
      </div>
      {showEngagement && (
        <div className="font-mono text-xs md:text-right">
          {it.engagement ? <>{num(views ?? 0)} {it.engagement.viewCount != null ? "views" : "points"}</> : <Unavailable />}
        </div>
      )}
    </li>
  );
}

export function ItemList({ items, showEngagement, empty }: { items: Item[]; showEngagement?: boolean; empty?: string }) {
  if (!items.length) return <Empty>{empty ?? "No items collected for this view yet."}</Empty>;
  return <ul className="border-t rule">{items.map((i) => <ItemRow key={i.id} it={i} showEngagement={showEngagement} />)}</ul>;
}

/** Monospace index table with a hover preview. Same pattern as an editorial catalog index. */
export function TopicIndex({ topics, onHover }: { topics: Topic[]; onHover?: (t: Topic | null) => void }) {
  if (!topics.length) return <Empty>No topics detected yet. Topics appear after the first collection run.</Empty>;
  return (
    <div role="table" className="font-mono text-[13px]">
      <div role="row" className="hidden grid-cols-[3rem_1fr_7rem_5rem_5rem_6rem] gap-3 border-y rule py-2 tick md:grid">
        <span>#</span><span>Topic</span><span>Category</span><span>Items</span><span>Sources</span><span>Status</span>
      </div>
      {topics.map((t, i) => (
        <Link role="row" key={t.slug} to={`/topic/${t.slug}`} onMouseEnter={() => onHover?.(t)} onFocus={() => onHover?.(t)}
          className="grid grid-cols-[1fr_auto] gap-x-3 border-b rule py-3 hover:bg-stone md:grid-cols-[3rem_1fr_7rem_5rem_5rem_6rem] md:items-baseline">
          <span className="hidden text-muted md:block">{String(i + 1).padStart(2, "0")}</span>
          <span className="font-serif text-lg tracking-tightest text-ink md:text-xl">{t.title}</span>
          <span className="hidden capitalize text-muted md:block">{t.category}</span>
          <span className="hidden md:block">{t.item_count}</span>
          <span className="hidden md:block">{t.source_count}</span>
          <span className="justify-self-end"><StatusTag status={t.status} /></span>
        </Link>
      ))}
    </div>
  );
}

export function TopicPreview({ t }: { t: Topic | null }) {
  if (!t) return <div className="border rule p-6 text-sm text-muted">Hover a topic to preview it.</div>;
  return (
    <aside className="sticky top-6 border rule bg-stone p-6" aria-live="polite">
      <p className="tick">First detected {ago(t.first_detected_at)}</p>
      <h3 className="mt-2 text-2xl">{t.title}</h3>
      <dl className="mt-5 grid grid-cols-2 gap-y-3 font-mono text-xs">
        <dt className="text-muted">Velocity</dt><dd>{t.velocity.toFixed(2)} items/h</dd>
        <dt className="text-muted">Source diversity</dt><dd>{t.source_count} publishers</dd>
        <dt className="text-muted">Items</dt><dd>{t.item_count}</dd>
        <dt className="text-muted">Last updated</dt><dd>{ago(t.last_updated_at)}</dd>
      </dl>
      <Link to={`/topic/${t.slug}`} className="btn mt-6">Open topic page</Link>
    </aside>
  );
}
