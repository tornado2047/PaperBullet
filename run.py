from __future__ import annotations

import os

from app.main import run_server


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "127.0.0.1").strip() or "127.0.0.1"
    port = int(os.getenv("APP_PORT", "8000"))
    run_server(host=host, port=port)
