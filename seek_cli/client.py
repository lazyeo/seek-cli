from __future__ import annotations

import json
from urllib.parse import quote_plus

from .constants import USER_AGENT
from .exceptions import TransportError
from .models import JobDetail, SearchResult
from .parsers import parse_detail_apollo, parse_search_apollo
from .session import load_seek_cookies


class SeekClient:
    """Read-only SEEK client abstraction.

    This client now prefers the "pure" transport path:
    browser-cookie session reuse plus browser-fingerprint HTTP requests.
    Current working transport uses curl_cffi impersonation rather than a full
    browser automation stack.
    """

    def __init__(self, timeout: float = 20.0, locale: str = "en-NZ"):
        self._timeout = timeout
        self._locale = locale
        self._http = self._build_http_client(timeout)

    def _build_http_client(self, timeout: float):
        try:
            from curl_cffi import requests as curl_requests  # type: ignore
        except Exception as err:  # pragma: no cover - import guard
            raise TransportError(
                "curl_cffi is required for SEEK HTTP session reuse. Install seek-cli with curl_cffi support."
            ) from err

        client = curl_requests.Session(impersonate="chrome136")
        client.headers.update(
            {
                "user-agent": USER_AGENT,
                "accept-language": f"{self._locale},en;q=0.9",
            }
        )
        client.timeout = timeout
        for domain, path, name, value in load_seek_cookies():
            client.cookies.set(name, value, domain=domain, path=path)
        return client

    def close(self) -> None:
        close = getattr(self._http, "close", None)
        if close:
            close()

    def __enter__(self) -> "SeekClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _get_html(self, url: str) -> str:
        resp = self._http.get(url)
        status = getattr(resp, "status_code", None)
        text = getattr(resp, "text", "")
        if status != 200:
            raise TransportError(f"SEEK request failed: HTTP {status} for {url}")
        if "Just a moment..." in text or "cf-mitigated" in text:
            raise TransportError(
                "SEEK anti-bot challenge is still active for this session. Open the same SEEK page in Chrome/OpenClaw browser first, then retry."
            )
        return text

    def _extract_apollo_data(self, html: str) -> dict:
        marker = "window.SEEK_APOLLO_DATA = "
        idx = html.find(marker)
        if idx == -1:
            raise TransportError("Could not find SEEK_APOLLO_DATA in HTML response.")
        payload = html[idx + len(marker):]
        try:
            obj, _ = json.JSONDecoder().raw_decode(payload)
        except Exception as err:
            raise TransportError("Failed to decode SEEK_APOLLO_DATA JSON payload.") from err
        return obj

    def search_jobs(self, keyword: str, location: str = "", page: int = 1) -> SearchResult:
        query = quote_plus(keyword.strip())
        url = f"https://www.seek.co.nz/jobs?keywords={query}"
        if location.strip():
            url += f"&where={quote_plus(location.strip())}"
        if page > 1:
            url += f"&page={page}"
        html = self._get_html(url)
        apollo = self._extract_apollo_data(html)
        return parse_search_apollo(apollo, keyword=keyword, location=location, page=page)

    def get_job_detail(self, job_id: str) -> JobDetail:
        url = f"https://www.seek.co.nz/job/{job_id}"
        html = self._get_html(url)
        apollo = self._extract_apollo_data(html)
        return parse_detail_apollo(apollo, job_id=job_id)
