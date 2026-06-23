from __future__ import annotations

from functools import lru_cache
from typing import Any
from urllib.parse import quote_plus

from app.config import settings
from app.services.http_utils import fetch_json


BASE_URL = "https://api.crossref.org/works"


def _headers() -> dict[str, str]:
    if settings.crossref_mailto:
        return {"User-Agent": f"BiomedDigest/1.0 (mailto:{settings.crossref_mailto})"}
    return {"User-Agent": "BiomedDigest/1.0"}


def enrich_by_doi_or_title(doi: str | None, title: str) -> dict[str, Any]:
    return dict(_enrich_cached(doi or "", title or ""))


@lru_cache(maxsize=512)
def _enrich_cached(doi: str, title: str) -> dict[str, Any]:
    if doi:
        safe_doi = quote_plus(doi)
        url = f"{BASE_URL}/{safe_doi}"
        try:
            payload = fetch_json(url, headers=_headers()).get("message", {})
            return _normalize(payload)
        except Exception:
            pass

    if not title:
        return {}

    params = (
        f"?query.title={quote_plus(title)}"
        "&rows=1"
        "&select=DOI,title,author,funder,published-online,published-print,abstract,URL,container-title,type,is-referenced-by-count"
    )
    payload = fetch_json(f"{BASE_URL}{params}", headers=_headers())
    items = payload.get("message", {}).get("items", [])
    if not items:
        return {}
    return _normalize(items[0])


def _normalize(item: dict[str, Any]) -> dict[str, Any]:
    authors = []
    institutions = set()
    for author in item.get("author", []):
        full_name = " ".join(value for value in [author.get("given"), author.get("family")] if value).strip()
        if full_name:
            authors.append(full_name)
        for aff in author.get("affiliation", []):
            name = (aff.get("name") or "").strip()
            if name:
                institutions.add(name)

    funders = []
    for funder in item.get("funder", []):
        name = (funder.get("name") or "").strip()
        if name:
            funders.append(name)

    published = _extract_date(item)
    abstract = item.get("abstract")
    if isinstance(abstract, str):
        abstract = (
            abstract.replace("<jats:p>", " ")
            .replace("</jats:p>", " ")
            .replace("<jats:title>", " ")
            .replace("</jats:title>", " ")
            .strip()
        )
        abstract = " ".join(abstract.split())

    titles = item.get("title") or []
    container_titles = item.get("container-title") or []
    return {
        "doi": item.get("DOI"),
        "title": titles[0] if titles else None,
        "authors": authors,
        "institutions": sorted(institutions),
        "funders": funders,
        "abstract": abstract,
        "published_at": published,
        "primary_link": item.get("URL"),
        "journal_or_server": container_titles[0] if container_titles else None,
        "type": item.get("type"),
        "citation_count": item.get("is-referenced-by-count"),
    }


def _extract_date(item: dict[str, Any]) -> str | None:
    for field in ["published-online", "published-print", "published"]:
        date_parts = item.get(field, {}).get("date-parts", [])
        if not date_parts or not date_parts[0]:
            continue
        parts = date_parts[0]
        year = parts[0]
        month = parts[1] if len(parts) > 1 else 1
        day = parts[2] if len(parts) > 2 else 1
        return f"{year:04d}-{month:02d}-{day:02d}"
    return None
