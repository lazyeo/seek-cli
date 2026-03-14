from __future__ import annotations

from pathlib import Path

APP_NAME = "seek-cli"
SCHEMA_VERSION = "1"
CACHE_DIR = Path.home() / ".config" / APP_NAME
INDEX_FILE = CACHE_DIR / "last_search.json"
DEFAULT_PAGE_SIZE = 20
USER_AGENT = "seek-cli/0.1.0 (+read-only prototype)"
