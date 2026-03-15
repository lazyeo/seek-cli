---
name: seek-cli
description: Read-only SEEK New Zealand job search and job-description extraction via the local `seek` CLI. Use when you need to search SEEK jobs, fetch a SEEK job description from a job id or SEEK NZ job URL, inspect a cached search result with `seek show`, or export SEEK search results to JSON/CSV across multiple pages. Prefer this skill over browser automation when the task is specifically about SEEK NZ listings and JD extraction.
---

# seek-cli Skill

Use the local `seek` CLI from this repository for SEEK NZ job discovery and JD extraction.

## Use this skill

- Run from the repository root so `uv run python -m seek_cli.cli ...` works.
- Prefer CLI extraction over browser automation for SEEK NZ pages.
- Use `--json` whenever the result will be consumed by another tool or model.
- Expect the transport to depend on a valid local browser session/cookie store.

## Core commands

### Search jobs

```bash
uv run python -m seek_cli.cli search "python"
uv run python -m seek_cli.cli search "data engineer" --location Auckland --page 2
uv run python -m seek_cli.cli search "python" --json
```

### Fetch a job description

```bash
uv run python -m seek_cli.cli detail 90683869
uv run python -m seek_cli.cli detail 'https://www.seek.co.nz/job/90683869?type=standard&ref=search-standalone'
uv run python -m seek_cli.cli detail 90683869 --json
```

### Use cached search results

```bash
uv run python -m seek_cli.cli show 1
uv run python -m seek_cli.cli show 1 --json
```

### Export results

```bash
uv run python -m seek_cli.cli export "python" --count 60 --format json -o jobs.json
uv run python -m seek_cli.cli export "python" --count 60 --format csv -o jobs.csv
```

`export` can page through multiple search result pages to satisfy larger `--count` values.

## Output expectations

When `--json` is used, expect this envelope:

```json
{
  "ok": true,
  "schema_version": "1",
  "data": {}
}
```

Important payload shapes:
- `search`: `data.jobs[]` contains normalized job summaries
- `detail` / `show`: `data.description` contains the extracted JD text

## Session and transport notes

- The CLI uses browser-cookie session reuse plus `curl_cffi` impersonation.
- It is read-only.
- If SEEK anti-bot challenge is still active, first open SEEK in Chrome or the OpenClaw browser and retry.
- Current cookie lookup order is documented in `README.md`.

## When to fall back to something else

Do not use this skill for:
- non-SEEK websites
- recruiter messaging or job applications
- arbitrary webpage cleanup where a generic extractor is better
- AU/global support assumptions that are not yet implemented in this repo

Use browser automation only when:
- the target is not SEEK NZ, or
- the local CLI transport fails and the user explicitly wants a browser-based workaround
