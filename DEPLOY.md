# Deploy on Vercel

Repo root must contain `vercel.json`, `backend/`, `frontend/`.

## Environment variables (Vercel > Settings > Environment Variables)
| Name | Value |
|---|---|
| DATABASE_URL | Postgres URL from Neon/Supabase (any `postgres://` or `postgresql://` form works) |
| CRON_SECRET | Any long random string you make up |
| YOUTUBE_API_KEY | Google Cloud > YouTube Data API v3 > API key (optional) |
| SENTRY_DSN | Optional |

## Scheduler (GitHub > Settings > Secrets and variables > Actions)
- APP_URL = your Vercel URL, no trailing slash
- CRON_SECRET = same value as on Vercel
Then Actions > ingest > Run workflow once to fill the database.

## Check
- `/api/health` returns {"ok": true}
- `/api/sources` shows each source's last_status. Fix or disable any that say "error".
