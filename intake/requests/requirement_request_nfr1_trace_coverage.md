---
uid: 4f7b6c2e-9a8d-4c4a-b7f1-0e1d2c3b4a5f
type: block
block_type: requirement_request
system: railweb
author: AD
block_name: NFR-1 Trace coverage clarification
in_port: User
out_port: Requirements Manager
priority: medium
impact: important
source: intake
source_path: "intake/requests/requirement_request_nfr1_trace_coverage.md"
date: 2025-09-18
---

# Use case: Trace coverage metric applicability

## Summary

Clarify that the trace coverage metric for audio segments applies only when segments are produced (i.e., when audio generation is enabled and segments exist). If no segments are created (e.g., in dry-run), the metric is not applicable.

## Primary flow (happy path)

1. A run produces audio segments.
2. The system reports trace coverage over created segments.

## Non-goals / constraints

- This clarification does not change how trace coverage is calculated when segments exist.

## Acceptance criteria

- Documentation updated to state: "Trace coverage metric applies only when audio segments exist; in dry-run or when no segments are created, the metric is N/A."

## Implementation notes / suggestions

- Update metrics documentation and any dashboard tooling to hide or mark the metric as N/A when no segments exist for a run.

## Provenance

- Created from advisor note (author: AD) on 2025-09-18.
