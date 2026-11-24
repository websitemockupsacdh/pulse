import { ErrorBox, ItemList, Loading, PageHead, Section } from "../components/ui";
import { useApi } from "../lib/api";
import { stamp } from "../lib/format";
import type { Item } from "../lib/types";

export default function Weather() {
  const { data, error, loading } = useApi<Item[]>("/feed", { category: "weather", limit: "60" });
  const official = (data ?? []).filter((i) => i.kind === "official");
  const news = (data ?? []).filter((i) => i.kind !== "official");
  return (
    <>
      <PageHead title="Weather & Disasters" lede="Official bulletins come first and are shown exactly as the issuing agency published them. Summaries never override a warning." />
      <p className="mb-2 border-l-2 border-clay bg-stone p-4 text-sm">For safety decisions, use the agency pages: PAGASA for weather and cyclones, PHIVOLCS for earthquakes and volcanoes, NDRRMC for emergency response.</p>
      {error && <ErrorBox msg={error} />}
      {loading ? <Loading /> : (
        <>
          <Section title="Official advisories">
            {official.length ? (
              <ul className="grid gap-3">
                {official.map((i) => (
                  <li key={i.id} className={`glass-card grid gap-3 rounded-2xl p-3 sm:p-4 ${i.image_url ? "sm:grid-cols-[12rem_minmax(0,1fr)]" : "md:grid-cols-[10rem_minmax(0,1fr)]"}`}>
                    {i.image_url && <a href={i.url} target="_blank" rel="noopener noreferrer" aria-label={`Open ${i.title}`}>
                      <img src={i.image_url} alt="" loading="lazy" referrerPolicy="no-referrer" className="preview-image"
                        onError={(event) => { if (event.currentTarget.parentElement) event.currentTarget.parentElement.style.display = "none"; }} />
                    </a>}
                    <div className="font-mono text-xs">
                      <p className="font-semibold">{i.publisher}</p><p className="text-muted">Published {stamp(i.published_at)}</p>
                      {i.severity && <p className="mt-1">{i.severity}</p>}
                      <a href={i.url} target="_blank" rel="noopener noreferrer" className="mt-2 block font-serif text-xl tracking-tightest text-ink hover:underline">{i.title}</a>
                      {i.snippet && <p className="mt-2 text-sm text-muted">{i.snippet}</p>}
                    </div>
                  </li>
                ))}
              </ul>
            ) : <p className="border border-dashed rule p-6 text-sm text-muted">No official bulletin has been collected yet. Check PAGASA, PHIVOLCS and NDRRMC directly for urgent or safety-critical information.</p>}
          </Section>
          <Section title="Related news coverage"><ItemList items={news} /></Section>
        </>
      )}
    </>
  );
}
