# seek-cli

A documentation-first, read-only CLI for SEEK job discovery.

## Status

Prototype scaffold. This repo currently provides:
- command structure
- HTTP client abstraction
- local index cache for `seek show`
- JSON output envelope
- documentation for implementation and reverse-engineering workflow

Live SEEK endpoint integration is intentionally not wired up yet; first we lock the interface and docs.

Current discovery status:
- SEEK pages load successfully in a real browser session
- page data is hydrated into `window.SEEK_APOLLO_DATA`
- direct `httpx` requests hit anti-bot / Cloudflare `403` responses
- **working breakthrough:** `curl_cffi` browser impersonation + browser-cookie reuse can fetch SEEK HTML with status 200 and Apollo data intact
- this keeps the MVP on the HTTP/session-reuse path instead of requiring full browser extraction

## Goals

- Search SEEK jobs from the terminal
- View job details / JD text
- Export results as JSON or CSV
- Keep human-readable Rich output and machine-friendly JSON output
- Stay read-only

## Non-goals

- Applying for jobs
- Messaging recruiters
- Account automation
- Hidden browser automation as a default path

## Commands

```bash
seek search "python"
seek search "data engineer" --location Auckland --page 2
seek detail 90683869
seek detail 'https://www.seek.co.nz/job/90683869?type=standard&ref=search-standalone'
seek show 3
seek export "backend engineer" --location Wellington --count 100 --format json -o jobs.json
```

## What works now

- live `search` against SEEK NZ pages
- live `detail` by job ID
- `show` using the cached last search result
- `export` to JSON and CSV

## Example workflow

```bash
# search live results
seek search "python"

# inspect a known job directly by id
seek detail 90683869

# or pass a SEEK NZ job URL directly
seek detail 'https://www.seek.co.nz/job/90683869?type=standard&ref=search-standalone'

# inspect the first job from your last search
seek show 1

# export current search space
seek export "python" --format json -o jobs.json
seek export "python" --format csv -o jobs.csv
```

## Install

```bash
uv sync
uv run seek --help
```

## Session reuse requirement

The current transport expects a local browser cookie store that already has a valid SEEK session / challenge-cleared state.

Current cookie lookup order:
- OpenClaw browser profile: `~/.openclaw/browser/openclaw/user-data/Default/Cookies`
- Chrome default profile: `~/Library/Application Support/Google/Chrome/Default/Cookies`

Transport stack:
- `browser-cookie3` for cookie extraction
- `curl_cffi` for Chrome-like HTTP fingerprinting

## Output contract

JSON output uses a stable envelope:

```json
{
  "ok": true,
  "schema_version": "1",
  "data": {}
}
```

## Project layout

```text
seek_cli/
├── cli.py
├── client.py
├── constants.py
├── exceptions.py
├── index_cache.py
├── models.py
└── commands/
    ├── __init__.py
    ├── _common.py
    ├── detail.py
    ├── export.py
    └── search.py

docs/
├── architecture.md
├── reverse-engineering-notes.md
└── roadmap.md
```

## Documentation

- Architecture: `docs/architecture.md`
- Reverse-engineering notes: `docs/reverse-engineering-notes.md`
- Roadmap: `docs/roadmap.md`
- Changelog: `CHANGELOG.md`

## Development principles

1. Docs move with code.
2. Reverse-engineering findings get written down immediately.
3. Keep transport, parsing, rendering, and command UX separate.
4. Preserve a read-only scope unless explicitly expanded.
