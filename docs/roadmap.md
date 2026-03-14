# Roadmap

## Phase 1 - Scaffold
- [x] project layout
- [x] CLI command skeleton
- [x] documentation baseline
- [x] cache and output envelope

## Phase 2 - Endpoint discovery
- [x] inspect SEEK search page runtime data
- [x] inspect SEEK detail page runtime data
- [ ] inspect background GraphQL / JSON requests if accessible
- [ ] confirm parameter names and pagination
- [x] document first-pass field mappings
- [x] record anti-bot constraint on direct HTTP fetches

## Phase 2.5 - Transport choice
- [x] prove viable HTTP session reuse path with browser-like fingerprinting
- [ ] harden cookie-source discovery and error handling
- [ ] implement one live transport behind `SeekClient`

## Phase 3 - Read-only MVP
- [ ] implement live `search`
- [ ] implement live `detail`
- [ ] support `show` from cached results
- [ ] support JSON export
- [ ] support CSV export

## Phase 4 - Hardening
- [ ] retry/backoff policy
- [ ] fixture-based tests for normalization
- [ ] UX polish for filters and empty states
- [ ] schema versioning notes

## Explicitly out of scope for now
- applying for jobs
- recruiter chat
- saved jobs sync
- account automation
