# seek-cli

Read-only CLI for SEEK New Zealand job discovery and job-description extraction.

## What it does

- search SEEK NZ jobs from the terminal
- fetch a full job description by job ID or SEEK NZ job URL
- inspect the last cached search result with `seek show`
- export search results to JSON or CSV
- page through multiple search result pages to satisfy larger export counts
- return structured JSON for downstream automation

## What it does not do

- apply for jobs
- message recruiters
- automate account actions
- act as a generic web scraper for arbitrary sites
- guarantee bypass of SEEK anti-bot protection in every environment

## How it works

`seek-cli` uses a read-only HTTP transport built on:
- `browser-cookie3` for local browser cookie reuse
- `curl_cffi` for Chrome-like request impersonation

The current implementation works by reusing an already-valid local browser session, fetching SEEK pages over HTTP, extracting `window.SEEK_APOLLO_DATA`, and normalizing the page data into CLI-friendly output.

This is intentionally not a browser automation workflow for normal use.

## Current scope

This repository currently targets **SEEK New Zealand** pages (`seek.co.nz`).

Implemented commands:
- `search`
- `detail`
- `show`
- `export`

Implemented capabilities:
- live job search
- live detail fetch by job ID
- live detail fetch by SEEK NZ job URL
- cached follow-up lookup with `show`
- multi-page export / collection
- normalized fields including listed time, bullet points, classifications, work arrangement, and company search URL when available

## Install

```bash
uv sync
uv run seek --help
```

## Usage

### Search jobs

```bash
seek search "python"
seek search "data engineer" --location Auckland --page 2
seek search "python" --json
```

### Fetch a job description

```bash
seek detail 90683869
seek detail 'https://www.seek.co.nz/job/90683869?type=standard&ref=search-standalone'
seek detail 90683869 --json
```

### Use cached search results

```bash
seek show 1
seek show 1 --json
```

### Export results

```bash
seek export "python" --count 60 --format json -o jobs.json
seek export "python" --count 60 --format csv -o jobs.csv
```

`export` will keep paging through search results until the requested count is reached or SEEK runs out of results.

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

# export more than one page of results
seek export "python" --count 60 --format json -o jobs.json
```

## Session requirement

The transport expects a local browser cookie store that already contains a valid SEEK session / challenge-cleared state.

Current cookie lookup order:
- OpenClaw browser profile: `~/.openclaw/browser/openclaw/user-data/Default/Cookies`
- Chrome default profile: `~/Library/Application Support/Google/Chrome/Default/Cookies`

If SEEK anti-bot challenge is still active for the current session, open SEEK in Chrome or the OpenClaw browser first, then retry the CLI.

## Output contract

JSON output uses a stable envelope:

```json
{
  "ok": true,
  "schema_version": "1",
  "data": {}
}
```

Notable fields:
- search jobs may include `listed_at`, `bullet_points`, and `classifications`
- detail/show payloads may include `work_arrangement`, `bullet_points`, `classifications`, and `company_search_url`

## Limitations and boundaries

- optimized for local/private use rather than public high-scale scraping
- depends on a valid local browser session
- currently NZ-only; AU support is not claimed
- subject to SEEK frontend and anti-bot changes
- read-only by design

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

skills/
└── seek-cli/
    └── SKILL.md
```

## Documentation

- Architecture: `docs/architecture.md`
- Reverse-engineering notes: `docs/reverse-engineering-notes.md`
- Roadmap: `docs/roadmap.md`
- Changelog: `CHANGELOG.md`

## Bundled AgentSkill

This repository also includes an AgentSkill for using the CLI from agent runtimes:

- `skills/seek-cli/SKILL.md`
