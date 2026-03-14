from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class JobSummary:
    job_id: str
    title: str
    company: str = ""
    location: str = ""
    salary: str = ""
    teaser: str = ""
    work_type: str = ""
    listing_url: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class JobDetail(JobSummary):
    description: str = ""


@dataclass
class SearchResult:
    keyword: str
    location: str
    page: int
    jobs: list[JobSummary]
    total: int | None = None
    has_more: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "keyword": self.keyword,
            "location": self.location,
            "page": self.page,
            "total": self.total,
            "has_more": self.has_more,
            "jobs": [job.to_dict() for job in self.jobs],
        }
