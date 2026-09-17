# BioHarness Architecture Documentation Consolidation Plan

Status: COMPLETE for documentation scope. Runtime/scientific scenarios remain `NOT_RUN`.

> Runtime implementation requires a separate future implementation plan.

## Goal

Consolidate accepted 2026-09-18 review corrections into authoritative BioHarness contracts so future contributors and agents do not need to traverse a same-PR supersession chain.

## Completed

- [x] Consolidated review corrections into `scientific-contracts-and-run-semantics.md`.
- [x] Consolidated the real synchronous/local Genome-web provider boundary into the P0 record.
- [x] Merged validation addendum/source-audit scenarios into the primary validation catalog.
- [x] Removed the separate validation addendum from the final branch diff.
- [x] Demoted review/source-audit files to non-authoritative rationale.
- [x] Simplified documentation authority/navigation.
- [x] Added evidence inspection provenance.
- [x] Marked the older hardening plan as historical documentation work.
- [x] Confirmed final branch changes remain documentation-only.
- [x] Preserved all runtime/scientific validation scenarios as `NOT_RUN`.

## Final Authority Path

```text
core architecture spec
  -> scientific/run contract
  -> P0 vertical slice
  -> scenario validation plan
```

Memory-specific architecture remains in the existing memory records. Evidence and review files do not participate in precedence resolution.
