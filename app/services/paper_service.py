from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from app.config import DOMAIN_PRESETS, settings
from app.db import (
    delete_papers_for_date,
    find_related_digests,
    get_daily_digest,
    list_archive_cards,
    list_papers,
    list_papers_between,
    upsert_daily_digest,
    upsert_paper,
)
from app.services.arxiv_client import fetch_latest_papers
from app.services.biorxiv_client import fetch_preprints
from app.services.crossref_client import enrich_by_doi_or_title
from app.services.journal_client import fetch_official_journal_papers
from app.services.pubmed_client import fetch_pubmed_papers
from app.services.summarizer import PaperSummarizer


summarizer = PaperSummarizer()


def collect_papers(
    domain: str,
    target_date_str: str | None,
    custom_query: str | None,
    limit: int,
    target_date_to_str: str | None = None,
    page: int = 1,
    page_size: int = 10,
    source_filters: list[str] | None = None,
) -> dict[str, Any]:
    del custom_query
    date_from, date_to = _parse_date_range(target_date_str, target_date_to_str)
    for current_date in _iterate_dates(date_from, date_to):
        _collect_single_day(domain, current_date, limit)
    return get_digest(
        domain=domain,
        target_date_str=date_from.isoformat(),
        limit=limit,
        target_date_to_str=date_to.isoformat(),
        page=page,
        page_size=page_size,
        source_filters=source_filters,
    )


def get_digest(
    domain: str,
    target_date_str: str | None,
    limit: int,
    target_date_to_str: str | None = None,
    page: int = 1,
    page_size: int = 10,
    source_filters: list[str] | None = None,
) -> dict[str, Any]:
    del limit
    page = max(1, page)
    page_size = max(1, min(page_size, 50))
    normalized_sources = _normalize_source_filters(source_filters)
    date_from, date_to = _parse_date_range(target_date_str, target_date_to_str)
    if date_from == date_to:
        digest = get_daily_digest(domain, date_from.isoformat())
        if digest is not None:
            ranked_all = list_papers_between(domain=domain, date_from=date_from.isoformat(), date_to=date_to.isoformat(), limit=None)
            filtered_ranked = _filter_papers_by_sources(ranked_all, normalized_sources)
            page_payload = _paginate_papers(filtered_ranked, page, page_size)
            return {
                "domain": digest["domain"],
                "date": digest["digest_date"],
                "date_from": digest["digest_date"],
                "date_to": digest["digest_date"],
                "is_range": False,
                "period_label": _format_period_label(date_from, date_to),
                "title": "论文速递",
                "subtitle": digest.get("subtitle"),
                "overview": digest.get("overview", []),
                "observation": "",
                "total_papers": page_payload["total_papers"],
                "page": page_payload["page"],
                "page_size": page_payload["page_size"],
                "total_pages": page_payload["total_pages"],
                "selected_sources": normalized_sources,
                "source_stats": _build_source_stats(ranked_all, normalized_sources),
                "category_stats": _build_category_stats(filtered_ranked),
                "recommended": [_public_paper_view(item) for item in _build_recommendations(filtered_ranked, limit=3)],
                "related": find_related_digests(domain, digest["digest_date"], limit=3),
                "items": [_public_paper_view(item) for item in page_payload["items"]],
            }

    ranked = list_papers_between(domain=domain, date_from=date_from.isoformat(), date_to=date_to.isoformat(), limit=None)
    filtered_ranked = _filter_papers_by_sources(ranked, normalized_sources)
    digest_bits = _compose_range_digest(domain, filtered_ranked, date_from, date_to)
    page_payload = _paginate_papers(filtered_ranked, page, page_size)
    if not ranked:
        return {
            "domain": domain,
            "date": date_to.isoformat(),
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "is_range": date_from != date_to,
            "period_label": _format_period_label(date_from, date_to),
            "title": "论文速递",
            "subtitle": "这个时间段还没有生成可展示的论文摘要，点击“更新本时段”即可抓取并整理区间内新论文。",
            "overview": [],
            "items": [],
            "observation": "",
            "source_stats": [],
            "category_stats": [],
            "selected_sources": normalized_sources,
            "recommended": [],
            "related": find_related_digests(domain, date_to.isoformat(), limit=3),
            "total_papers": 0,
            "page": 1,
            "page_size": page_size,
            "total_pages": 0,
        }

    return {
        "domain": domain,
        "date": date_to.isoformat(),
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "is_range": date_from != date_to,
        "period_label": _format_period_label(date_from, date_to),
        "title": "论文速递",
        "subtitle": digest_bits["subtitle"],
        "overview": digest_bits["overview"],
        "observation": "",
        "total_papers": page_payload["total_papers"],
        "page": page_payload["page"],
        "page_size": page_payload["page_size"],
        "total_pages": page_payload["total_pages"],
        "selected_sources": normalized_sources,
        "source_stats": _build_source_stats(ranked, normalized_sources),
        "category_stats": _build_category_stats(filtered_ranked),
        "recommended": [_public_paper_view(item) for item in _build_recommendations(filtered_ranked, limit=3)],
        "related": find_related_digests(domain, date_to.isoformat(), limit=3),
        "items": [_public_paper_view(item) for item in page_payload["items"]],
    }


def get_archive(domain: str | None, limit: int, cursor: str | None) -> dict[str, Any]:
    offset = int(cursor or "0")
    items = list_archive_cards(domain=domain, limit=limit, offset=offset)
    next_cursor = str(offset + limit) if len(items) == limit else None
    return {
        "items": [
            {
                "domain": item["domain"],
                "date": item["digest_date"],
                "title": item["title"],
                "subtitle": item.get("subtitle"),
                "overview": item.get("overview", [])[:3],
                "total_papers": item.get("total_papers", 0),
            }
            for item in items
        ],
        "next_cursor": next_cursor,
    }


def resolve_query(domain: str, custom_query: str | None = None) -> str:
    del custom_query
    config = _get_domain_config(domain)
    return config["source_queries"]["arxiv"]


def _get_domain_config(domain: str) -> dict[str, Any]:
    if domain not in DOMAIN_PRESETS:
        raise ValueError(f"unsupported domain: {domain}")
    return DOMAIN_PRESETS[domain]


def _fetch_all_sources(domain_config: dict[str, Any], target_date: date, limit: int) -> list[dict[str, Any]]:
    per_source_limit = min(max(limit, 9), settings.collect_max_results)
    queries = domain_config["source_queries"]
    papers: list[dict[str, Any]] = []
    papers.extend(_safe_fetch(fetch_latest_papers, queries["arxiv"], target_date, per_source_limit))
    papers.extend(
        _safe_fetch(
            fetch_preprints,
            server="biorxiv",
            target_date=target_date,
            max_results=per_source_limit,
            categories=queries.get("biorxiv_categories"),
            keywords=queries.get("biorxiv_keywords"),
        )
    )
    papers.extend(
        _safe_fetch(
            fetch_preprints,
            server="medrxiv",
            target_date=target_date,
            max_results=per_source_limit,
            categories=queries.get("medrxiv_categories"),
            keywords=queries.get("medrxiv_keywords"),
        )
    )
    papers.extend(_safe_fetch(fetch_pubmed_papers, queries["pubmed"], target_date, per_source_limit))
    papers.extend(_safe_fetch(fetch_official_journal_papers, domain=domain_config["key"], target_date=target_date, max_results=per_source_limit))
    return papers


def _safe_fetch(fetcher, *args, **kwargs) -> list[dict[str, Any]]:
    try:
        return fetcher(*args, **kwargs)
    except Exception:
        return []


def _collect_single_day(domain: str, target_date: date, limit: int) -> list[dict[str, Any]]:
    domain_config = _get_domain_config(domain)
    domain_config = {**domain_config, "key": domain}
    delete_papers_for_date(domain, target_date.isoformat())
    fetched = _fetch_all_sources(domain_config, target_date, limit)
    papers = _dedupe_papers(fetched)

    persisted: list[dict[str, Any]] = []
    for paper in papers:
        _enrich_metadata(paper)
        if not _is_research_article(paper):
            continue
        analysis = summarizer.analyze_paper(paper, domain_config["label"])
        paper["abstract"] = analysis.get("abstract_brief") or ""
        paper.update(analysis)
        paper["domain"] = domain
        paper["collected_for_date"] = target_date.isoformat()
        paper["paper_id"] = upsert_paper(paper)
        persisted.append(paper)

    ranked = sorted(
        persisted,
        key=lambda item: (item.get("ranking_score", 0), item.get("published_at") or ""),
        reverse=True,
    )
    digest_bits = summarizer.compose_digest(domain_config["label"], ranked)
    digest = {
        "domain": domain,
        "date": target_date.isoformat(),
        "title": digest_bits["title"],
        "subtitle": digest_bits["subtitle"],
        "overview": digest_bits["overview"],
        "observation": digest_bits["observation"],
        "featured": ranked[:3],
        "notable": ranked[3:9],
        "related": find_related_digests(domain, target_date.isoformat(), limit=3),
        "total_papers": len(ranked),
    }
    digest_items = [
        {"paper_id": paper["paper_id"], "role": "featured", "sort_order": index}
        for index, paper in enumerate(digest["featured"], start=1)
    ] + [
        {"paper_id": paper["paper_id"], "role": "notable", "sort_order": index}
        for index, paper in enumerate(digest["notable"], start=1)
    ]
    upsert_daily_digest(digest, digest_items)
    return ranked


def _enrich_metadata(paper: dict[str, Any]) -> None:
    source = paper.get("source")
    if source == "pubmed":
        return

    if source in {"biorxiv", "medrxiv"} and paper.get("doi") and paper.get("abstract"):
        return

    metadata = enrich_by_doi_or_title(paper.get("doi"), paper["title"])
    if metadata.get("doi") and not paper.get("doi"):
        paper["doi"] = metadata["doi"]
    if metadata.get("primary_link") and paper.get("source") not in {"pubmed", "nature_journal", "science_journal", "cell_press"}:
        paper["primary_link"] = metadata["primary_link"]
    if metadata.get("institutions"):
        paper["institutions"] = metadata["institutions"]
    if metadata.get("funders"):
        paper["funders"] = metadata["funders"]
    if metadata.get("authors") and paper.get("source") == "arxiv":
        paper["authors"] = metadata["authors"]
    if metadata.get("abstract") and len(metadata["abstract"]) > len(paper.get("abstract") or ""):
        paper["abstract"] = metadata["abstract"]
    if metadata.get("journal_or_server") and not paper.get("journal_or_server"):
        paper["journal_or_server"] = metadata["journal_or_server"]
    if metadata.get("published_at") and not paper.get("published_at"):
        paper["published_at"] = metadata["published_at"]
    if metadata.get("citation_count") is not None and paper.get("citation_count") is None:
        paper["citation_count"] = metadata["citation_count"]
    if metadata.get("type"):
        paper["crossref_type"] = metadata["type"]
        paper.setdefault("raw", {})
        paper["raw"]["crossref_type"] = metadata["type"]


def _is_research_article(paper: dict[str, Any]) -> bool:
    title = (paper.get("title") or "").strip().lower()
    abstract = (paper.get("abstract") or "").strip().lower()
    journal = (paper.get("journal_or_server") or "").strip().lower()
    source = (paper.get("source") or "").strip().lower()
    crossref_type = (paper.get("crossref_type") or paper.get("raw", {}).get("crossref_type") or "").strip().lower()
    publication_types = [item.lower() for item in paper.get("publication_types", [])]
    doi = (paper.get("doi") or "").strip().lower()
    author_count = len(paper.get("authors", []))
    institution_count = len(paper.get("institutions", []))
    funder_count = len(paper.get("funders", []))

    excluded_title_tokens = [
        "editorial",
        "commentary",
        "comment",
        "perspective",
        "news",
        "career",
        "book review",
        "author correction",
        "publisher correction",
        "retraction",
        "erratum",
        "corrigendum",
        "reply to",
        "response to",
        "obituary",
        "podcast",
    ]
    if any(token in title for token in excluded_title_tokens):
        return False

    if publication_types and any(
        token in item
        for item in publication_types
        for token in ["review", "editorial", "comment", "news", "biography", "interview", "published erratum", "letter"]
    ):
        return False

    if crossref_type and crossref_type not in {"journal-article", "posted-content", "proceedings-article"}:
        return False

    if source in {"arxiv", "biorxiv", "medrxiv"}:
        return True

    if source == "pubmed":
        return True

    if source == "nature_journal" and len(abstract) < 80:
        return False

    if journal in {"nature", "science"} and len(abstract) < 120:
        return False

    if doi.startswith("10.1038/d41586-"):
        return False

    if journal in {"nature", "science"} and author_count <= 1 and institution_count == 0 and funder_count == 0 and len(abstract) < 260:
        return False

    if source in {"nature_journal", "science_journal", "cell_press"} and len(title.split()) < 4:
        return False

    nonresearch_patterns = [
        "this editorial",
        "this comment",
        "this perspective",
        "the news section",
        "book review",
    ]
    if any(pattern in abstract for pattern in nonresearch_patterns):
        return False

    return True


def _dedupe_papers(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chosen: dict[str, dict[str, Any]] = {}
    for paper in papers:
        key = paper.get("doi") or _normalize_title(paper.get("title") or "")
        if key in chosen:
            if _paper_richness(paper) > _paper_richness(chosen[key]):
                chosen[key] = paper
        else:
            chosen[key] = paper
    return list(chosen.values())


def _paper_richness(paper: dict[str, Any]) -> int:
    return sum(
        [
            len(paper.get("abstract") or ""),
            len(paper.get("institutions", [])) * 40,
            len(paper.get("funders", [])) * 30,
            20 if paper.get("doi") else 0,
            10 if paper.get("pdf_link") else 0,
        ]
    )


def _normalize_title(title: str) -> str:
    return "".join(char.lower() for char in title if char.isalnum())


def _parse_date(value: str | None) -> date:
    if not value:
        return date.today()
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_date_range(value_from: str | None, value_to: str | None) -> tuple[date, date]:
    if value_from and not value_to:
        single = _parse_date(value_from)
        return single, single

    end_date = _parse_date(value_to) if value_to else _parse_date(None)
    start_date = _parse_date(value_from) if value_from else end_date - timedelta(days=6)
    if start_date > end_date:
        raise ValueError("date_from must be earlier than or equal to date_to")
    return start_date, end_date


def _iterate_dates(date_from: date, date_to: date):
    current = date_from
    while current <= date_to:
        yield current
        current += timedelta(days=1)


def _compose_range_digest(domain: str, ranked: list[dict[str, Any]], date_from: date, date_to: date) -> dict[str, Any]:
    domain_label = _get_domain_config(domain)["label"]
    digest_bits = summarizer.compose_digest(domain_label, ranked)
    period_label = _format_period_label(date_from, date_to)
    return {
        "title": "论文速递",
        "subtitle": f"{period_label}内共整理 {len(ranked)} 篇论文。{digest_bits['subtitle']}" if ranked else f"{period_label}内暂无论文。",
        "overview": digest_bits["overview"],
        "observation": "",
    }


def _format_period_label(date_from: date, date_to: date) -> str:
    if date_from == date_to:
        return date_from.isoformat()
    return f"{date_from.isoformat()} 至 {date_to.isoformat()}"


def _paginate_papers(papers: list[dict[str, Any]], page: int, page_size: int) -> dict[str, Any]:
    total_papers = len(papers)
    if total_papers == 0:
        return {
            "items": [],
            "page": 1,
            "page_size": page_size,
            "total_pages": 0,
            "total_papers": 0,
        }

    total_pages = (total_papers + page_size - 1) // page_size
    safe_page = min(page, total_pages)
    start = (safe_page - 1) * page_size
    end = start + page_size
    return {
        "items": papers[start:end],
        "page": safe_page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_papers": total_papers,
    }


def _public_paper_view(paper: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": paper.get("id"),
        "source": paper.get("source"),
        "source_family": _source_family_key(paper),
        "title": paper.get("title"),
        "short_title_cn": paper.get("short_title_cn"),
        "summary": paper.get("summary"),
        "summary_cn": paper.get("summary_cn"),
        "one_line_takeaway": paper.get("one_line_takeaway"),
        "topic_label": paper.get("topic_label"),
        "publication_year": paper.get("publication_year"),
        "citation_count": paper.get("citation_count"),
        "research_category": paper.get("research_category"),
        "research_type": paper.get("research_type"),
        "brief_basis": paper.get("brief_basis"),
        "abstract_brief": paper.get("abstract_brief"),
        "introduction_brief": paper.get("introduction_brief"),
        "methods_brief": paper.get("methods_brief"),
        "results_brief": paper.get("results_brief"),
        "discussion_brief": paper.get("discussion_brief"),
        "novelty_score": paper.get("novelty_score"),
        "strengths": paper.get("strengths", []),
        "weaknesses": paper.get("weaknesses", []),
        "innovations": paper.get("innovations", []),
        "authors": paper.get("authors", []),
        "institutions": paper.get("institutions", []),
        "funders": paper.get("funders", []),
        "journal_or_server": paper.get("journal_or_server"),
        "doi": paper.get("doi"),
        "primary_link": paper.get("primary_link"),
        "pdf_link": paper.get("pdf_link"),
        "published_at": paper.get("published_at"),
        "keywords": paper.get("keywords", []),
        "ranking_score": paper.get("ranking_score", 0),
    }


def _build_source_stats(papers: list[dict[str, Any]], selected_sources: list[str] | None = None) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for paper in papers:
        key = _source_family_key(paper)
        counts[key] = counts.get(key, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], _source_option_label(item[0]).lower()))
    selected_set = set(selected_sources or [])
    return [
        {
            "key": key,
            "label": _source_option_label(key),
            "count": count,
            "selected": key in selected_set if selected_set else False,
        }
        for key, count in ordered
    ]


def _build_category_stats(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for paper in papers:
        label = paper.get("research_category") or paper.get("topic_label") or "综合生物医学"
        counts[label] = counts.get(label, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{"label": label, "count": count} for label, count in ordered]


def _build_recommendations(papers: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    candidates = [paper for paper in papers if paper.get("title")]
    ranked = sorted(
        candidates,
        key=lambda item: (
            item.get("citation_count") is not None,
            item.get("citation_count") or -1,
            item.get("ranking_score") or 0,
            item.get("published_at") or "",
        ),
        reverse=True,
    )
    return ranked[:limit]


def _normalize_source_filters(source_filters: list[str] | None) -> list[str]:
    valid = {"nature", "science", "cell", "pubmed", "biorxiv", "medrxiv", "arxiv"}
    normalized: list[str] = []
    for item in source_filters or []:
        key = str(item).strip().lower()
        if key in valid and key not in normalized:
            normalized.append(key)
    return normalized


def _filter_papers_by_sources(papers: list[dict[str, Any]], source_filters: list[str] | None) -> list[dict[str, Any]]:
    if not source_filters:
        return papers
    selected = set(source_filters)
    return [paper for paper in papers if _source_family_key(paper) in selected]


def _source_family_label(paper: dict[str, Any]) -> str:
    return _source_option_label(_source_family_key(paper))


def _source_family_key(paper: dict[str, Any]) -> str:
    source = (paper.get("source") or "").lower()
    journal = (paper.get("journal_or_server") or "").lower()
    if source == "pubmed":
        return "pubmed"
    if source == "biorxiv":
        return "biorxiv"
    if source == "medrxiv":
        return "medrxiv"
    if source == "arxiv":
        return "arxiv"
    if source == "cell_press":
        return "cell"
    if source == "science_journal" or journal == "science":
        return "science"
    if source == "nature_journal" or journal.startswith("nature"):
        return "nature"
    return "other"


def _source_option_label(key: str) -> str:
    mapping = {
        "nature": "Nature",
        "science": "Science",
        "cell": "Cell",
        "pubmed": "PubMed",
        "biorxiv": "bioRxiv",
        "medrxiv": "medRxiv",
        "arxiv": "arXiv",
        "other": "其他来源",
    }
    return mapping.get(key, key)
