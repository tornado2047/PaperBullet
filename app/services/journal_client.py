from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Any
from xml.etree import ElementTree as ET

from app.config import DOMAIN_PRESETS, OFFICIAL_JOURNAL_FEEDS
from app.services.http_utils import fetch_text


def fetch_official_journal_papers(
    domain: str,
    target_date: date,
    max_results: int,
    source_filters: list[str] | None = None,
) -> list[dict[str, Any]]:
    domain_config = DOMAIN_PRESETS[domain]
    keywords = [item.lower() for item in domain_config.get("journal_keywords", [])]
    selected = set(source_filters or [])
    feeds = [feed for feed in OFFICIAL_JOURNAL_FEEDS if not selected or _feed_family_key(feed) in selected]
    if not feeds:
        return []

    papers: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(len(feeds), 6)) as executor:
        futures = []
        for feed in feeds:
            default_limit = 2 if feed["source"] == "science_journal" else 3
            per_feed_limit = int(feed.get("per_feed_limit", max(default_limit, min(max_results, 6))))
            futures.append(executor.submit(_fetch_feed, feed, domain, keywords, target_date, per_feed_limit))
        for future in as_completed(futures):
            papers.extend(future.result())
    return papers[:max_results]


def _feed_family_key(feed: dict[str, Any]) -> str:
    source = feed.get("source")
    journal = (feed.get("journal") or "").lower()
    if source == "cell_press":
        return "cell"
    if source == "science_journal" or journal == "science":
        return "science"
    if source == "nature_journal" or journal.startswith("nature"):
        return "nature"
    return "other"


def _fetch_feed(
    feed: dict[str, Any],
    domain: str,
    keywords: list[str],
    target_date: date,
    max_results: int,
) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(fetch_text(feed["feed_url"], timeout=12))
    except Exception:
        return []

    items = [node for node in root.findall(".//{*}item")]
    collection: list[dict[str, Any]] = []
    for item in items:
        parsed = _parse_item(feed, item)
        if parsed is None:
            continue
        if parsed.get("published_at") != target_date.isoformat():
            continue
        if not _matches_domain(feed, parsed, keywords, domain):
            continue
        collection.append(parsed)
        if len(collection) >= max_results:
            break
    return collection


def _parse_item(feed: dict[str, Any], item: ET.Element) -> dict[str, Any] | None:
    title = _clean_text(_node_text(item, "title"))
    link = _clean_text(_node_text(item, "link"))
    encoded = _node_text(item, "encoded")
    description = _node_text(item, "description")
    doi = _extract_doi(item, link)
    published_at = _extract_published_at(item, description)
    if not title or not link or not published_at:
        return None

    snippet = _extract_snippet(feed["source"], encoded or description)
    authors = _extract_authors(item, description)
    external_id = doi or _clean_text(_node_text(item, "guid")) or link
    paper: dict[str, Any] = {
        "source": feed["source"],
        "external_id": external_id,
        "title": title,
        "abstract": snippet,
        "authors": authors,
        "institutions": [],
        "funders": [],
        "journal_or_server": feed["journal"],
        "doi": doi,
        "primary_link": link,
        "pdf_link": None,
        "published_at": published_at,
        "keywords": [feed["journal"]],
        "summary": None,
        "innovations": [],
        "raw": {
            "feed_url": feed["feed_url"],
            "publisher": feed["publisher"],
            "description": description,
            "encoded": encoded,
        },
    }

    return paper


def _matches_domain(feed: dict[str, Any], paper: dict[str, Any], keywords: list[str], domain: str) -> bool:
    haystack = " ".join(
        [
            paper.get("journal_or_server") or "",
            paper.get("title") or "",
            paper.get("abstract") or "",
        ]
    ).lower()
    hit_count = sum(1 for keyword in keywords if keyword in haystack)
    if domain != "biomed_all":
        return hit_count >= 1

    if feed["journal"] in {"Nature Medicine", "Nature Biotechnology", "Nature Methods", "Nature Biomedical Engineering", "Cell", "Cell Reports Medicine", "Med"}:
        return True

    if feed["journal"] in {"Nature", "Science"}:
        return hit_count >= 1

    if feed.get("strict_keyword_match"):
        return hit_count >= 1
    return hit_count >= 1


def _extract_published_at(item: ET.Element, description: str) -> str | None:
    for candidate in [
        _node_text(item, "date"),
        _node_text(item, "pubDate"),
        _extract_from_description(description),
    ]:
        normalized = _normalize_date(candidate)
        if normalized:
            return normalized
    return None


def _extract_doi(item: ET.Element, link: str) -> str | None:
    for candidate in [
        _node_text(item, "doi"),
        _node_text(item, "identifier"),
        link,
    ]:
        value = _clean_text(candidate)
        if not value:
            continue
        match = re.search(r"(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", value, flags=re.IGNORECASE)
        if match:
            return match.group(1).rstrip(".,;)")
    return None


def _extract_authors(item: ET.Element, description: str) -> list[str]:
    creators = [_clean_text(node.text or "") for node in item.findall(".//{http://purl.org/dc/elements/1.1/}creator")]
    creators = [value for value in creators if value]
    if creators:
        return creators

    match = re.search(r"Author\(s\):\s*(.+)", description or "", flags=re.IGNORECASE)
    if not match:
        return []
    raw = _strip_tags(match.group(1))
    return [part.strip() for part in raw.split(",") if part.strip()][:20]


def _extract_snippet(source: str, raw_html: str) -> str:
    if not raw_html:
        return ""
    plain = _strip_tags(raw_html)
    if source == "nature_journal":
        plain = re.sub(r"^.+?Published online:\s*[\dA-Za-z ,:-]+;\s*doi:[^\s]+\s*", "", plain, flags=re.IGNORECASE)
    elif source == "cell_press":
        plain = re.sub(r"Publication date:\s*Available online\s*[\dA-Za-z ,:-]+", "", plain, flags=re.IGNORECASE)
        plain = re.sub(r"Source:\s*.*?(?=Author\(s\):|$)", "", plain, flags=re.IGNORECASE)
        plain = re.sub(r"Author\(s\):.+", "", plain, flags=re.IGNORECASE)
    elif source == "science_journal":
        plain = re.sub(r"Science,\s*Volume.+", "", plain, flags=re.IGNORECASE)
    return _clean_text(plain)


def _extract_from_description(description: str) -> str | None:
    match = re.search(r"Available online\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})", description or "", flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = _clean_text(value).replace("Published online:", "").strip()
    patterns = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%SZ",
        "%d %B %Y",
        "%a, %d %b %Y %H:%M:%S %Z",
    ]
    for pattern in patterns:
        try:
            return datetime.strptime(cleaned, pattern).date().isoformat()
        except ValueError:
            continue
    try:
        return parsedate_to_datetime(cleaned).date().isoformat()
    except Exception:
        return None

def _node_text(node: ET.Element, suffix: str) -> str:
    found = node.find(f".//{{*}}{suffix}")
    if found is None:
        return ""
    return "".join(found.itertext())


def _strip_tags(value: str) -> str:
    return _clean_text(re.sub(r"<[^>]+>", " ", unescape(value or "")))


def _clean_text(value: str) -> str:
    return " ".join((value or "").replace("\xa0", " ").split())
