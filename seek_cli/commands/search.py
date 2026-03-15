from __future__ import annotations

import click
from rich.table import Table

from ..client import SeekClient
from ..index_cache import save_search
from ._common import console, emit_data, fail, structured_output_options


@click.command()
@click.argument("keyword")
@click.option("--location", default="", help="Location filter")
@click.option("--page", default=1, type=int, help="Page number")
@structured_output_options
def search(keyword: str, location: str, page: int, as_json: bool) -> None:
    """Search SEEK jobs (prototype)."""
    try:
        with SeekClient() as client:
            result = client.search_jobs(keyword=keyword, location=location, page=page)
        save_search(result)

        payload = result.to_dict()
        if as_json:
            emit_data(payload, as_json=True)
            return

        table = Table(title=f"SEEK search: {keyword}")
        table.add_column("#", style="dim", width=3)
        table.add_column("Title", style="cyan")
        table.add_column("Company", style="green")
        table.add_column("Location")
        table.add_column("Salary", style="yellow")
        table.add_column("Listed", style="magenta", width=8)

        for i, job in enumerate(result.jobs, start=1):
            table.add_row(str(i), job.title, job.company, job.location, job.salary, job.listed_at or "-")

        console.print(table)
        if result.total is not None:
            console.print(f"[dim]Approx total results: {result.total} · page {result.page}[/dim]")
        console.print("[dim]Use `seek show <index>` to view cached detail lookup targets.[/dim]")
    except Exception as err:
        fail(err)
