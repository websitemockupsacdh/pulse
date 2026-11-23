import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { useApi } from "../lib/api";
import type { SourceInfo } from "../lib/types";
import { ago } from "../lib/format";

const NAV: [string, string][] = [
  ["/", "Home"], ["/trending", "Trending"], ["/news", "News"], ["/social", "Social Radar"], ["/videos", "Videos & Live"],
  ["/sports", "Sports"], ["/weather", "Weather & Disasters"], ["/science", "Science & Tech"], ["/entertainment", "Entertainment"], ["/search", "Search"],
];
const MORE: [string, string][] = [
  ["/business", "Business & Economy"], ["/gaming", "Gaming"], ["/international", "International Affairs"],
  ["/education", "Education"], ["/lifestyle", "Lifestyle"], ["/environment", "Environment"],
];

export default function Layout() {
  const { pathname } = useLocation();
  useEffect(() => { window.scrollTo(0, 0); }, [pathname]);
  return (
    <div className="mx-auto max-w-[1200px] px-5 md:px-8">
      <a href="#main" className="sr-only focus:not-sr-only">Skip to content</a>
      <header className="flex flex-wrap items-baseline gap-x-8 gap-y-3 py-5">
        <Link to="/" className="font-serif text-3xl tracking-tightest">pulse.</Link>
        <nav aria-label="Primary" className="-mx-1 flex min-w-0 flex-1 gap-1 overflow-x-auto text-sm font-medium md:flex-wrap md:overflow-visible">
          {NAV.map(([to, label]) => (
            <NavLink key={to} to={to} end={to === "/"}
              className={({ isActive }) => `whitespace-nowrap px-2 py-1 ${isActive ? "border-b-2 border-clay text-clay" : "hover:underline"}`}>
              {label}
            </NavLink>
          ))}
        </nav>
        <span className="tick hidden lg:inline">Philippines · No sign-in needed</span>
      </header>
      <main id="main" className="min-h-[70vh]"><Outlet /></main>
      <Footer />
    </div>
  );
}

function Footer() {
  const { data } = useApi<SourceInfo[]>("/sources");
  const on = data?.filter((s) => s.enabled) ?? [];
  return (
    <footer className="mt-16 border-t rule py-10 text-sm">
      <div className="grid gap-10 md:grid-cols-3">
        <div>
          <p className="font-serif text-2xl tracking-tightest">pulse.</p>
          <p className="mt-3 max-w-xs text-muted">An index of public information. We link to originals, show snippets only, and never copy full articles. We are not a social network and ask for no account.</p>
        </div>
        <div>
          <h3 className="tick mb-3 !font-mono">More topics</h3>
          <ul className="space-y-1.5">{MORE.map(([to, l]) => <li key={to}><Link className="hover:underline" to={to}>{l}</Link></li>)}</ul>
        </div>
        <div>
          <h3 className="tick mb-3">Sources ({on.length} active)</h3>
          <ul className="space-y-1.5 font-mono text-xs">
            {(data ?? []).map((s) => (
              <li key={s.slug} className={s.enabled ? "" : "text-muted"} title={s.last_status}>
                {s.name} <span className="text-muted">{s.enabled ? (s.last_run_at ? `· ${ago(s.last_run_at)}` : "· pending") : "· not connected"}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <p className="mt-10 border-t rule pt-5 text-xs text-muted">
        Summaries written by AI are labelled and cite their sources. Official weather and disaster warnings always come from the issuing agency, never from a summary. Publisher content belongs to its publishers.
      </p>
    </footer>
  );
}
