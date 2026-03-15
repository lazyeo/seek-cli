from __future__ import annotations

from html import unescape
import re
from typing import Any

from .models import JobDetail, JobSummary, SearchResult


def _first_non_empty(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def parse_search_apollo(
    apollo_data: dict[str, Any],
    keyword: str,
    location: str = "",
    page: int = 1,
    total: int | None = None,
) -> SearchResult:
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
            location_label = _first_non_empty(first.get("label"), first.get("description"), first.get("whereValue"))

        listing_date = value.get("listingDate") or {}
        listed_at = _first_non_empty(
            listing_date.get('label({"context":"JOB_POSTED","length":"SHORT","locale":"en-NZ","timezone":"Pacific/Auckland"})'),
            listing_date.get("label"),
        )

        classifications: list[str] = []
        for item in value.get("classifications") or []:
            if not isinstance(item, dict):
                continue
            parts = []
            classification_ref = (item.get("classification") or {}).get("__ref")
            subclassification_ref = (item.get("subclassification") or {}).get("__ref")
            if classification_ref and classification_ref in apollo_data:
                parts.append(apollo_data[classification_ref].get("description") or "")
            if subclassification_ref and subclassification_ref in apollo_data:
                parts.append(apollo_data[subclassification_ref].get("description") or "")
            label = " / ".join([p for p in parts if p])
            if label:
                classifications.append(label)

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
                listed_at=listed_at,
                listing_url=listing_url,
                bullet_points=list(value.get("bulletPoints") or []),
                classifications=classifications,
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

    has_more = None
    if total is not None:
        has_more = page * max(len(deduped), 1) < total

    return SearchResult(keyword=keyword, location=location, page=page, jobs=deduped, total=total, has_more=has_more)


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
    listed_at_obj = job.get("listedAt") or {}
    work_arrangements = {}
    for key_name, value in details.items():
        if key_name.startswith("workArrangements(") and isinstance(value, dict):
            work_arrangements = value
            break
    description = _html_to_text(job.get('content({"platform":"WEB"})') or "")
    company = advertiser.get('name({"locale":"en-NZ"})') or ""
    listed_at = _first_non_empty(
        listed_at_obj.get('label({"context":"JOB_POSTED","length":"SHORT","locale":"en-NZ","timezone":"Pacific/Auckland"})'),
        listed_at_obj.get("label"),
    )
    classifications = [
        item.get('label({"languageCode":"en"})')
        for item in (job.get("classifications") or [])
        if isinstance(item, dict) and item.get('label({"languageCode":"en"})')
    ]
    work_arrangement = _first_non_empty(
        work_arrangements.get('label({"locale":"en-NZ"})'),
        details.get("seoInfo", {}).get("workType"),
    )
    company_search_url = details.get('companySearchUrl({"languageCode":"en","zone":"anz-2"})') or ""

    return JobDetail(
        job_id=str(job.get("id") or job_id),
        title=job.get("title") or "",
        company=company,
        location=location_obj.get('label({"locale":"en-NZ","type":"LONG"})') or "",
        salary=salary,
        teaser=job.get("abstract") or "",
        work_type=work_types.get('label({"locale":"en-NZ"})') or "",
        work_arrangement=work_arrangement,
        listed_at=listed_at,
        listing_url=f"https://www.seek.co.nz/job/{job_id}",
        bullet_points=list(products.get("bullets") or []),
        classifications=classifications,
        description=description,
        tags=list(products.get("bullets") or []),
        company_search_url=company_search_url,
    )
