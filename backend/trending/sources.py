"""
THE ONE FILE TO EDIT.
Add, remove or disable a feed by changing a line here.

type: rss | google_trends | wikipedia | reddit | usgs | fx
region: "PH" or "INTL"
limit: max items kept from that source

NOTE: feed URLs below are from memory and untested. A feed that fails is
skipped and reported as status "error" in the output; it never breaks the rest.
"""

SOURCES = [
    # --- Search / attention (no account, no key) ---
    {"id": "gtrends-ph", "name": "Google Trends PH", "type": "google_trends",
     "category": "trending", "region": "PH", "url": "https://trends.google.com/trending/rss?geo=PH", "limit": 20},
    {"id": "wiki-en", "name": "Wikipedia (EN) most viewed", "type": "wikipedia",
     "category": "trending", "region": "INTL", "project": "en.wikipedia", "limit": 15},
    {"id": "wiki-tl", "name": "Wikipedia (TL) most viewed", "type": "wikipedia",
     "category": "trending", "region": "PH", "project": "tl.wikipedia", "limit": 10},

    # --- Social (public pages only; no logins) ---
    {"id": "reddit-ph", "name": "r/Philippines", "type": "reddit",
     "category": "social", "region": "PH", "subreddit": "Philippines", "limit": 15},
    {"id": "reddit-popular", "name": "Reddit r/popular", "type": "reddit",
     "category": "social", "region": "INTL", "subreddit": "popular", "limit": 15},
    {"id": "reddit-chikaph", "name": "r/ChikaPH", "type": "reddit",
     "category": "social", "region": "PH", "subreddit": "ChikaPH", "limit": 10},
    # X, Facebook, Instagram, Threads: no public keyless feed. Not included on purpose.
    # Culture outlets stand in for them (see the "culture" category below).

    # --- News ---
    {"id": "bbc", "name": "BBC News", "type": "rss", "category": "news", "region": "INTL",
     "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "limit": 10},
    {"id": "aljazeera", "name": "Al Jazeera", "type": "rss", "category": "news", "region": "INTL",
     "url": "https://www.aljazeera.com/xml/rss/all.xml", "limit": 10},
    {"id": "gma", "name": "GMA News", "type": "rss", "category": "news", "region": "PH",
     "url": "https://data.gmanetwork.com/gno/rss/news/feed.xml", "limit": 10},
    {"id": "inquirer", "name": "Inquirer.net", "type": "rss", "category": "news", "region": "PH",
     "url": "https://www.inquirer.net/fullfeed", "limit": 10},
    {"id": "philstar", "name": "Philstar", "type": "rss", "category": "news", "region": "PH",
     "url": "https://www.philstar.com/rss/headlines", "limit": 10},
    {"id": "rappler", "name": "Rappler", "type": "rss", "category": "news", "region": "PH",
     "url": "https://www.rappler.com/feed/", "limit": 10},

    # --- Sports ---
    {"id": "espn", "name": "ESPN", "type": "rss", "category": "sports", "region": "INTL",
     "url": "https://www.espn.com/espn/rss/news", "limit": 10},

    # --- Weather and disaster ---
    {"id": "usgs-ph", "name": "USGS Earthquakes (PH area)", "type": "usgs", "category": "disaster", "region": "PH",
     "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson",
     "contains": "Philippines", "limit": 10},
    # PAGASA / PHIVOLCS: no clean feed. Add later as a scrape type if wanted.

    # --- Currency ---
    {"id": "fx-usd-php", "name": "USD/PHP", "type": "fx", "category": "currency", "region": "PH",
     "url": "https://open.er-api.com/v6/latest/USD", "base": "USD", "quote": "PHP", "limit": 1},

    # --- Science and tech ---
    {"id": "verge", "name": "The Verge", "type": "rss", "category": "tech", "region": "INTL",
     "url": "https://www.theverge.com/rss/index.xml", "limit": 8},
    {"id": "techcrunch", "name": "TechCrunch", "type": "rss", "category": "tech", "region": "INTL",
     "url": "https://techcrunch.com/feed/", "limit": 8},
    {"id": "ars", "name": "Ars Technica", "type": "rss", "category": "tech", "region": "INTL",
     "url": "https://feeds.arstechnica.com/arstechnica/index", "limit": 8},

    # --- Entertainment ---
    {"id": "variety", "name": "Variety", "type": "rss", "category": "entertainment", "region": "INTL",
     "url": "https://variety.com/feed/", "limit": 8},

    # --- Culture (stand-in for social trend journalism) ---
    # Add feeds here (e.g. Know Your Meme, Mashable, Spot.ph) once you confirm their URLs.
]
