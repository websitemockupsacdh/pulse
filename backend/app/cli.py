"""python -m app.cli ingest | refresh | check-sources | seed-demo | run-once"""
import sys

from sqlalchemy import select

from .db import Base, SessionLocal, engine
from .models import Source
from .services.pipeline import ingest_all
from .services.seed import seed
from .services.trends import refresh_topics


def main(cmd: str) -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
        if cmd in ("ingest", "run-once"):
            print(ingest_all(db))
        if cmd in ("refresh", "run-once"):
            print("topics refreshed:", refresh_topics(db))
        if cmd == "seed-demo":
            from .services.demo import seed_demo
            seed_demo(db); print("demo data loaded (dev only)")
        if cmd == "check-sources":
            for s in db.scalars(select(Source)):
                print(f"{s.slug:12} enabled={s.enabled!s:5} {s.last_status}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "run-once")
