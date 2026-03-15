# Architecture

## Purpose

`seek-cli` is a read-only command-line interface for SEEK job discovery. The first iteration optimizes for stable local tooling and clear documentation before wiring up live network integration.

## Layers

### 1. CLI layer
- built with Click
- parses user arguments
- delegates to client/actions
- renders Rich tables for humans
- emits envelope JSON for scripts

### 2. Client layer
- owns HTTP transport
- hides endpoint details from commands
- normalizes request params and response payloads
- should later support retries, backoff, and endpoint version changes

### 3. Model / normalization layer
- converts raw SEEK payloads into stable CLI-friendly shapes
- protects command UX from upstream schema churn

### 4. Cache layer
- stores the last search result set locally
- enables `seek show <index>` without retyping IDs

### 5. Export layer
- writes normalized records to JSON/CSV

## Initial command surface

- `seek search`
- `seek detail`
- `seek show`
- `seek export`

## Data flow

1. User runs command
2. Click parses options
3. Command calls `SeekClient`
4. Client fetches one or more SEEK pages over the session-reuse transport
5. Client extracts `SEEK_APOLLO_DATA` (and when available `SEEK_REDUX_DATA`)
6. Parser normalizes the payload into local models
7. Command either:
   - renders Rich output to terminal, or
   - emits `{ok, schema_version, data}` JSON envelope
8. Search results are cached for follow-up `show`

## Multi-page collection

`export` now collects jobs across multiple search pages until:
- the requested `--count` is satisfied,
- SEEK reports there are no more results, or
- repeated/empty pages suggest collection is exhausted.

Deduplication is done on `job_id`, because SEEK can emit the same listing multiple times with different tracking tokens.

## Documentation policy

When new endpoint knowledge is discovered, update both:
- `docs/reverse-engineering-notes.md`
- relevant command examples in `README.md`

When public CLI behavior changes, also update:
- `CHANGELOG.md`
- any examples affected by the change

## Planned live integration concerns

- pagination
- request headers / anti-bot handling
- upstream field variability
- location and work-type filters
- careful rate limiting
- graceful degradation if SEEK changes response shapes

## Transport strategy note

Current evidence suggests plain HTTP requests hit SEEK anti-bot protection quickly, while a real browser session can load the page and expose structured Apollo cache data in `window.SEEK_APOLLO_DATA`.

So the client layer should be designed to support more than one transport:

1. **HTTP transport**
   - preferred if we can reliably reuse a cleared browser session or stable endpoint
   - current best candidate: `curl_cffi` browser impersonation + browser-cookie reuse
2. **Browser-backed transport**
   - open page in a real browser context
   - extract hydrated Apollo cache
   - normalize into local models

The CLI surface should stay the same regardless of transport. That is why normalization stays separate from transport.
