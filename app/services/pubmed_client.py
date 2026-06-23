from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

from app.services.http_utils import fetch_json, fetch_text


EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def fetch_pubmed_papers(query: str, target_date: date, max_results: int) -> list[dict[str, Any]]:
    dated_query = f"({query}) AND {target_date.year:04d}/{target_date.month:02d}/{target_date.day:02d}[Date - Publication]"
    search_url = (
        f"{EUTILS}/esearch.fcgi?db=pubmed&retmode=json&sort=pub+date"
        f"&retmax={max(max_results * 2, 12)}&term={quote_plus(dated_query)}"
    )
    search_payload = fetch_json(search_url)
    ids = search_payload.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []

    summary_url = f"{EUTILS}/esummary.fcgi?db=pubmed&retmode=json&id={','.join(ids)}"
    summary_payload = fetch_json(summary_url).get("result", {})

    fetch_url = f"{EUTILS}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(ids)}"
    root = ET.fromstring(fetch_text(fetch_url))
    detail_map = _parse_pubmed_xml(root)

    papers: list[dict[str, Any]] = []
    for pmid in ids:
        summary = summary_payload.get(pmid)
        detail = detail_map.get(pmid, {})
        if not summary:
            continue
        published = (summary.get("epubdate") or summary.get("pubdate") or "")[:10]
        if published != target_date.isoformat():
            continue

        doi = _extract_doi(summary.get("articleids", [])) or detail.get("doi")
        papers.append(
            {
                "source": "pubmed",
                "external_id": pmid,
                "title": (summary.get("title") or "").strip(),
                "abstract": detail.get("abstract", "").strip(),
                "authors": [author.get("name") for author in summary.get("authors", []) if author.get("name")],
                "institutions": detail.get("institutions", []),
                "funders": detail.get("funders", []),
                "journal_or_server": summary.get("fulljournalname") or summary.get("source") or "PubMed",
                "doi": doi,
                "primary_link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "pdf_link": None,
                "published_at": published,
                "keywords": detail.get("keywords", []),
                "citation_count": summary.get("pmcrefcount"),
                "publication_types": summary.get("pubtype", []),
                "summary": None,
                "innovations": [],
                "raw": {
                    "summary": summary,
                    "detail": detail,
                },
            }
        )
        if len(papers) >= max_results:
            break

    return papers


def _extract_doi(article_ids: list[dict[str, Any]]) -> str | None:
    for article_id in article_ids:
        if article_id.get("idtype") == "doi":
            return article_id.get("value")
    return None


def _parse_pubmed_xml(root: ET.Element) -> dict[str, dict[str, Any]]:
    details: dict[str, dict[str, Any]] = {}
    for article in root.findall(".//PubmedArticle"):
        pmid = _text(article.find(".//PMID"))
        if not pmid:
            continue

        abstract_parts = []
        for node in article.findall(".//Abstract/AbstractText"):
            label = (node.attrib.get("Label") or "").strip()
            text = "".join(node.itertext()).strip()
            if not text:
                continue
            abstract_parts.append(f"{label}: {text}" if label else text)

        institutions = []
        for node in article.findall(".//Author/AffiliationInfo/Affiliation"):
            text = _text(node)
            if text and text not in institutions:
                institutions.append(text)

        keywords = []
        for node in article.findall(".//Keyword"):
            text = _text(node)
            if text and text not in keywords:
                keywords.append(text)

        funders = []
        for node in article.findall(".//Grant/Agency"):
            text = _text(node)
            if text and text not in funders:
                funders.append(text)

        doi = None
        for node in article.findall(".//ArticleId"):
            if node.attrib.get("IdType") == "doi":
                doi = _text(node)
                break

        details[pmid] = {
            "abstract": " ".join(abstract_parts),
            "institutions": institutions[:12],
            "keywords": keywords[:10],
            "funders": funders[:10],
            "doi": doi,
        }
    return details


def _text(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return " ".join("".join(node.itertext()).split())
