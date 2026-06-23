from __future__ import annotations

from datetime import date
from typing import Any

from app.services.http_utils import fetch_json


BASE_URL = "https://api.biorxiv.org/details"


def fetch_preprints(
    server: str,
    target_date: date,
    max_results: int,
    categories: list[str] | None = None,
    keywords: list[str] | None = None,
) -> list[dict[str, Any]]:
    collection: list[dict[str, Any]] = []
    cursor = 0
    normalized_categories = {item.lower() for item in categories or []}
    normalized_keywords = [item.lower() for item in keywords or []]

    while len(collection) < max_results:
        url = f"{BASE_URL}/{server}/{target_date.isoformat()}/{target_date.isoformat()}/{cursor}"
        payload = fetch_json(url)
        rows = payload.get("collection", [])
        if not rows:
            break

        for row in rows:
            if row.get("date") != target_date.isoformat():
                continue
            category = (row.get("category") or "").lower()
            haystack = f"{row.get('title', '')} {row.get('abstract', '')}".lower()
            keyword_hits = sum(1 for keyword in normalized_keywords if keyword in haystack)
            if normalized_categories and category and category not in normalized_categories:
                if normalized_keywords and keyword_hits < 2:
                    continue
            elif normalized_keywords and keyword_hits < 1:
                continue

            doi = (row.get("doi") or "").strip() or None
            version = (row.get("version") or "1").strip() or "1"
            primary_link = f"https://www.{server}.org/content/{doi}v{version}" if doi else None
            pdf_link = f"{primary_link}.full.pdf" if primary_link else None
            corresponding_institution = (row.get("author_corresponding_institution") or "").strip()

            collection.append(
                {
                    "source": server,
                    "external_id": doi or f"{server}:{row.get('title', '')[:64]}",
                    "title": (row.get("title") or "").strip(),
                    "abstract": (row.get("abstract") or "").strip(),
                    "authors": _split_people(row.get("authors") or ""),
                    "institutions": [corresponding_institution] if corresponding_institution else [],
                    "funders": [],
                    "journal_or_server": server,
                    "doi": doi,
                    "primary_link": primary_link,
                    "pdf_link": pdf_link,
                    "published_at": row.get("date"),
                    "keywords": [value for value in [row.get("category")] if value],
                    "summary": None,
                    "innovations": [],
                    "raw": row,
                }
            )
            if len(collection) >= max_results:
                break

        cursor += len(rows)
        if len(rows) < 30:
            break

    return collection


def _split_people(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]
