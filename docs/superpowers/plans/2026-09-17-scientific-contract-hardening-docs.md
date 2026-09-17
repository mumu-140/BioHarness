# BioHarness Scientific Contract Hardening Documentation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the current BioHarness architecture records so scientific validity, authority, data identity, invalidation, execution recovery, and memory promotion have explicit non-conflicting semantics before implementation starts.

**Architecture:** Keep the existing headless Research Control Plane, provider/adapter boundaries, evidence-backed memory, and external workflow engines. Add one authoritative scientific-contract decision record that overrides a small set of older conflicting clauses, then validate it against the existing Genome-web TF Nextflow pilot as the first real-world vertical slice. Do not add runtime services, databases, workflow engines, or production integrations in this documentation phase.

**Tech Stack:** Markdown architecture records, Git/GitHub review, existing Genome-web Nextflow pilot as an external reference implementation.

**Spec:** `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`

## Global Constraints

- Documentation-only change: no application code, database migration, deployment, or production data mutation.
- Existing mature scientific algorithms and workflow engines remain external providers.
- Existing historical design records remain readable; later decision records explicitly override only conflicting semantics.
- Scientific validity and execution success remain independent.
- Memory cannot directly become Policy or Canonical state.
- Every proposed P0 runtime behavior must be testable against a concrete failure or recovery scenario.
- Validation scenarios created in this documentation phase are `NOT_RUN` until a future implementation executes them.

---

### Task 1: Establish an authoritative documentation map

**Files:**
- Create: `docs/README.md`

**Interfaces:**
- Consumes: all current architecture records under `docs/architecture/` and the core architecture spec.
- Produces: one explicit precedence and navigation map used by future contributors and agents.

- [ ] **Step 1: Define document classes**

Record the difference between core spec, later decision records, reference/evidence records, validation records, and implementation plans.

- [ ] **Step 2: Define conflict precedence**

Specify that later focused decision records override older clauses only where they explicitly name a superseded rule; absence of a conflict leaves the older rule active.

- [ ] **Step 3: Record current implementation state**

State that BioHarness currently contains architecture documentation only and that the P0 validation suite is not yet executed.

- [ ] **Step 4: Review links**

Verify every linked repository path exists on the branch.

- [ ] **Step 5: Commit**

Commit message: `docs: add architecture authority map`

### Task 2: Define scientific and execution contracts

**Files:**
- Create: `docs/architecture/scientific-contracts-and-run-semantics.md`

**Interfaces:**
- Consumes: `ResearchContext`, `Policy`, `Recipe`, `Module`, `Workflow`, `Run`, `Artifact`, `Decision`, `ResearchMemory`, and `MemoryPathway` concepts from existing records.
- Produces: `ScientificTaskSpec`, `ResolvedDataRef`, `PolicyDecision`, `ScientificAssessment`, `ResolvedConfiguration`, `ChangeImpactContract`, `RunSpec`, `RunAttempt`, `RunEvent`, `ValidationReport`, and `CanonicalPointer` semantics.

- [ ] **Step 1: Separate authority from scientific truth**

Define policy authorization, scientific assessment, and resolved configuration as independent outputs. Explicitly prohibit policy or project decisions from converting an unidentifiable scientific design into a valid inference.

- [ ] **Step 2: Freeze scientific intent before planning**

Define the minimal `ScientificTaskSpec` fields needed to tell whether a task is answerable with the available data.

- [ ] **Step 3: Make data identity reproducible**

Define `ResolvedDataRef` so logical provider identity is accompanied by revision/version, content identity when available, schema/namespace, biological reference version, and resolution time.

- [ ] **Step 4: Replace topology-only thawing with impact propagation**

Define an explicit change-impact contract with compatibility predicates and required downstream revalidation.

- [ ] **Step 5: Separate analysis identity from execution retries**

Define immutable `RunSpec`, one-or-more `RunAttempt` records, append-only `RunEvent`s, immutable `Artifact`s, appendable `ValidationReport`s, and governed `CanonicalPointer` updates.

- [ ] **Step 6: Define idempotency and reconciliation**

Require external submission identity, idempotency keys where supported, an `UNKNOWN`/reconciling state for lost acknowledgements, and query-before-resubmit behavior.

- [ ] **Step 7: Define retrieval channels**

Separate mandatory deterministic context from exact reference lookup, hybrid memory recall, and optional graph expansion. Required policy/critical contradiction information must not compete in semantic top-k retrieval.

- [ ] **Step 8: Define evidence independence**

Distinguish repeated runs from independent datasets/studies and state that null/negative scientific results can be valid successful analyses.

- [ ] **Step 9: Name superseded clauses**

Explicitly override the old single authority/similarity precedence for scientific truth, the assumption that declared slot mutations are inherently lower impact, and topology-only partial thawing.

- [ ] **Step 10: Commit**

Commit message: `docs: define scientific and run contracts`

### Task 3: Add evidence and reusable-project register

**Files:**
- Create: `docs/architecture/evidence-register-2026-09-17.md`

**Interfaces:**
- Consumes: primary papers, specifications, and mature project documentation.
- Produces: an auditable record of what BioHarness borrows, what it does not infer, and which architecture clause each source informs.

- [ ] **Step 1: Record scientific workflow/provenance references**

Include AiiDA, Nextflow/nf-core, Snakemake, OpenLineage, RO-Crate, and GA4GH DRS/WES patterns.

- [ ] **Step 2: Record scientific-analysis validity references**

Include DESeq2 design/count semantics, GO enrichment background semantics, RNA-seq selection-bias guidance, and replicate-aware single-cell differential-expression evidence.

- [ ] **Step 3: Record memory/retrieval references**

Include RAPTOR, HippoRAG, Agent Workflow Memory, TiMEM, and Graphiti as bounded inspirations rather than delegated scientific authority.

- [ ] **Step 4: Record agent/research-system references**

Include BioMedAgent and PaperQA-style evidence retrieval as comparison points, and the Schultz et al. 2026 EGT work as a concrete example of modular scientific software plus Snakemake and graph representation.

- [ ] **Step 5: Record evaluation references**

Include scientific-agent, long-memory, and adversarial-tool-use benchmark directions; record that benchmark transfer to BioHarness is a hypothesis until tested.

- [ ] **Step 6: Commit**

Commit message: `docs: record scientific architecture evidence`

### Task 4: Define the first real-world P0 vertical slice

**Files:**
- Create: `docs/architecture/p0-genome-web-tf-vertical-slice.md`

**Interfaces:**
- Consumes: existing Genome-web TF Nextflow pilot and the contracts from Task 2.
- Produces: one bounded P0 scenario that exercises provider resolution, context freezing, governed execution, recovery, artifact validation, decision, and memory-candidate capture without publication.

- [ ] **Step 1: Map existing TF pilot stages**

Map registry preflight, `PREPARE`, `MAFFT`, `IQTREE`, and `BUNDLE` into BioHarness provider and lifecycle objects without rewriting biological logic.

- [ ] **Step 2: Freeze the P0 task semantics**

Use an explicit task such as: build TF-family phylogenies for registered genomes, preserve assembly/annotation identity, produce validated candidate artifacts, and do not publish to the production database.

- [ ] **Step 3: Define success and non-success states**

Separate executor completion, candidate-package validation, scientific acceptance, and canonical publication authorization.

- [ ] **Step 4: Define recovery cases**

Cover leading-zero UID preservation, cross-UID identity conflict, all-skipped datasets, corrupted candidate packages, resume after failure, unknown external submission acknowledgement, and parameter-local invalidation.

- [ ] **Step 5: Define memory feedback**

Only validated failure lessons or compatibility findings become memory candidates; raw execution frequency does not promote method or lab scope.

- [ ] **Step 6: Commit**

Commit message: `docs: define TF vertical slice`

### Task 5: Define executable validation scenarios

**Files:**
- Create: `docs/architecture/scenario-validation-plan.md`

**Interfaces:**
- Consumes: Tasks 2 and 4.
- Produces: a future test matrix with preconditions, action, expected state transition, forbidden behavior, and current execution status.

- [ ] **Step 1: Add TF-tree lifecycle tests**

Include identity, cache invalidation, failure recovery, candidate validation, and no-implicit-publish assertions.

- [ ] **Step 2: Add RNA-seq to GO scientific-contract tests**

Include ambiguous scientific intent, incompatible count semantics, confounded designs, ID namespace mismatch, GO background provenance, and valid null-result handling.

- [ ] **Step 3: Add pathway reactivation tests**

Test bulk-to-single-cell changes and annotation/reference-version changes using dependency-aware revalidation.

- [ ] **Step 4: Add memory-promotion tests**

Test correlated duplicate evidence, fatal contradictions, project-to-method scope proposals, and dormant-but-valid pathways.

- [ ] **Step 5: Mark execution status**

Mark every scenario `NOT_RUN`; do not claim implementation correctness from documentation review.

- [ ] **Step 6: Commit**

Commit message: `docs: add architecture validation scenarios`

### Task 6: Cross-document review and Draft PR

**Files:**
- Review: all files created in Tasks 1-5 and existing architecture records named by the supersession table.

**Interfaces:**
- Consumes: completed documentation set.
- Produces: a Draft PR with bounded scope and explicit unverified runtime status.

- [ ] **Step 1: Check repository diff**

Confirm changes are limited to `docs/**`.

- [ ] **Step 2: Check semantic consistency**

Confirm `ScientificTaskSpec`, `ResolvedDataRef`, `RunSpec`, `RunAttempt`, `ValidationReport`, and `CanonicalPointer` retain identical meanings across all new records.

- [ ] **Step 3: Check supersession clarity**

Confirm every overridden old clause is explicitly named and that non-conflicting older architecture remains active.

- [ ] **Step 4: Check verification language**

Search for unsupported statements such as `validated`, `passes`, `works`, or `verified` when referring to BioHarness runtime behavior. Runtime scenarios must remain `NOT_RUN`.

- [ ] **Step 5: Open Draft PR**

PR title: `docs: harden scientific contracts and define P0 validation slice`

PR body must state: documentation only; no runtime implementation; no production changes; validation scenarios not executed.
