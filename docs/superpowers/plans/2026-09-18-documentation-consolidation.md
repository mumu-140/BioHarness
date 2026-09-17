# BioHarness Architecture Documentation Consolidation Plan

Status: COMPLETE for documentation/design scope. Runtime/scientific scenarios remain `NOT_RUN`.

> Runtime implementation requires a separate future implementation plan.

## Goal

Keep one short authoritative path and remove semantic ambiguity before runtime implementation starts. The second pass reviewed the already-consolidated design as a fresh implementation specification rather than adding another ADR layer.

## First-pass consolidation

- [x] Consolidated review corrections into `scientific-contracts-and-run-semantics.md`.
- [x] Consolidated the real synchronous/local Genome-web provider boundary into the P0 record.
- [x] Merged validation addendum/source-audit scenarios into the primary scenario catalog.
- [x] Removed the separate validation addendum from the final branch diff.
- [x] Demoted review/source-audit files to non-authoritative rationale.
- [x] Simplified documentation authority/navigation.
- [x] Added evidence inspection provenance.
- [x] Preserved all runtime/scientific validation scenarios as `NOT_RUN`.

## Second-pass hardening

- [x] Made authorization action/resource-scoped, including protected reads/resolution where policy applies.
- [x] Bound `ScientificAssessment` to explicit TaskSpec/data/method-contract dependencies and require reassessment when assumption-relevant configuration changes.
- [x] Separated RunSpec result-affecting environment contracts from RunAttempt concrete host/scheduler/allocation observations; ReproducibilityContract determines result-affecting runtime identity.
- [x] Defined the minimum evidence-linked `Finding` contract and its boundary from Artifact, ValidationReport, Decision, ResearchMemory, and CanonicalPointer.
- [x] Versioned ValidationProfiles/gate evaluations so later validation rules do not rewrite historical acceptance.
- [x] Harmonized the core architecture spec with RunSpec/RunAttempt, immutable Artifact, typed validation, Finding, Decision, and canonical-state semantics.
- [x] Removed stale memory semantics that treated adaptive-slot change as low scientific impact or bulk -> single-cell topology as sufficient downstream reuse evidence.
- [x] Made P0 TaskSpec use requested/logical biological scope before `ResolvedDataRef` resolution.
- [x] Pinned the audited Genome-web TF provider revision to `05072cbbcd533ca59afa13996d8d0edd8f939c6e` and tightened capability claims for execution identity, polling, resume, reconciliation, and cancellation.
- [x] Reframed `scenario-validation-plan.md` as an acceptance-scenario catalog with required fixture/action/assertion/evidence metadata; it is not an executable harness.
- [x] Performed fresh source/diff verification; all branch changes remain under `docs/**` and runtime/scientific scenarios remain `NOT_RUN`.

## Final Authority Path

```text
core architecture spec
  -> scientific/run contract
  -> P0 vertical slice
  -> acceptance-scenario catalog
  -> memory architecture records when relevant
```

Evidence and review/audit records do not participate in precedence resolution.

## Handoff Boundary

This plan closes documentation/design hardening only. It does not prove runtime correctness. The next implementation phase must create a separate P0 implementation plan and execute the acceptance scenarios with fresh evidence.