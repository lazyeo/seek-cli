from __future__ import annotations

import json
from typing import Any, Callable

import click
from rich.console import Console

from ..constants import SCHEMA_VERSION
from ..exceptions import SeekCliError

console = Console(stderr=True)


def structured_output_options(func: Callable[..., Any]) -> Callable[..., Any]:
    func = click.option("--json", "as_json", is_flag=True, help="Emit JSON envelope.")(func)
    return func


def emit_data(data: dict[str, Any], as_json: bool) -> None:
    if as_json:
        click.echo(json.dumps({"ok": True, "schema_version": SCHEMA_VERSION, "data": data}, ensure_ascii=False, indent=2))
        return


def fail(err: Exception) -> None:
    if isinstance(err, SeekCliError):
        raise click.ClickException(str(err)) from err
    raise click.ClickException(f"Unexpected error: {err}") from err
