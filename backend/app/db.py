from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

def _normalize(url: str) -> str:
    """Accept the URL exactly as Neon/Supabase/Vercel Postgres show it."""
    for old in ("postgres://", "postgresql://"):
        if url.startswith(old):
            return "postgresql+psycopg://" + url[len(old):]
    return url


DB_URL = _normalize(settings.database_url)
_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, connect_args=_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def ensure_compatibility_schema() -> None:
    """Apply the additive item-image change for existing deployments without Alembic yet."""
    columns = {column["name"] for column in inspect(engine).get_columns("items")}
    if "image_url" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE items ADD COLUMN image_url VARCHAR(1024)"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
