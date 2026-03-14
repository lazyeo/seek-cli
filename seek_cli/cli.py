from __future__ import annotations

import click

from .commands.detail import detail, show
from .commands.export import export
from .commands.search import search


@click.group()
def cli() -> None:
    """Read-only SEEK CLI."""


cli.add_command(search)
cli.add_command(detail)
cli.add_command(show)
cli.add_command(export)


if __name__ == "__main__":
    cli()
