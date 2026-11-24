"""
Fetch every enabled source in sources.py and write one normalized JSON file.

Run from the backend/ folder:
    python -m trending.run --out ../frontend/public/trending.json

Standard library only, so it adds nothing to requirements.txt.
Every item: {title, url, source, sourceId, category, region, rank, extra, fetchedAt}
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from .sources import SOURCES

UA = "PulseTrendingBot/0.1 (+https://github.com/websitemockupsacdh/pulse)"
TIMEOUT = 15


def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def http_json(url: str):
    return json.loads(http_get(url).decode("utf-8"))


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _text(el, name: str) -> str:
    for c in el:
        if _local(c.tag) == name and c.text:
            return c.text.strip()
    return ""


def make(src, rank, title, url, extra=None):
    return {
        "title": title, "url": url, "source": src["name"], "sourceId": src["id"],
        "category": src["category"], "region": src["region"], "rank": rank,
        "extra": extra or {},
    }


# ---------- fetchers: each returns a list of items ----------

def fetch_rss(src):
    root = ET.fromstring(http_get(src["url"]))
    out = []
    # RSS 2.0 <item> or Atom <entry>
    entries = [e for e in root.iter() if _local(e.tag) in ("item", "entry")]
    for i, e in enumerate(entries[: src["limit"]], 1):
        title = _text(e, "title")
        link = _text(e, "link")
        if not link:  # Atom stores the link in an attribute
            for c in e:
                if _local(c.tag) == "link" and c.get("href"):
                    link = c.get("href")
                    break
        if title and link:
            out.append(make(src, i, title, link, {"published": _text(e, "pubDate") or _text(e, "updated")}))
    return out


def fetch_google_trends(src):
    root = ET.fromstring(http_get(src["url"]))
    out = []
    for i, e in enumerate([e for e in root.iter() if _local(e.tag) == "item"][: src["limit"]], 1):
        title = _text(e, "title")
        traffic = _text(e, "approx_traffic")
        link = "https://www.google.com/search?q=" + urllib.parse.quote_plus(title)
        if title:
            out.append(make(src, i, title, link, {"traffic": traffic}))
    return out


def fetch_wikipedia(src):
    # Yesterday (UTC): today's totals are not published yet.
    d = datetime.now(timezone.utc) - timedelta(days=1)
    url = (f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/"
           f"{src['project']}/all-access/{d:%Y/%m/%d}")
    articles = http_json(url)["items"][0]["articles"]
    host = src["project"] + ".org"
    out, rank = [], 0
    for a in articles:
        name = a["article"]
        if name == "Main_Page" or ":" in name:  # skip Special:, Wikipedia:, etc.
            continue
        rank += 1
        out.append(make(src, rank, name.replace("_", " "), f"https://{host}/wiki/{name}", {"views": a["views"]}))
        if rank >= src["limit"]:
            break
    return out


def fetch_reddit(src):
    url = f"https://www.reddit.com/r/{src['subreddit']}/hot.json?limit=30&raw_json=1"
    posts = http_json(url)["data"]["children"]
    out, rank = [], 0
    for p in posts:
        d = p["data"]
        if d.get("stickied"):
            continue
        rank += 1
        out.append(make(src, rank, d["title"], "https://www.reddit.com" + d["permalink"],
                        {"score": d.get("score"), "comments": d.get("num_comments")}))
        if rank >= src["limit"]:
            break
    return out


def fetch_usgs(src):
    feats = http_json(src["url"])["features"]
    needle = src.get("contains", "").lower()
    out, rank = [], 0
    for f in feats:
        p = f["properties"]
        if needle and needle not in (p.get("place") or "").lower():
            continue
        rank += 1
        out.append(make(src, rank, f"M{p['mag']} - {p['place']}", p["url"], {"mag": p["mag"], "time": p["time"]}))
        if rank >= src["limit"]:
            break
    return out


def fetch_fx(src):
    data = http_json(src["url"])
    rate = data["rates"][src["quote"]]
    title = f"{src['base']}/{src['quote']} {rate:.2f}"
    return [make(src, 1, title, "https://www.bsp.gov.ph/", {"rate": rate})]


FETCHERS = {
    "rss": fetch_rss, "google_trends": fetch_google_trends, "wikipedia": fetch_wikipedia,
    "reddit": fetch_reddit, "usgs": fetch_usgs, "fx": fetch_fx,
}


def run_one(src):
    if src.get("enabled", True) is False:
        return src, [], "disabled"
    try:
        return src, FETCHERS[src["type"]](src), "ok"
    except Exception as e:  # one bad source must never break the rest
        print(f"[trending] {src['id']} failed: {e}", file=sys.stderr)
        return src, [], f"error: {type(e).__name__}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="trending.json")
    args = ap.parse_args()

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(run_one, SOURCES))

    items, status = [], []
    for src, got, st in results:
        for it in got:
            it["fetchedAt"] = now
        items.extend(got)
        status.append({"id": src["id"], "name": src["name"], "category": src["category"],
                       "region": src["region"], "status": st, "count": len(got)})

    # Never overwrite a good file with an empty one.
    if not items:
        print("[trending] nothing fetched; leaving existing file untouched", file=sys.stderr)
        sys.exit(1)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"generatedAt": now, "sources": status, "items": items}, f, ensure_ascii=False, indent=1)
    print(f"[trending] wrote {len(items)} items from {sum(s['status']=='ok' for s in status)}/{len(status)} sources -> {args.out}")


if __name__ == "__main__":
    main()
