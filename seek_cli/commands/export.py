from __future__ import annotations

import csv
import json
from pathlib import Path

import click

from ..client import SeekClient
from ._common import fail


@click.command(name="export")
@click.argument("keyword")
@click.option("--location", default="", help="Location filter")
@click.option("--page", default=1, type=int, help="Page number")
@click.option("--count", default=20, type=int, help="Target number of jobs to export")
@click.option("--format", "fmt", type=click.Choice(["json", "csv"]), default="json")
@click.option("-o", "--output", "output_path", required=True, help="Output file path")
def export(keyword: str, location: str, page: int, count: int, fmt: str, output_path: str) -> None:
    """Export normalized search results."""
    try:
        with SeekClient() as client:
            result = client.search_jobs(keyword=keyword, location=location, page=page)

        jobs = [job.to_dict() for job in result.jobs[:count]]
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if fmt == "json":
            path.write_text(json.dumps(jobs, ensure_ascii=False, indent=2))
        else:
            with path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=list(jobs[0].keys()) if jobs else ["job_id", "title"])
                writer.writeheader()
                writer.writerows(jobs)

        click.echo(f"Exported {len(jobs)} jobs to {path}")
        if len(jobs) < count:
            click.echo(
                f"Note: only {len(jobs)} jobs were available from the current fetched page/search result.",
                err=True,
            )
    except Exception as err:
        fail(err)
