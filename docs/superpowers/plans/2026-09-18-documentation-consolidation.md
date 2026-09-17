# BioHarness Architecture Documentation Consolidation Plan

Status: documentation tasks executed on PR #1; runtime/scientific scenarios remain `NOT_RUN`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Consolidate all accepted 2026-09-18 review corrections into the authoritative BioHarness contracts so future contributors and agents do not need to traverse a same-PR supersession chain.

**Architecture:** Keep the existing core architecture and focused scientific/run contract as the authoritative semantic layer. Fold review-derived corrections into the authoritative contract, P0 vertical slice, and primary validation plan; retain review/source-audit documents only as non-authoritative rationale/evidence records.

**Tech Stack:** Markdown architecture records, Git/GitHub review, existing Genome-web TF Nextflow source as the P0 reference implementation.

**Spec:** `docs/architecture/scientific-contracts-and-run-semantics.md`

## Global Constraints

- Documentation-only change: no runtime code, database migrations, deployment changes, workflow code changes, or production data mutation.
- Keep the headless Research Control Plane + provider/adapter architecture.
- Do not claim runtime implementation or scientific validation; executable scenarios remain `NOT_RUN`.
- Scientific validity, authorization, execution completion, validation, and canonical publication remain separate concepts.
- Provider capabilities are revision-scoped and may not be fabricated when unsupported.
- Git history preserves prior review wording; authoritative docs should contain the final semantics rather than a chain of same-PR overrides.

---

### Task 1: Consolidate the scientific/run contract

**Files:**
- Modified: `docs/architecture/scientific-contracts-and-run-semantics.md`

- [x] Replace pre-execution `SUPPORTED` terminology with `ANALYSIS_SUPPORTED` vocabulary.
- [x] Move provider submission identity from RunSpec to RunAttempt (`submission_key`).
- [x] Add current-side-effect authorization separate from historical ContextSnapshot/PolicyDecision.
- [x] Add typed `ValidationReport` and `ValidationProfile` semantics.
- [x] Add `ReproducibilityContract`.
- [x] Add explicit untrusted-content rule.
- [x] Add revision-checked CanonicalPointer mutation.
- [x] Extend `ResolvedDataRef` for composite collection/manifest identity.
- [x] Add revision-scoped `WorkflowExecutorCapabilitySnapshot` and limited-reconciliation semantics.
- [x] Clarify engine-internal retry versus BioHarness RunAttempt.
- [x] Update architecture invariants and P0 boundary.

### Task 2: Consolidate the P0 vertical slice

**Files:**
- Modified: `docs/architecture/p0-genome-web-tf-vertical-slice.md`

- [x] Remove ordinary method parameters from ScientificTaskSpec and place them in ResolvedConfiguration.
- [x] Record the actual local/synchronous executor capability boundary.
- [x] Require resolved-manifest/member provenance.
- [x] Require typed provider/candidate validation rather than a generic PASS.
- [x] Narrow uncertain-execution recovery to capability-driven reconciliation and `NEEDS_OPERATOR_RECONCILIATION` where necessary.
- [x] Keep production publication out of P0.

### Task 3: Consolidate executable validation scenarios

**Files:**
- Modified: `docs/architecture/scenario-validation-plan.md`
- Removed from final branch diff: `docs/architecture/scenario-validation-addendum-2026-09-18.md`

- [x] Merge live-authorization, attempt identity, validation typing, reproducibility, untrusted-content, canonical-race, collection-identity, provider-capability, explicit-resume, and resolved-manifest cases.
- [x] Deduplicate overlapping TF failure/recovery cases.
- [x] Preserve all runtime scenarios as `NOT_RUN`.
- [x] Remove the separate addendum after its scenarios are represented in the primary plan.

### Task 4: Demote review records from authority

**Files:**
- Modified: `docs/architecture/multi-perspective-review-2026-09-18.md`
- Modified: `docs/architecture/workflow-executor-capabilities-and-p0-source-audit.md`

- [x] Change status to non-authoritative review/source-audit rationale.
- [x] State that final semantics are integrated into authoritative documents.
- [x] Remove the review files from the precedence path.
- [x] Preserve findings, inspected sources, and rationale for auditability.

### Task 5: Simplify the documentation map and evidence metadata

**Files:**
- Modified: `docs/README.md`
- Modified: `docs/architecture/evidence-register-2026-09-17.md`

- [x] Make the scientific/run contract, P0, and primary scenario plan authoritative for their scopes.
- [x] Classify review/source-audit files as non-authoritative.
- [x] Remove same-PR correction precedence from the normal reading path.
- [x] Add check-time/inspection-depth/claim-scope metadata to the evidence register.

### Task 6: Fresh verification

- [x] Compare branch to `main`: final changed paths remain under `docs/**`.
- [x] Confirm the separate validation addendum is absent from the final branch diff and its scenarios are represented in the primary plan.
- [x] Fetch the consolidated authoritative contract and confirm accepted corrections are present.
- [x] Fetch P0 and confirm it describes the actual synchronous/local Genome-web provider capability boundary.
- [x] Fetch review/source-audit records and confirm they are explicitly non-authoritative.
- [x] Keep PR Draft; no runtime/scientific completion claim is made.
