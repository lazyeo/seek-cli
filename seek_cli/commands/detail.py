from __future__ import annotations

import re
from urllib.parse import urlparse

import click
from rich.panel import Panel

from ..client import SeekClient
from ..index_cache import get_job_by_index
from ._common import console, emit_data, fail, structured_output_options


def _coerce_job_id(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"\d+", value):
        return value

    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc.endswith("seek.co.nz"):
        match = re.search(r"/job/(\d+)", parsed.path)
        if match:
            return match.group(1)

    raise click.ClickException("Expected a SEEK job id or a SEEK NZ job URL.")


@click.command()
@click.argument("job_id_or_url")
@structured_output_options
def detail(job_id_or_url: str, as_json: bool) -> None:
    """Show job detail by ID or SEEK NZ job URL."""
    try:
        job_id = _coerce_job_id(job_id_or_url)
        with SeekClient() as client:
            job = client.get_job_detail(job_id)

        payload = job.to_dict()
        if as_json:
            emit_data(payload, as_json=True)
            return

        console.print(
            Panel(
                f"[bold cyan]{job.title}[/bold cyan]\n"
                f"{job.company} · {job.location}\n"
                f"Salary: {job.salary or '-'}\n"
                f"Type: {job.work_type or '-'}\n\n"
                f"{job.description}",
                title="Job detail",
                border_style="cyan",
            )
        )
    except Exception as err:
        fail(err)


@click.command()
@click.argument("index", type=int)
@structured_output_options
def show(index: int, as_json: bool) -> None:
    """Show detail for a job in the cached last search result."""
    try:
        job = get_job_by_index(index)
        if not job:
            raise click.ClickException("No cached result at that index. Run `seek search` first.")

        with SeekClient() as client:
            detail_result = client.get_job_detail(job.job_id)

        payload = detail_result.to_dict()
        if as_json:
            emit_data(payload, as_json=True)
            return

        console.print(
            Panel(
                f"[bold cyan]{detail_result.title}[/bold cyan]\n"
                f"{detail_result.company} · {detail_result.location}\n\n"
                f"{detail_result.description}",
                title=f"Cached result #{index}",
                border_style="green",
            )
        )
    except Exception as err:
        fail(err)
