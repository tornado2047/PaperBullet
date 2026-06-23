from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from app.config import DOMAIN_PRESETS, settings
from app.db import init_db, list_papers
from app.services.paper_service import collect_papers, get_archive, get_digest
from app.services.scheduler import start_scheduler, stop_scheduler


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def list_domains() -> dict:
    return {
        "domains": [
            {
                "key": key,
                "label": value["label"],
                "description": value["description"],
                "theme_color": value["theme_color"],
            }
            for key, value in DOMAIN_PRESETS.items()
        ]
    }


def _parse_sources(values: list[str] | None) -> list[str]:
    normalized: list[str] = []
    for value in values or []:
        for item in str(value).split(","):
            cleaned = item.strip().lower()
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)
    return normalized


class LiteratureHandler(BaseHTTPRequestHandler):
    server_version = "BiomedDigest/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self._serve_file(STATIC_DIR / "index.html")
            return

        if parsed.path == "/archive":
            self._serve_file(STATIC_DIR / "archive.html")
            return

        target = self._resolve_static_path(parsed.path)
        if target is not None:
            self._serve_file(target)
            return

        if parsed.path == "/api/domains":
            self._send_json(list_domains())
            return

        if parsed.path == "/api/digest":
            params = parse_qs(parsed.query)
            domain = params.get("domain", ["biomed_all"])[0]
            date_from = params.get("date_from", [None])[0]
            date_to = params.get("date_to", [None])[0]
            date_value = params.get("date", [None])[0]
            sources = _parse_sources(params.get("sources", []))
            limit = int(params.get("limit", ["24"])[0])
            page = int(params.get("page", ["1"])[0])
            page_size = int(params.get("page_size", ["10"])[0])
            try:
                self._send_json(
                    get_digest(
                        domain=domain,
                        target_date_str=date_from or date_value,
                        target_date_to_str=date_to,
                        limit=limit,
                        page=page,
                        page_size=page_size,
                        source_filters=sources,
                    )
                )
            except ValueError as exc:
                self._send_json({"detail": str(exc)}, HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == "/api/archive":
            params = parse_qs(parsed.query)
            domain = params.get("domain", [None])[0]
            limit = int(params.get("limit", ["12"])[0])
            cursor = params.get("cursor", [None])[0]
            try:
                self._send_json(get_archive(domain=domain, limit=limit, cursor=cursor))
            except ValueError as exc:
                self._send_json({"detail": str(exc)}, HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == "/api/papers":
            params = parse_qs(parsed.query)
            domain = params.get("domain", [None])[0]
            date_value = params.get("date", [None])[0]
            limit = int(params.get("limit", ["20"])[0])
            if not domain or not date_value:
                self._send_json({"detail": "domain and date are required"}, HTTPStatus.BAD_REQUEST)
                return
            items = list_papers(domain=domain, collected_for_date=date_value, limit=limit)
            self._send_json(
                {
                    "domain": domain,
                    "collected_for_date": date_value,
                    "total": len(items),
                    "items": items,
                }
            )
            return

        self._send_json({"detail": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in ["/api/refresh", "/api/digest/refresh"]:
            self._send_json({"detail": "Not found"}, HTTPStatus.NOT_FOUND)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"

        try:
            payload = json.loads(raw_body)
            result = collect_papers(
                domain=payload["domain"],
                target_date_str=payload.get("date_from") or payload.get("date"),
                target_date_to_str=payload.get("date_to"),
                custom_query=payload.get("custom_query"),
                limit=int(payload.get("limit", 18)),
                page=int(payload.get("page", 1)),
                page_size=int(payload.get("page_size", 10)),
                source_filters=_parse_sources(payload.get("sources", [])),
            )
            self._send_json(result)
        except KeyError:
            self._send_json({"detail": "domain is required"}, HTTPStatus.BAD_REQUEST)
        except ValueError as exc:
            self._send_json({"detail": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            self._send_json({"detail": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, format: str, *args) -> None:
        return

    def _serve_file(self, path: Path) -> None:
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _resolve_static_path(self, path: str) -> Path | None:
        candidates = []
        if path.startswith("/static/"):
            candidates.append(path.removeprefix("/static/"))
        elif path.count("/") == 1 and "." in path:
            candidates.append(path.removeprefix("/"))

        for relative_path in candidates:
            target = (STATIC_DIR / relative_path).resolve()
            if str(target).startswith(str(STATIC_DIR.resolve())) and target.exists():
                return target
        return None


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    init_db()
    start_scheduler()
    server = ThreadingHTTPServer((host, port), LiteratureHandler)
    try:
        print(f"{settings.app_name} running at http://{host}:{port}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_scheduler()
        server.server_close()


if __name__ == "__main__":
    run_server()
