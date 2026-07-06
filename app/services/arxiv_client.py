from __future__ import annotations

import html
import ssl
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
SSL_CONTEXT = ssl.create_default_context()


def _text(node: ET.Element | None) -> str:
    if node is None or node.text is None:
        return ""
    return " ".join(node.text.split())


def _date_filtered_query(query: str, target_date: date) -> str:
    day = target_date.strftime("%Y%m%d")
    return f"({query}) AND submittedDate:[{day}0000 TO {day}2359]"


def fetch_latest_papers(query: str, target_date: date, max_results: int = 20) -> list[dict[str, Any]]:
    dated_query = _date_filtered_query(query, target_date)
    encoded_query = quote(dated_query, safe='():"+ ')
    encoded_query = encoded_query.replace(" ", "+")
    url = (
        f"{ARXIV_API_URL}?search_query={encoded_query}"
        f"&start=0&max_results={max(max_results, 20)}"
        "&sortBy=submittedDate&sortOrder=descending"
    )
    request = Request(url, headers={"User-Agent": "BiomedDigest/1.0"})
    try:
        with urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
            body = response.read().decode("utf-8")
    except (HTTPError, URLError):
        return []

    root = ET.fromstring(body)
    entries = root.findall("atom:entry", ATOM_NS)

    papers: list[dict[str, Any]] = []
    for entry in entries:
        published_raw = _text(entry.find("atom:published", ATOM_NS))
        if not published_raw:
            continue
        if published_raw[:10] != target_date.isoformat():
            continue

        arxiv_id = _text(entry.find("atom:id", ATOM_NS)).split("/")[-1]
        title = html.unescape(_text(entry.find("atom:title", ATOM_NS)))
        abstract = html.unescape(_text(entry.find("atom:summary", ATOM_NS)))
        authors = [_text(author.find("atom:name", ATOM_NS)) for author in entry.findall("atom:author", ATOM_NS)]

        primary_link = _text(entry.find("atom:id", ATOM_NS))
        pdf_link = None
        doi = None
        categories = [category.attrib.get("term", "") for category in entry.findall("atom:category", ATOM_NS)]

        for link in entry.findall("atom:link", ATOM_NS):
            if link.attrib.get("title") == "pdf":
                pdf_link = link.attrib.get("href")

        doi_node = entry.find("arxiv:doi", ATOM_NS)
        if doi_node is not None and doi_node.text:
            doi = doi_node.text.strip()

        papers.append(
            {
                "source": "arxiv",
                "external_id": arxiv_id,
                "title": title,
                "abstract": abstract,
                "authors": [author for author in authors if author],
                "institutions": [],
                "funders": [],
                "journal_or_server": "arXiv",
                "doi": doi,
                "primary_link": primary_link,
                "pdf_link": pdf_link,
                "published_at": published_raw,
                "keywords": [category for category in categories if category],
                "summary": None,
                "innovations": [],
                "raw": {
                    "categories": categories,
                    "query": dated_query,
                },
            }
        )
        if len(papers) >= max_results:
            break

    return papers
