from __future__ import annotations

import json
from typing import Any

from .constants import CACHE_DIR, INDEX_FILE
from .models import JobSummary, SearchResult


def save_search(result: SearchResult) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def load_search() -> dict[str, Any] | None:
    if not INDEX_FILE.exists():
        return None
    return json.loads(INDEX_FILE.read_text())


def get_job_by_index(index: int) -> JobSummary | None:
    payload = load_search()
    if not payload:
        return None
    jobs = payload.get("jobs", [])
    if index < 1 or index > len(jobs):
        return None
    return JobSummary(**jobs[index - 1])
