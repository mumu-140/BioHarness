# BioHarness Architecture Documentation Consolidation Plan

Status: documentation consolidation executed on PR #1; runtime/scientific scenarios remain `NOT_RUN`.

> This plan is complete as documentation work. Runtime implementation requires a separate future plan.

**Goal:** Consolidate all accepted 2026-09-18 review corrections into the authoritative BioHarness contracts so future contributors and agents do not need to traverse a same-PR supersession chain.

**Architecture:** Keep the core architecture and scientific/run contract authoritative. Fold review-derived corrections into the authoritative contract, P0 vertical slice, and primary validation plan; retain review/source-audit files only as non-authoritative rationale/evidence.

## Constraints Preserved

- Documentation only; no runtime code, migrations, deployment, workflow-code, or production-data changes.
- Headless Research Control Plane + provider/adapter architecture retained.
- Runtime/scientific scenarios remain `NOT_RUN`.
- Scientific validity, authorization, execution completion, validation, and canonical publication remain separate.
- Provider capabilities are revision-scoped and cannot be fabricated.

## Completed Work

- [x] Consolidated R1-R11 into `scientific-contracts-and-run-semantics.md`.
- [x] Separated TaskSpec scientific intent from ResolvedConfiguration method/provider defaults.
- [x] Separated RunSpec analysis identity from RunAttempt submission identity.
- [x] Added current-side-effect authorization, typed validation, reproducibility, trust boundaries, collection identity, and CAS canonical updates.
- [x] Added revision-scoped WorkflowExecutor capability semantics and safe unknown-state handling.
- [x] Consolidated P0 against the actual synchronous/local Genome-web Nextflow provider.
- [x] Merged the former validation addendum/source-audit scenarios into the primary scenario plan.
- [x] Removed the separate validation addendum from the final branch diff.
- [x] Demoted review/source-audit files to non-authoritative rationale records.
- [x] Simplified `docs/README.md` to the final authority path.
- [x] Added evidence inspection provenance metadata.
- [x] Marked the older hardening plan as historical documentation work.

## Fresh Verification Recorded

- [x] Final branch diff remains `docs/**` only.
- [x] The primary scenario plan contains the merged review/source-audit acceptance cases.
- [x] The authoritative contract contains the accepted corrections.
- [x] P0 explicitly models the current `synchronous_process` / `local` provider and does not claim remote exactly-once semantics.
- [x] Review/source-audit records state that they are non-authoritative.
- [x] Runtime/scientific acceptance remains `NOT_RUN`.
- [x] PR remains Draft for the next independent review pass.
