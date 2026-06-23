from __future__ import annotations

import json
import ssl
from urllib.request import Request, urlopen


SSL_CONTEXT = ssl.create_default_context()


def fetch_text(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> str:
    request = Request(url, headers=headers or {"User-Agent": "BiomedDigest/1.0"})
    with urlopen(request, timeout=timeout, context=SSL_CONTEXT) as response:
        return response.read().decode("utf-8")


def fetch_json(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> dict:
    return json.loads(fetch_text(url, headers=headers, timeout=timeout))
