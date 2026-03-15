# Changelog

## 0.1.0 - 2026-03-14

- created initial `seek-cli` scaffold
- added CLI entrypoint and command groups
- added placeholder read-only client abstraction
- added local search index cache for `seek show`
- added README, architecture notes, reverse-engineering notes, and roadmap
- confirmed SEEK search/detail data is exposed in browser Apollo cache (`SEEK_APOLLO_DATA`)
- documented that plain `httpx` requests currently hit anti-bot / Cloudflare `403`
- added parser helpers for normalized search/detail extraction from Apollo cache
- proved a working HTTP transport using `curl_cffi` impersonation plus browser-cookie reuse
- started wiring live search/detail fetches through session-reuse transport
- validated live `show` and `export` flows using the same transport
- updated README with real workflow examples and current capability status
- `seek detail` now accepts either a job id or a SEEK NZ job URL
- added a bundled `seek-cli` AgentSkill under `skills/seek-cli/`
- added multi-page job collection for export flows
- normalized richer fields including listed time, bullet points, classifications, work arrangement, and company search URL
- updated docs and skill guidance to match the new collection/export behavior
