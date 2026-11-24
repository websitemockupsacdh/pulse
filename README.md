# PULSE

Public trend discovery for the Philippines. React + Vite + TS + Tailwind frontend, FastAPI backend.

## Run locally
    cd backend && pip install -r requirements.txt && cp .env.example .env
    python -m app.cli run-once        # collect from enabled sources, cluster, score
    python -m app.cli seed-demo       # DEV ONLY: labeled sample data when offline
    uvicorn app.main:app --reload
    cd ../frontend && npm install && npm run dev   # proxies /api to :8000

Vercel: see DEPLOY.md. Self-hosted: set `VITE_API_BASE`, `DATABASE_URL` (Postgres), `REDIS_URL`; run `celery -A app.tasks worker -B`.

## Architecture
- `connectors/`: one class per source type. RSS sources can discover a publisher's declared feed from the configured page. Publishers and curated topic feeds are rows in `sources`, not code.
- `services/pipeline.py`: validate, canonical-URL dedup, store. `trends.py`: cross-source clustering, velocity, status via env thresholds.
- `services/search.py`: indexed retrieval first (SQL now, OpenSearch via `OPENSEARCH_URL` later). AI expansion comes after.
- `GET /api/home` returns layout from the `page_sections` table. `/api/stream` is SSE.
- Missing engagement is `null`, shown as "Not provided by source", never 0.
- Reader-selected web push alerts match new items by topic category or keyword. Configure `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, and `VAPID_SUBJECT`; push delivery requires HTTPS and browser push support.
- Images are shown as publisher-provided feed previews when an RSS item supplies an image. The original article remains the link target.

## Not done yet (honest list)
- Publisher home/category pages in `seed.py` are checked for declared RSS/Atom feeds at collection time. Some sites (including social-only pages) may not publish a machine-readable feed; check `/api/sources` and disable any source that reports an error.
- Set up a matching VAPID key pair before enabling browser push notifications. iOS requires the installed Home Screen web app for push.
- AI briefing, conflict detection, query expansion: endpoints and UI slots exist, no model wired. Briefings must cite sources.
- Alembic migrations, OpenSearch backend, Redis rate limiter/cache, and the AI briefing layer.
