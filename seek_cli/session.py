from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .exceptions import SeekCliError


@dataclass
class CookieSource:
    label: str
    path: Path | None = None
    browser: str | None = None


DEFAULT_SOURCES: list[CookieSource] = [
    CookieSource(label="openclaw-chrome", path=Path.home() / ".openclaw/browser/openclaw/user-data/Default/Cookies"),
    CookieSource(label="chrome-default", path=Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"),
]


def load_seek_cookies() -> list[tuple[str, str, str, str]]:
    """Load SEEK cookies from known browser cookie stores.

    Returns tuples of `(domain, path, name, value)`.
    """
    try:
        import browser_cookie3  # type: ignore
    except Exception as err:  # pragma: no cover - import guard
        raise SeekCliError(
            "browser-cookie3 is required for HTTP session reuse. Install seek-cli with browser-cookie3 support."
        ) from err

    found: list[tuple[str, str, str, str]] = []
    tried: list[str] = []

    for source in DEFAULT_SOURCES:
        if source.path and not source.path.exists():
            continue
        tried.append(source.label)
        try:
            jar = browser_cookie3.chrome(cookie_file=str(source.path), domain_name=".seek.co.nz")
        except Exception:
            continue
        for c in jar:
            if "seek.co.nz" not in c.domain:
                continue
            found.append((c.domain, c.path, c.name, c.value))
        if found:
            return dedupe_cookies(found)

    raise SeekCliError(
        "Could not load SEEK cookies from browser stores. Tried: "
        + (", ".join(tried) if tried else "no available stores")
        + ". Open SEEK in Chrome/OpenClaw browser first so the anti-bot-cleared session cookies exist."
    )


def dedupe_cookies(items: Iterable[tuple[str, str, str, str]]) -> list[tuple[str, str, str, str]]:
    seen: set[tuple[str, str, str]] = set()
    out: list[tuple[str, str, str, str]] = []
    for domain, path, name, value in items:
        key = (domain, path, name)
        if key in seen:
            continue
        seen.add(key)
        out.append((domain, path, name, value))
    return out
