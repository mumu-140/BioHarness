# BioHarness Scientific Contract Hardening Documentation Plan

Status: Historical documentation plan. The architecture-hardening tasks were executed in PR #1 and later consolidated by `docs/superpowers/plans/2026-09-18-documentation-consolidation.md`. Runtime/scientific validation remains `NOT_RUN`.

> This file is retained as planning history only. Current authoritative semantics are in `docs/architecture/scientific-contracts-and-run-semantics.md`, `docs/architecture/p0-genome-web-tf-vertical-slice.md`, and `docs/architecture/scenario-validation-plan.md`.

## Original Goal

Repair the BioHarness architecture records so scientific validity, authority, data identity, invalidation, execution recovery, and memory promotion have explicit non-conflicting semantics before implementation starts.

## Original Architecture Direction

Keep the existing headless Research Control Plane, provider/adapter boundaries, evidence-backed memory, and external workflow engines. Add explicit scientific/run contracts and validate the design against the existing Genome-web TF Nextflow pilot as the first real-world vertical slice.

## Global Constraints

- Documentation-only change: no application code, database migration, deployment, or production data mutation.
- Existing mature scientific algorithms and workflow engines remain external providers.
- Scientific validity and execution success remain independent.
- Memory cannot directly become Policy or Canonical state.
- Every proposed P0 runtime behavior must be testable against a concrete failure or recovery scenario.
- Validation scenarios are `NOT_RUN` until a future implementation executes them.

## Documentation Tasks

- [x] Establish a documentation authority/navigation map.
- [x] Define scientific and execution contracts.
- [x] Add an evidence/reference register.
- [x] Define the Genome-web TF P0 vertical slice.
- [x] Define executable validation scenarios.
- [x] Perform cross-document review and open Draft PR #1.
- [x] Perform multi-perspective architecture review.
- [x] Perform source-level audit of the selected P0 Genome-web TF provider.
- [x] Consolidate review corrections back into authoritative contracts.

## Runtime Tasks

These were never part of the documentation phase and remain intentionally unexecuted:

- [ ] Implement BioHarness runtime/control-plane objects.
- [ ] Implement Genome-web Data Provider adapter.
- [ ] Implement the P0 local Nextflow WorkflowExecutor adapter.
- [ ] Execute `scenario-validation-plan.md` acceptance scenarios.
- [ ] Record fresh runtime/scientific validation evidence.

No unchecked runtime item in this historical plan should be interpreted as a documentation blocker for PR #1.
