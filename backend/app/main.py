import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes import router
from .config import settings
from .db import Base, SessionLocal, engine, ensure_compatibility_schema
from .services.seed import seed

logging.basicConfig(level=logging.INFO, format='{"t":"%(asctime)s","lvl":"%(levelname)s","log":"%(name)s","msg":"%(message)s"}')

if settings.sentry_dsn:
    import sentry_sdk
    sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.1)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)  # dev convenience. Production uses Alembic migrations.
    ensure_compatibility_schema()
    with SessionLocal() as db:
        seed(db)
    yield


app = FastAPI(title="PULSE API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
                   allow_methods=["GET", "POST", "DELETE"], allow_headers=["*"])

_hits: dict[str, deque] = defaultdict(deque)
LIMIT, WINDOW = 120, 60  # per IP per minute. Swap for Redis-backed limiter when running multiple instances.


@app.middleware("http")
async def rate_limit_and_cache(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    q, t = _hits[ip], time.time()
    while q and q[0] < t - WINDOW:
        q.popleft()
    if len(q) >= LIMIT and not request.url.path.endswith("/stream"):
        return JSONResponse({"detail": "rate limit"}, status_code=429, headers={"Retry-After": "30"})
    q.append(t)
    resp = await call_next(request)
    if request.method == "GET" and request.url.path.startswith("/api") and not request.url.path.endswith("/stream"):
        resp.headers.setdefault("Cache-Control", "public, max-age=30")
    return resp


app.include_router(router)
