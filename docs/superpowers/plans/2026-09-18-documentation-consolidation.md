# BioHarness Architecture Documentation Consolidation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

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
- Modify: `docs/architecture/scientific-contracts-and-run-semantics.md`

**Interfaces:**
- Consumes: findings R1-R11 from `multi-perspective-review-2026-09-18.md` and the provider capability decisions in `workflow-executor-capabilities-and-p0-source-audit.md`.
- Produces: one authoritative contract for task intent, analysis feasibility, policy authorization, configuration, data identity, RunSpec/RunAttempt identity, provider capability negotiation, validation profiles, reproducibility, content trust, and canonical updates.

- [ ] Replace pre-execution `SUPPORTED` terminology with `ANALYSIS_SUPPORTED` vocabulary.
- [ ] Move provider submission identity from RunSpec to RunAttempt (`submission_key`).
- [ ] Add current-side-effect authorization separate from historical ContextSnapshot/PolicyDecision.
- [ ] Add typed `ValidationReport` and `ValidationProfile` semantics.
- [ ] Add `ReproducibilityContract`.
- [ ] Add explicit untrusted-content rule.
- [ ] Add revision-checked CanonicalPointer mutation.
- [ ] Extend `ResolvedDataRef` for composite collection/manifest identity.
- [ ] Add revision-scoped `WorkflowExecutorCapabilitySnapshot` and limited-reconciliation semantics.
- [ ] Clarify engine-internal retry versus BioHarness RunAttempt.
- [ ] Update architecture invariants and P0 boundary.

### Task 2: Consolidate the P0 vertical slice

**Files:**
- Modify: `docs/architecture/p0-genome-web-tf-vertical-slice.md`

**Interfaces:**
- Consumes: final Task 1 contracts and the source-observed Genome-web launcher/Nextflow behavior.
- Produces: a P0 design that matches the actual synchronous local Nextflow provider rather than a hypothetical remote submit/poll service.

- [ ] Remove `min_family_sequences` from ScientificTaskSpec and place method parameters in ResolvedConfiguration.
- [ ] Record the actual local/synchronous executor capability boundary.
- [ ] Require resolved-manifest/member provenance.
- [ ] Require typed provider/candidate validation rather than a generic PASS.
- [ ] Narrow lost-acknowledgement recovery to capability-driven reconciliation and `NEEDS_OPERATOR_RECONCILIATION` where necessary.
- [ ] Keep production publication out of P0.

### Task 3: Consolidate executable validation scenarios

**Files:**
- Modify: `docs/architecture/scenario-validation-plan.md`
- Delete after merge: `docs/architecture/scenario-validation-addendum-2026-09-18.md`

**Interfaces:**
- Consumes: the existing validation plan plus all addendum/source-audit scenarios.
- Produces: one primary `NOT_RUN` scenario catalog.

- [ ] Merge live-authorization, attempt idempotency, validation typing, reproducibility, untrusted-content, canonical-race, collection-identity, provider-capability, explicit-resume, and resolved-manifest cases.
- [ ] Deduplicate overlapping TF failure/recovery cases.
- [ ] Preserve all scenarios as `NOT_RUN`.
- [ ] Delete the separate addendum after its scenarios are represented in the primary plan.

### Task 4: Demote review records from authority

**Files:**
- Modify: `docs/architecture/multi-perspective-review-2026-09-18.md`
- Modify: `docs/architecture/workflow-executor-capabilities-and-p0-source-audit.md`

**Interfaces:**
- Consumes: final authoritative contracts from Tasks 1-3.
- Produces: concise audit/rationale records that point to authoritative docs and no longer override them.

- [ ] Change status to `Review record / non-authoritative rationale`.
- [ ] Add a prominent statement that final semantics have been integrated into authoritative documents.
- [ ] Remove language that future readers could interpret as an additional precedence layer.
- [ ] Preserve findings, inspected sources, and rationale for auditability.

### Task 5: Simplify the documentation map and evidence metadata

**Files:**
- Modify: `docs/README.md`
- Modify: `docs/architecture/evidence-register-2026-09-17.md`

**Interfaces:**
- Consumes: consolidated final structure.
- Produces: a short authority path for future humans/agents and an evidence record with explicit inspection provenance.

- [ ] Make `scientific-contracts-and-run-semantics.md`, P0, and the primary scenario plan authoritative for their respective scopes.
- [ ] Classify the two 2026-09-18 review files as non-authoritative audit records.
- [ ] Remove same-PR correction precedence from normal reading flow.
- [ ] Add checked-at/inspection-depth metadata to the evidence register at least for sources directly inspected during this audit.

### Task 6: Fresh verification

**Files:**
- Review all changed docs.

**Interfaces:**
- Produces: evidence-backed PR status only; no runtime-completion claim.

- [ ] Compare branch to `main` and confirm changed paths remain documentation-only.
- [ ] Verify the deleted validation addendum is represented in the consolidated validation plan.
- [ ] Verify the authoritative contract contains all accepted R1-R11 corrections.
- [ ] Verify P0 reflects the actual synchronous/local Genome-web provider capability boundary.
- [ ] Verify review records are explicitly non-authoritative.
- [ ] Keep PR Draft until final consolidation review is complete.
