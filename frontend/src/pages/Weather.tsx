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
              <ul className="border-t rule">
                {official.map((i) => (
                  <li key={i.id} className="grid gap-2 border-b rule py-4 md:grid-cols-[10rem_1fr]">
                    <div className="font-mono text-xs"><p className="font-semibold">{i.publisher}</p><p className="text-muted">Published {stamp(i.published_at)}</p>{i.severity && <p className="mt-1">{i.severity}</p>}</div>
                    <a href={i.url} target="_blank" rel="noopener noreferrer" className="font-serif text-xl tracking-tightest hover:underline">{i.title}</a>
                  </li>
                ))}
              </ul>
            ) : <p className="border border-dashed rule p-6 text-sm text-muted">No official bulletin has been collected. PAGASA, PHIVOLCS and NDRRMC sources are registered but switched off until their feed addresses are verified. Check the agency sites directly.</p>}
          </Section>
          <Section title="Related news coverage"><ItemList items={news} /></Section>
        </>
      )}
    </>
  );
}
