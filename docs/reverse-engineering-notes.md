# Reverse-engineering notes

## Scope

Read-only only:
- search jobs
- fetch job detail / JD
- export normalized data

## Process

1. inspect SEEK web requests in browser devtools
2. identify search and detail endpoints
3. capture required query params and headers
4. record pagination behavior
5. normalize payload fields into local models
6. avoid account or mutation flows unless explicitly approved later

## Evidence log

### 2026-03-14
- repo scaffold created
- command/documentation surface defined before live endpoint wiring
- confirmed via live browser inspection that SEEK search and detail pages hydrate Apollo state into `window.SEEK_APOLLO_DATA`
- direct unauthenticated `httpx` fetches to `https://www.seek.co.nz/python-jobs` returned Cloudflare / anti-bot `403 Just a moment...`
- this means the likely extraction strategies are now:
  1. normal HTTP with a better browser-session reuse path, or
  2. browser-backed page fetch + Apollo state extraction, or
  3. HTML extraction after obtaining a valid browser-cleared session
- follow-up experiment succeeded with `curl_cffi` impersonation (`chrome136`) plus browser-cookie reuse from the OpenClaw Chrome profile; both search and detail pages returned `200` and preserved `SEEK_APOLLO_DATA`
- conclusion: plain `httpx` is insufficient, but browser-session reuse over an HTTP transport is viable

### Confirmed search-page data shape
- page example: `https://www.seek.co.nz/python-jobs`
- browser globals observed: `SEEK_APOLLO_DATA`, `SEEK_CONFIG`, `SEEK_APP_CONFIG`, `__APOLLO_CLIENT__`
- search result entries are stored under keys like:
  - `JobSearchV6Data:{"id":"90683869","tracking":"..."}`
  - advertiser references under `JobSearchV6Advertiser:<id>`
- sample list fields confirmed on `JobSearchV6Data` objects:
  - `id`
  - `title`
  - `companyName`
  - `locations`
  - `salaryLabel`
  - `teaser`
  - `bulletPoints`
  - `listingDate`
  - `classifications`
  - `advertiser`
  - `roleId`
- card links use URLs shaped like:
  - `https://www.seek.co.nz/job/<job-id>?type=<standard|promoted>&ref=search-standalone...`

### Confirmed detail-page data shape
- page example: `https://www.seek.co.nz/job/90683869?...`
- Apollo cache root contains:
  - `ROOT_QUERY["jobDetails:{\"id\":\"90683869\"}"]`
- confirmed useful fields under that object:
  - `job.id`
  - `job.title`
  - `job.abstract`
  - `job.content({"platform":"WEB"})`  ← HTML JD body
  - `job.salary.label`
  - `job.workTypes.label({"locale":"en-NZ"})`
  - `job.location.label({"locale":"en-NZ","type":"LONG"})`
  - `job.classifications[]`
  - `job.products.bullets[]`
  - `job.shareLink(...)`
  - `companySearchUrl(...)`
  - `workArrangements(...).label(...)`
  - advertiser metadata via `Advertiser:<id>`

### Engineering implication
- SEEK data is not blocked at the rendered page layer once a browser session loads successfully.
- The cleanest MVP may be a **browser-assisted read-only extractor** that:
  1. loads the search or job page,
  2. reads `window.SEEK_APOLLO_DATA`,
  3. normalizes the cache into stable CLI output.
- If later we find a stable internal JSON endpoint behind the page, the client layer can switch transports without changing the CLI surface.

## Notes template for future findings

### Endpoint
- name:
- URL pattern:
- method:
- auth required:
- important headers:
- rate limit observations:

### Request params
- keyword:
- location:
- page:
- sort:
- work type:

### Response mapping
- job id:
- title:
- company:
- location:
- salary:
- teaser:
- jd body:
- listing URL:

### Risks
- anti-bot behavior:
- schema instability:
- missing fields / region-specific behavior:
