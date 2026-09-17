# BioHarness Documentation Map

Date: 2026-09-17
Status: Authoritative navigation and precedence record

BioHarness is currently in the **architecture and validation-design phase**. The repository does not yet contain a BioHarness runtime implementation. Any scenario marked as an acceptance test or validation case is therefore a future executable specification unless an explicit Run record says otherwise.

## 1. Document Classes

BioHarness documentation is divided into five classes.

### Core architecture spec

- `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`

Defines the stable product boundary: a headless research control plane, provider/adapter architecture, governed Runs and Artifacts, evidence-backed Research Memory, and explicit Decision/Policy promotion.

### Architecture decision records

Focused records refine or override narrow semantics without replacing the entire core architecture.

Current records:

- `docs/architecture/provider-composition-and-research-memory.md`
- `docs/architecture/hierarchical-associative-memory.md`
- `docs/architecture/memory-pathway-consolidation-and-promotion.md`
- `docs/architecture/scientific-contracts-and-run-semantics.md`

### Evidence and reference records

- `docs/architecture/reference-architectures.md`
- `docs/architecture/evidence-register-2026-09-17.md`

These files document external systems, papers, standards, and internal projects that inform the design. They are evidence catalogs, not implementation dependencies by default.

### Validation records

- `docs/architecture/p0-genome-web-tf-vertical-slice.md`
- `docs/architecture/scenario-validation-plan.md`

These define concrete scenarios and expected behavior. Unless explicitly updated with fresh execution evidence, their status is `NOT_RUN`.

### Implementation/documentation plans

- `docs/superpowers/plans/`

Plans describe intended work. A plan is not proof that the described capability exists.

## 2. Precedence Rule

When two architecture records appear to conflict, apply the following rule:

1. explicit hard constraints in the core architecture remain active unless a later decision record explicitly names and supersedes that clause;
2. a later focused decision record overrides an older record only for the semantic issue it explicitly changes;
3. all non-conflicting older design decisions remain active;
4. evidence/reference records never override BioHarness policy or contracts by themselves;
5. implementation behavior is authoritative only when backed by the implemented contract, tests, and recorded execution evidence.

This avoids silently rewriting history while allowing the architecture to become more precise.

## 3. 2026-09-17 Scientific-Contract Hardening

`docs/architecture/scientific-contracts-and-run-semantics.md` is the current authoritative decision record for the following issues:

- distinguishing authorization from scientific validity;
- freezing scientific intent before workflow planning;
- reproducible logical-to-physical data identity;
- dependency-aware invalidation and revalidation;
- separating analysis identity from execution attempts;
- idempotent external submission and unknown-state reconciliation;
- separating deterministic required context from semantic memory retrieval;
- distinguishing repeated executions from independent scientific evidence;
- treating valid null/negative results as successful scientific outcomes.

Where the older records conflict with these points, the scientific-contract record wins.

In particular, the following older interpretations are superseded:

- a single precedence ladder must not be used to decide scientific truth merely because it is useful for configuration/authority resolution;
- a declared adaptive-slot mutation is not automatically low-impact; revalidation is determined by scientific dependency impact;
- partial thawing is not determined only by graph topology; affected downstream assumptions and artifacts must be revalidated according to explicit impact contracts.

## 4. Stable Architecture That Remains Active

The following existing principles remain unchanged:

- BioHarness is headless and the Web is a client/workbench, not the scientific source of truth;
- mature scientific algorithms and workflow engines remain external whenever practical;
- Genome-web remains an authoritative biological Data Provider rather than being copied into BioHarness;
- official computation is governed and historical Run/Artifact evidence is immutable by default;
- execution success and scientific validity are independent;
- authoritative state, derived Research Memory, and ephemeral model context are distinct;
- Memory cannot directly promote itself into Policy or Canonical state;
- Memory Pathway activation, maturity, and scope are independent dimensions;
- project completion cools or consolidates memory rather than deleting scientific history;
- dedicated graph/vector infrastructure remains optional until demonstrated workload justifies it.

## 5. Current P0 Direction

The first implementation should prove a real vertical slice rather than build every subsystem horizontally.

The selected P0 reference scenario is the existing Genome-web TF Nextflow pilot:

```text
registered genome inputs
    -> provider resolution
    -> ScientificTaskSpec + ContextSnapshot
    -> immutable RunSpec
    -> external Nextflow execution
    -> RunAttempt / RunEvent collection
    -> candidate Artifact registration
    -> independent ValidationReport
    -> Decision
    -> evidence-backed MemoryCandidate
```

P0 explicitly stops before automatic publication to the production biological database.

See `docs/architecture/p0-genome-web-tf-vertical-slice.md`.

## 6. Verification Language

Architecture documents may state requirements such as `must`, `shall`, or `expected`.

They must not imply runtime completion unless fresh execution evidence exists. Use these status terms consistently:

- `DESIGNED`: contract exists in documentation;
- `IMPLEMENTED`: runtime code exists for the contract;
- `TESTED`: a specified test has been executed with fresh results;
- `VALIDATED`: scientific/operational acceptance criteria have been executed and passed;
- `NOT_RUN`: scenario exists only as a specification.

As of this record, the new scientific-contract scenarios are `DESIGNED / NOT_RUN`.
