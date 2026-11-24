import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { useEffect } from "react";
import Notifications from "./Notifications";

const NAV: [string, string][] = [
  ["/", "Home"], ["/trending", "Trending"], ["/news", "News"], ["/sports", "Sports"],
  ["/weather", "Weather"], ["/science", "Science + Tech"], ["/entertainment", "Showbiz"],
  ["/kpop", "K-pop"], ["/jpop", "J-pop"], ["/ppop", "P-pop"], ["/prc", "PRC"],
  ["/business", "Business"], ["/gaming", "Gaming"], ["/international", "World"],
  ["/education", "Education"], ["/lifestyle", "Lifestyle"], ["/environment", "Environment"],
  ["/search", "Search"],
];

export default function Layout() {
  const { pathname } = useLocation();
  useEffect(() => { document.getElementById("main")?.scrollTo(0, 0); }, [pathname]);
  return (
    <div className="mx-auto flex h-dvh w-full max-w-[1500px] flex-col overflow-hidden px-3 md:px-6">
      <a href="#main" className="sr-only focus:not-sr-only">Skip to content</a>
      <header className="glass-shell flex shrink-0 items-center gap-3 border-b rule py-3 md:gap-5">
        <Link to="/" className="shrink-0 font-serif text-3xl tracking-tightest">pulse.</Link>
        <nav aria-label="Primary" className="nav-scroll flex min-w-0 flex-1 gap-1 overflow-x-auto text-sm font-medium md:flex-wrap md:overflow-visible">
          {NAV.map(([to, label]) => (
            <NavLink key={to} to={to} end={to === "/"}
              className={({ isActive }) => `whitespace-nowrap rounded-lg px-2.5 py-2 transition-colors ${isActive ? "bg-white/70 text-clay" : "hover:bg-white/50"}`}>
              {label}
            </NavLink>
          ))}
        </nav>
        <Notifications />
      </header>
      <main id="main" tabIndex={-1} className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-1 pb-5">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

function Footer() {
  return (
    <footer className="glass-shell flex shrink-0 flex-wrap items-center justify-between gap-x-4 gap-y-2 border-t rule py-2.5 text-xs">
      <div className="flex items-center gap-2">
        <span className="flex h-8 items-center rounded-md bg-slate-900 px-1.5">
          <img src="acdhlogo.png" alt="ACDH Creatives" className="h-6 w-auto max-w-[78px] object-contain" />
        </span>
        <span>Created by <strong>ACDH Creatives</strong></span>
      </div>
      <nav aria-label="ACDH Creatives links" className="flex flex-wrap items-center gap-x-4 gap-y-1">
        <a className="hover:underline" href="https://www.facebook.com/acdh.creatives" target="_blank" rel="noopener noreferrer">Facebook</a>
        <a className="hover:underline" href="mailto:acdh.creatives@gmail.com">Email</a>
        <a className="hover:underline" href="https://acdhcreatives.vercel.app/" target="_blank" rel="noopener noreferrer">Website</a>
      </nav>
      <span className="hidden text-muted lg:block">Publisher links only · No sign-in needed</span>
    </footer>
  );
}
