import hashlib
import re
from urllib.parse import urlsplit, urlunsplit

STOP = set("""a an the of in on at to for and or but is are was were be been with by from as that this it its
after before over under about into than then their his her they he she we you i not no new says say said
ng sa na ang mga at para si ni kay ay ito may ang""".split())


def canonical_url(url: str) -> str:
    p = urlsplit(url.strip())
    return urlunsplit((p.scheme.lower(), p.netloc.lower().removeprefix("www."), p.path.rstrip("/"), "", ""))


def url_hash(url: str) -> str:
    return hashlib.sha256(canonical_url(url).encode()).hexdigest()


def tokens(title: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", title.lower()) if w not in STOP and len(w) > 2}


def title_fp(title: str) -> str:
    return hashlib.sha1(" ".join(sorted(tokens(title))).encode()).hexdigest()


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def slugify(title: str) -> str:
    return "-".join(re.findall(r"[a-z0-9]+", title.lower())[:8]) or "topic"
