# PULSE

Public trend discovery for the Philippines. React + Vite + TS + Tailwind frontend, FastAPI backend.

## Run locally
    cd backend && pip install -r requirements.txt && cp .env.example .env
    python -m app.cli run-once        # collect from enabled sources, cluster, score
    python -m app.cli seed-demo       # DEV ONLY: labeled sample data when offline
    uvicorn app.main:app --reload
    cd ../frontend && npm install && npm run dev   # proxies /api to :8000

Production: set `VITE_API_BASE`, `DATABASE_URL` (Postgres), `REDIS_URL`; run `celery -A app.tasks worker -B`.

## Architecture
- `connectors/`: one class per source type (rss, youtube, reddit, social_unavailable). Register in `registry.py`. Publishers are rows in `sources`, not code.
- `services/pipeline.py`: validate, canonical-URL dedup, store. `trends.py`: cross-source clustering, velocity, status via env thresholds.
- `services/search.py`: indexed retrieval first (SQL now, OpenSearch via `OPENSEARCH_URL` later). AI expansion comes after.
- `GET /api/home` returns layout from the `page_sections` table. `/api/stream` is SSE.
- Missing engagement is `null`, shown as "Not provided by source", never 0.

## Not done yet (honest list)
- Feed URLs in `seed.py` are unverified (sandbox had no network). Run `python -m app.cli run-once`, then `check-sources`.
- PAGASA, PHIVOLCS, NDRRMC are registered but disabled until official feed URLs are verified.
- X, Threads, Facebook, Instagram, TikTok need authorized API access; adapters report unavailable.
- AI briefing, conflict detection, query expansion: endpoints and UI slots exist, no model wired. Briefings must cite sources.
- Alembic migrations, OpenSearch backend, Redis rate limiter/cache, YouTube embeds, sports/science sources.
