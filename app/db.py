from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.config import settings


_DB_INIT_LOCK = threading.RLock()
_DB_INITIALIZED = False


def _ensure_parent() -> None:
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection(initialize: bool = True) -> Iterator[sqlite3.Connection]:
    if initialize:
        _ensure_initialized()
    _ensure_parent()
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    global _DB_INITIALIZED
    with _DB_INIT_LOCK:
        with get_connection(initialize=False) as conn:
            _create_schema(conn)
        _DB_INITIALIZED = True


def _ensure_initialized() -> None:
    with _DB_INIT_LOCK:
        if _DB_INITIALIZED and _has_table("papers"):
            return
        init_db()


def _has_table(table_name: str) -> bool:
    _ensure_parent()
    with sqlite3.connect(settings.database_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
    return row is not None


def _create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            source TEXT NOT NULL,
            external_id TEXT NOT NULL,
            title TEXT NOT NULL,
            abstract TEXT,
            authors_json TEXT NOT NULL,
            institutions_json TEXT NOT NULL,
            funders_json TEXT NOT NULL,
            journal_or_server TEXT,
            doi TEXT,
            primary_link TEXT,
            pdf_link TEXT,
            published_at TEXT,
            collected_for_date TEXT NOT NULL,
            keywords_json TEXT NOT NULL DEFAULT '[]',
            short_title_cn TEXT,
            summary_cn TEXT,
            one_line_takeaway TEXT,
            topic_label TEXT,
            publication_year INTEGER,
            citation_count INTEGER,
            research_category TEXT,
            research_type TEXT,
            brief_basis TEXT,
            abstract_brief TEXT,
            introduction_brief TEXT,
            methods_brief TEXT,
            results_brief TEXT,
            discussion_brief TEXT,
            novelty_score INTEGER,
            strengths_json TEXT NOT NULL DEFAULT '[]',
            weaknesses_json TEXT NOT NULL DEFAULT '[]',
            ranking_score REAL DEFAULT 0,
            summary TEXT,
            innovations_json TEXT NOT NULL,
            raw_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(domain, source, external_id, collected_for_date)
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_papers_lookup
        ON papers(domain, collected_for_date, published_at DESC)
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_digests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            digest_date TEXT NOT NULL,
            title TEXT NOT NULL,
            subtitle TEXT,
            overview_json TEXT NOT NULL,
            observation TEXT,
            related_json TEXT NOT NULL,
            total_papers INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(domain, digest_date)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_digest_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            digest_id INTEGER NOT NULL,
            paper_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            sort_order INTEGER NOT NULL,
            UNIQUE(digest_id, role, sort_order)
        )
        """
    )
    _ensure_column(conn, "papers", "journal_or_server", "TEXT")
    _ensure_column(conn, "papers", "keywords_json", "TEXT NOT NULL DEFAULT '[]'")
    _ensure_column(conn, "papers", "short_title_cn", "TEXT")
    _ensure_column(conn, "papers", "summary_cn", "TEXT")
    _ensure_column(conn, "papers", "one_line_takeaway", "TEXT")
    _ensure_column(conn, "papers", "topic_label", "TEXT")
    _ensure_column(conn, "papers", "publication_year", "INTEGER")
    _ensure_column(conn, "papers", "citation_count", "INTEGER")
    _ensure_column(conn, "papers", "research_category", "TEXT")
    _ensure_column(conn, "papers", "research_type", "TEXT")
    _ensure_column(conn, "papers", "brief_basis", "TEXT")
    _ensure_column(conn, "papers", "abstract_brief", "TEXT")
    _ensure_column(conn, "papers", "introduction_brief", "TEXT")
    _ensure_column(conn, "papers", "methods_brief", "TEXT")
    _ensure_column(conn, "papers", "results_brief", "TEXT")
    _ensure_column(conn, "papers", "discussion_brief", "TEXT")
    _ensure_column(conn, "papers", "novelty_score", "INTEGER")
    _ensure_column(conn, "papers", "strengths_json", "TEXT NOT NULL DEFAULT '[]'")
    _ensure_column(conn, "papers", "weaknesses_json", "TEXT NOT NULL DEFAULT '[]'")
    _ensure_column(conn, "papers", "ranking_score", "REAL DEFAULT 0")
    _ensure_column(conn, "daily_digests", "subtitle", "TEXT")
    _ensure_column(conn, "daily_digests", "observation", "TEXT")
    _ensure_column(conn, "daily_digests", "related_json", "TEXT NOT NULL DEFAULT '[]'")
    _ensure_column(conn, "daily_digests", "total_papers", "INTEGER NOT NULL DEFAULT 0")


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, column_type: str) -> None:
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


def upsert_paper(paper: dict) -> int:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO papers (
                domain, source, external_id, title, abstract,
                authors_json, institutions_json, funders_json, journal_or_server,
                doi, primary_link, pdf_link, published_at,
                collected_for_date, keywords_json, short_title_cn, summary_cn,
                one_line_takeaway, topic_label, publication_year, citation_count,
                research_category, research_type, brief_basis,
                abstract_brief, introduction_brief, methods_brief,
                results_brief, discussion_brief, novelty_score,
                strengths_json, weaknesses_json, ranking_score,
                summary, innovations_json, raw_json
            ) VALUES (
                :domain, :source, :external_id, :title, :abstract,
                :authors_json, :institutions_json, :funders_json, :journal_or_server,
                :doi, :primary_link, :pdf_link, :published_at,
                :collected_for_date, :keywords_json, :short_title_cn, :summary_cn,
                :one_line_takeaway, :topic_label, :publication_year, :citation_count,
                :research_category, :research_type, :brief_basis,
                :abstract_brief, :introduction_brief, :methods_brief,
                :results_brief, :discussion_brief, :novelty_score,
                :strengths_json, :weaknesses_json, :ranking_score,
                :summary, :innovations_json, :raw_json
            )
            ON CONFLICT(domain, source, external_id, collected_for_date)
            DO UPDATE SET
                title = excluded.title,
                abstract = excluded.abstract,
                authors_json = excluded.authors_json,
                institutions_json = excluded.institutions_json,
                funders_json = excluded.funders_json,
                journal_or_server = excluded.journal_or_server,
                doi = excluded.doi,
                primary_link = excluded.primary_link,
                pdf_link = excluded.pdf_link,
                published_at = excluded.published_at,
                keywords_json = excluded.keywords_json,
                short_title_cn = excluded.short_title_cn,
                summary_cn = excluded.summary_cn,
                one_line_takeaway = excluded.one_line_takeaway,
                topic_label = excluded.topic_label,
                publication_year = excluded.publication_year,
                citation_count = excluded.citation_count,
                research_category = excluded.research_category,
                research_type = excluded.research_type,
                brief_basis = excluded.brief_basis,
                abstract_brief = excluded.abstract_brief,
                introduction_brief = excluded.introduction_brief,
                methods_brief = excluded.methods_brief,
                results_brief = excluded.results_brief,
                discussion_brief = excluded.discussion_brief,
                novelty_score = excluded.novelty_score,
                strengths_json = excluded.strengths_json,
                weaknesses_json = excluded.weaknesses_json,
                ranking_score = excluded.ranking_score,
                summary = excluded.summary,
                innovations_json = excluded.innovations_json,
                raw_json = excluded.raw_json
            """,
            {
                **paper,
                "authors_json": json.dumps(paper.get("authors", []), ensure_ascii=False),
                "institutions_json": json.dumps(paper.get("institutions", []), ensure_ascii=False),
                "funders_json": json.dumps(paper.get("funders", []), ensure_ascii=False),
                "keywords_json": json.dumps(paper.get("keywords", []), ensure_ascii=False),
                "strengths_json": json.dumps(paper.get("strengths", []), ensure_ascii=False),
                "weaknesses_json": json.dumps(paper.get("weaknesses", []), ensure_ascii=False),
                "innovations_json": json.dumps(paper.get("innovations", []), ensure_ascii=False),
                "raw_json": json.dumps(paper.get("raw", {}), ensure_ascii=False),
            },
        )
        row = conn.execute(
            """
            SELECT id
            FROM papers
            WHERE domain = ? AND source = ? AND external_id = ? AND collected_for_date = ?
            """,
            (paper["domain"], paper["source"], paper["external_id"], paper["collected_for_date"]),
        ).fetchone()
        return int(row["id"])


def delete_papers_for_date(domain: str, collected_for_date: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM papers WHERE domain = ? AND collected_for_date = ?",
            (domain, collected_for_date),
        )


def delete_papers_for_date_sources(domain: str, collected_for_date: str, source_filters: list[str]) -> None:
    clauses = []
    params: list[object] = [domain, collected_for_date]
    for source in source_filters:
        if source in {"arxiv", "biorxiv", "medrxiv", "pubmed"}:
            clauses.append("source = ?")
            params.append(source)
        elif source == "cell":
            clauses.append("source = ?")
            params.append("cell_press")
        elif source == "science":
            clauses.append("(source = ? OR lower(journal_or_server) = ?)")
            params.extend(["science_journal", "science"])
        elif source == "nature":
            clauses.append("(source = ? OR lower(journal_or_server) LIKE ?)")
            params.extend(["nature_journal", "nature%"])

    if not clauses:
        return

    with get_connection() as conn:
        conn.execute(
            f"""
            DELETE FROM papers
            WHERE domain = ? AND collected_for_date = ?
            AND ({" OR ".join(clauses)})
            """,
            params,
        )


def list_papers(domain: str, collected_for_date: str, limit: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM papers
            WHERE domain = ? AND collected_for_date = ?
            ORDER BY published_at DESC, created_at DESC
            LIMIT ?
            """,
            (domain, collected_for_date, limit),
        ).fetchall()

    return [_deserialize_paper(row) for row in rows]


def list_papers_between(domain: str, date_from: str, date_to: str, limit: int | None = None) -> list[dict]:
    query = """
        SELECT *
        FROM papers
        WHERE domain = ? AND collected_for_date >= ? AND collected_for_date <= ?
        ORDER BY ranking_score DESC, published_at DESC, created_at DESC
    """
    params: list[object] = [domain, date_from, date_to]
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [_deserialize_paper(row) for row in rows]


def _deserialize_paper(row: sqlite3.Row | dict) -> dict:
    item = dict(row)
    item["authors"] = json.loads(item.pop("authors_json") or "[]")
    item["institutions"] = json.loads(item.pop("institutions_json") or "[]")
    item["funders"] = json.loads(item.pop("funders_json") or "[]")
    item["keywords"] = json.loads(item.pop("keywords_json") or "[]")
    item["strengths"] = json.loads(item.pop("strengths_json") or "[]")
    item["weaknesses"] = json.loads(item.pop("weaknesses_json") or "[]")
    item["innovations"] = json.loads(item.pop("innovations_json") or "[]")
    item["raw"] = json.loads(item.pop("raw_json") or "{}")
    return item


def upsert_daily_digest(digest: dict, items: list[dict]) -> int:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO daily_digests (
                domain, digest_date, title, subtitle,
                overview_json, observation, related_json, total_papers, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(domain, digest_date)
            DO UPDATE SET
                title = excluded.title,
                subtitle = excluded.subtitle,
                overview_json = excluded.overview_json,
                observation = excluded.observation,
                related_json = excluded.related_json,
                total_papers = excluded.total_papers,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                digest["domain"],
                digest["date"],
                digest["title"],
                digest.get("subtitle"),
                json.dumps(digest.get("overview", []), ensure_ascii=False),
                digest.get("observation"),
                json.dumps(digest.get("related", []), ensure_ascii=False),
                digest.get("total_papers", 0),
            ),
        )
        digest_row = conn.execute(
            "SELECT id FROM daily_digests WHERE domain = ? AND digest_date = ?",
            (digest["domain"], digest["date"]),
        ).fetchone()
        digest_id = int(digest_row["id"])
        conn.execute("DELETE FROM daily_digest_items WHERE digest_id = ?", (digest_id,))
        for item in items:
            conn.execute(
                """
                INSERT INTO daily_digest_items (digest_id, paper_id, role, sort_order)
                VALUES (?, ?, ?, ?)
                """,
                (digest_id, item["paper_id"], item["role"], item["sort_order"]),
            )
        return digest_id


def get_daily_digest(domain: str, digest_date: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM daily_digests
            WHERE domain = ? AND digest_date = ?
            """,
            (domain, digest_date),
        ).fetchone()
        if row is None:
            return None

        digest = dict(row)
        digest["overview"] = json.loads(digest.pop("overview_json") or "[]")
        digest["related"] = json.loads(digest.pop("related_json") or "[]")

        item_rows = conn.execute(
            """
            SELECT ddi.role, ddi.sort_order, p.*
            FROM daily_digest_items ddi
            JOIN papers p ON p.id = ddi.paper_id
            WHERE ddi.digest_id = ?
            ORDER BY ddi.role, ddi.sort_order
            """,
            (digest["id"],),
        ).fetchall()

    featured = []
    notable = []
    for row in item_rows:
        item = _deserialize_paper(row)
        role = item.pop("role")
        item.pop("sort_order")
        if role == "featured":
            featured.append(item)
        else:
            notable.append(item)

    digest["featured"] = featured
    digest["notable"] = notable
    return digest


def list_archive_cards(domain: str | None, limit: int, offset: int) -> list[dict]:
    query = """
        SELECT domain, digest_date, title, subtitle, overview_json, total_papers
        FROM daily_digests
    """
    params: list[object] = []
    if domain:
        query += " WHERE domain = ?"
        params.append(domain)
    query += " ORDER BY digest_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    items = []
    for row in rows:
        item = dict(row)
        item["overview"] = json.loads(item.pop("overview_json") or "[]")
        items.append(item)
    return items


def find_related_digests(domain: str, digest_date: str, limit: int = 3) -> list[dict]:
    with get_connection() as conn:
        prev_row = conn.execute(
            """
            SELECT domain, digest_date, title
            FROM daily_digests
            WHERE domain = ? AND digest_date < ?
            ORDER BY digest_date DESC
            LIMIT 1
            """,
            (domain, digest_date),
        ).fetchone()
        next_row = conn.execute(
            """
            SELECT domain, digest_date, title
            FROM daily_digests
            WHERE domain = ? AND digest_date > ?
            ORDER BY digest_date ASC
            LIMIT 1
            """,
            (domain, digest_date),
        ).fetchone()
        recent_rows = conn.execute(
            """
            SELECT domain, digest_date, title
            FROM daily_digests
            WHERE domain = ? AND digest_date != ?
            ORDER BY digest_date DESC
            LIMIT ?
            """,
            (domain, digest_date, max(limit, 3)),
        ).fetchall()

    seen = set()
    items = []
    for row in [prev_row, next_row, *recent_rows]:
        if row is None:
            continue
        key = (row["domain"], row["digest_date"])
        if key in seen:
            continue
        seen.add(key)
        items.append({"domain": row["domain"], "date": row["digest_date"], "title": row["title"]})
        if len(items) >= limit:
            break
    return items
