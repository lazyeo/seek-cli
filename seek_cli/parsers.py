from __future__ import annotations

from html import unescape
import re
from typing import Any

from .models import JobDetail, JobSummary, SearchResult


def parse_search_apollo(apollo_data: dict[str, Any], keyword: str, location: str = "", page: int = 1) -> SearchResult:
    """Normalize SEEK search-page Apollo cache into SearchResult.

    This parser is transport-agnostic: the caller can obtain the Apollo cache
    from browser extraction, saved fixtures, or a future HTTP pathway.
    """
    jobs: list[JobSummary] = []

    for key, value in apollo_data.items():
        if not key.startswith("JobSearchV6Data:") or not isinstance(value, dict):
            continue

        job_id = str(value.get("id") or "")
        if not job_id:
            continue

        locations = value.get("locations") or []
        location_label = ""
        if locations:
            first = locations[0] or {}
            location_label = first.get("label") or first.get("description") or first.get("whereValue") or ""

        listing_url = f"https://www.seek.co.nz/job/{job_id}"
        jobs.append(
            JobSummary(
                job_id=job_id,
                title=value.get("title") or "",
                company=value.get("companyName") or "",
                location=location_label,
                salary=value.get("salaryLabel") or "",
                teaser=value.get("teaser") or "",
                work_type=value.get("workType") or "",
                listing_url=listing_url,
                tags=[t.get("label", "") if isinstance(t, dict) else str(t) for t in (value.get("tags") or []) if t],
            )
        )

    # same job can appear more than once with different tracking tokens; keep first occurrence
    deduped: list[JobSummary] = []
    seen: set[str] = set()
    for job in jobs:
        if job.job_id in seen:
            continue
        seen.add(job.job_id)
        deduped.append(job)

    return SearchResult(keyword=keyword, location=location, page=page, jobs=deduped, total=None, has_more=None)


def _html_to_text(value: str) -> str:
    text = value.replace("<br />", "\n").replace("<br/>", "\n").replace("<br>", "\n")
    text = re.sub(r"</(p|div|li|h[1-6]|ul|ol|strong)>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_detail_apollo(apollo_data: dict[str, Any], job_id: str) -> JobDetail:
    """Normalize SEEK detail-page Apollo cache into JobDetail."""
    root = apollo_data.get("ROOT_QUERY") or {}
    key = f'jobDetails:{{"id":"{job_id}"}}'
    details = root.get(key) or {}
    job = details.get("job") or {}

    salary = (job.get("salary") or {}).get("label") or ""
    location_obj = job.get("location") or {}
    work_types = job.get("workTypes") or {}
    advertiser_ref = (job.get("advertiser") or {}).get("__ref")
    advertiser = apollo_data.get(advertiser_ref, {}) if advertiser_ref else {}
    products = job.get("products") or {}
    description = _html_to_text(job.get('content({"platform":"WEB"})') or "")
    company = advertiser.get('name({"locale":"en-NZ"})') or ""

    return JobDetail(
        job_id=str(job.get("id") or job_id),
        title=job.get("title") or "",
        company=company,
        location=location_obj.get('label({"locale":"en-NZ","type":"LONG"})') or "",
        salary=salary,
        teaser=job.get("abstract") or "",
        work_type=work_types.get('label({"locale":"en-NZ"})') or "",
        listing_url=f"https://www.seek.co.nz/job/{job_id}",
        description=description,
        tags=list(products.get("bullets") or []),
    )
