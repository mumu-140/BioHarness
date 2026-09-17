# BioHarness Scientific Contract Hardening Documentation Plan

Status: HISTORICAL / SUPERSEDED BY CONSOLIDATED DESIGN

> This file records the original documentation-hardening work that led to PR #1. It is not authoritative architecture and not runtime evidence. Final semantics live in the authoritative docs listed by `docs/README.md`.

## Goal

Repair the BioHarness architecture records so scientific validity, authority, data identity, invalidation, execution recovery, and memory promotion have explicit non-conflicting semantics before implementation starts.

## Architecture

Keep the existing headless Research Control Plane, provider/adapter boundaries, evidence-backed memory, and external workflow engines. Add explicit scientific/run contracts and validate the design against the existing Genome-web TF Nextflow pilot as the first real-world vertical slice.

## Historical documentation tasks

- [x] Establish a documentation authority/navigation map.
- [x] Add scientific intent, feasibility, authorization, data identity, and Run semantics.
- [x] Define dependency-aware revalidation instead of mutation-label heuristics.
- [x] Separate RunSpec, RunAttempt, Artifact, validation, Decision/canonical state.
- [x] Define provider capability honesty and safe uncertain-execution behavior.
- [x] Record external/internal architecture evidence and adoption boundaries.
- [x] Select the existing Genome-web TF Nextflow pilot as P0.
- [x] Create architecture acceptance scenarios and preserve them as `NOT_RUN`.
- [x] Perform multi-perspective review and fold accepted findings back into authoritative docs.
- [x] Consolidate same-PR correction layers into final authoritative contracts.

## Handoff

This historical plan does not authorize runtime implementation and does not claim that any acceptance scenario has executed.

Current implementation planning must start from:

```text
docs/README.md
  -> core architecture spec
  -> scientific/run contract
  -> P0 vertical slice
  -> acceptance-scenario catalog
```
