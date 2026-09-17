# BioHarness Architecture Documentation Consolidation Plan

Status: SECOND-PASS HARDENING IN PROGRESS. Runtime/scientific scenarios remain `NOT_RUN`.

> Runtime implementation requires a separate future implementation plan.

## Goal

Keep one short authoritative path and remove semantic ambiguity before runtime implementation starts. The second pass reviews the already-consolidated design as if it were a fresh implementation specification, rather than adding another ADR layer.

## First-pass consolidation completed

- [x] Consolidated review corrections into `scientific-contracts-and-run-semantics.md`.
- [x] Consolidated the real synchronous/local Genome-web provider boundary into the P0 record.
- [x] Merged validation addendum/source-audit scenarios into the primary validation catalog.
- [x] Removed the separate validation addendum from the final branch diff.
- [x] Demoted review/source-audit files to non-authoritative rationale.
- [x] Simplified documentation authority/navigation.
- [x] Added evidence inspection provenance.
- [x] Preserved all runtime/scientific validation scenarios as `NOT_RUN`.

## Second-pass hardening tasks

- [ ] Make authorization action-scoped: protected reads/resolution as well as external side effects require current authorization where policy applies.
- [ ] Remove the planning circularity between `ScientificAssessment` and exact method/configuration selection by binding assessment to explicit candidate method contracts and requiring reassessment when assumption-relevant configuration changes.
- [ ] Separate RunSpec's result-affecting environment contract from RunAttempt's concrete host/scheduler/allocation observations; let the ReproducibilityContract decide which runtime controls enter `analysis_hash`.
- [ ] Define the minimum `Finding` contract and its boundary from Artifact, ValidationReport, Decision, and ResearchMemory.
- [ ] Version ValidationProfiles/gate evaluations so later validation rules do not rewrite historical acceptance.
- [ ] Harmonize the core architecture spec's legacy `Run`, execution-lifecycle, Artifact trust-lifecycle, and Policy wording with the authoritative focused contract.
- [ ] Remove stale Memory examples that imply slot changes are low scientific impact or that bulk -> single-cell can blindly reuse downstream evidence.
- [ ] Make P0 TaskSpec use logical/requested biological scope before `ResolvedDataRef` resolution.
- [ ] Pin the directly audited Genome-web source revision and tighten the current provider capability claims, especially durable execution identity, polling, and cancellation.
- [ ] Keep the validation document as an acceptance-scenario catalog with a required fixture/action/assertion/evidence schema; do not imply an executable harness already exists.
- [ ] Freshly verify final diff scope, authoritative reading path, source revision, and PR status.

## Final Authority Path

```text
core architecture spec
  -> scientific/run contract
  -> P0 vertical slice
  -> scenario validation plan
```

Memory-specific architecture remains in the existing memory records. Evidence and review files do not participate in precedence resolution.