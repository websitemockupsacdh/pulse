# Deploy on Vercel

Repo root must contain `vercel.json`, `backend/`, `frontend/`.

## Environment variables (Vercel > Settings > Environment Variables)
| Name | Value |
|---|---|
| DATABASE_URL | Postgres URL from Neon/Supabase (any `postgres://` or `postgresql://` form works) |
| CRON_SECRET | Any long random string you make up |
| VAPID_PUBLIC_KEY | Public key from your web-push VAPID key pair |
| VAPID_PRIVATE_KEY | Matching private VAPID key (keep secret) |
| VAPID_SUBJECT | Contact URI, e.g. `mailto:admin@example.com` |
| SENTRY_DSN | Optional |

## Scheduler (GitHub > Settings > Secrets and variables > Actions)
- APP_URL = your Vercel URL, no trailing slash
- CRON_SECRET = same value as on Vercel
Then Actions > ingest > Run workflow once to fill the database.

## Check
- `/api/health` returns {"ok": true}
- `/api/sources` shows each source's last_status. Fix or disable any that say "error".
- Push alerts require HTTPS, a valid matching VAPID key pair, and permission on each reader's device. On iOS, readers must add the site to their Home Screen.
