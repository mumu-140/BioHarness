# BioHarness Architecture Documentation Consolidation Plan

Status: documentation consolidation executed on PR #1; runtime/scientific scenarios remain `NOT_RUN`.

> **For agentic workers:** This plan records completed documentation work. Runtime implementation is a separate future plan.

**Goal:** Consolidate all accepted 2026-09-18 review corrections into the authoritative BioHarness contracts so future contributors and agents do not need to traverse a same-PR supersession chain.

**Architecture:** Keep the existing core architecture and focused scientific/run contract as the authoritative semantic layer. Fold review-derived corrections into the authoritative contract, P0 vertical slice, and primary validation plan; retain review/source-audit documents only as non-authoritative rationale/evidence records.

**Spec:** `docs/architecture/scientific-contracts-and-run-semantics.md`

## Global Constraints

- Documentation-only change: no runtime code, database migrations, deployment changes, workflow code changes, or production data mutation.
- Keep the headless Research Control Plane + provider/adapter architecture.
- Do not claim runtime implementation or scientific validation; executable scenarios remain `NOT_RUN`.
- Scientific validity, authorization, execution completion, validation, and canonical publication remain separate concepts.
- Provider capabilities are revision-scoped and may not be fabricated when unsupported.
- Git history preserves prior review wording; authoritative docs contain final semantics rather than a same-PR override chain.

## Completed Documentation Tasks

- [x] Consolidate R1-R11 review corrections into `scientific-contracts-and-run-semantics.md`.
- [x] Keep `ScientificTaskSpec` focused on scientific intent; put provider/method defaults in `ResolvedConfiguration`.
- [x] Separate RunSpec analysis identity from RunAttempt submission identity.
- [x] Require current authorization for every new governed side effect.
- [x] Add typed ValidationReports/ValidationProfiles and ReproducibilityContract.
- [x] Add collection/member identity, untrusted-content boundary, and CAS canonical updates.
- [x] Add revision-scoped WorkflowExecutor capability semantics and safe `UNKNOWN` handling.
- [x] Consolidate P0 against the actual synchronous/local Genome-web Nextflow provider.
- [x] Merge the validation addendum and provider-capability scenarios into `scenario-validation-plan.md`.
- [x] Remove the separate scenario addendum from the final branch diff.
- [x] Demote multi-perspective review and provider source audit to non-authoritative rationale records.
- [x] Simplify `docs/README.md` to a short authoritative reading path.
- [x] Add evidence check-time / inspection-depth / claim-scope metadata.
- [x] Mark the older hardening plan as historical documentation work rather than runtime state.

## Fresh Documentation Verification

- [x] Branch comparison to `main` contains only `docs/**` changes.
- [x] Primary scenario plan contains the merged authorization, attempt, validation, reproducibility, security, canonical, collection, and P0 capability cases.
- [x] Authoritative contract contains the accepted review corrections.
- [x] P0 explicitly states `synchronous_process` / `local` and does not claim remote exactly-once semantics.
- [x] Review/source-audit records explicitly state that they are non-authoritative.
- [x] Runtime/scientific acceptance remains `NOT_RUN`.
- [x] PR remains Draft pending the next independent source/review pass.
