# BioHarness Documentation Map

Date: 2026-09-18
Status: Authoritative navigation record

BioHarness is currently in the architecture and validation-design phase. Runtime implementation does not yet exist in this repository.

## 1. Read These First

Future contributors and agents should normally read BioHarness in this order:

1. `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`
   - stable product boundary and core Research Control Plane model.
2. `docs/architecture/scientific-contracts-and-run-semantics.md`
   - authoritative scientific intent, feasibility, authorization, data identity, RunSpec/RunAttempt, provider capability, validation, reproducibility, canonical-state, and context contracts.
3. `docs/architecture/p0-genome-web-tf-vertical-slice.md`
   - authoritative first implementation slice using the actual current Genome-web TF Nextflow provider.
4. `docs/architecture/scenario-validation-plan.md`
   - authoritative executable-spec catalog; all scenarios remain `NOT_RUN` until implementation executes them.
5. Memory-specific architecture records when needed:
   - `docs/architecture/provider-composition-and-research-memory.md`
   - `docs/architecture/hierarchical-associative-memory.md`
   - `docs/architecture/memory-pathway-consolidation-and-promotion.md`

This path is intentionally short. A future implementation should not need to traverse multiple same-PR correction records to discover the final meaning of a contract.

## 2. Document Classes

### Core architecture

- `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`

Defines the stable product boundary: headless Research Control Plane, provider/adapter architecture, governed computation, evidence/provenance, and research-memory feedback.

### Authoritative focused contracts

- `docs/architecture/scientific-contracts-and-run-semantics.md`
- `docs/architecture/p0-genome-web-tf-vertical-slice.md`
- `docs/architecture/scenario-validation-plan.md`
- memory architecture records listed above.

These files contain current normative design semantics for their scope.

### Evidence/reference records

- `docs/architecture/reference-architectures.md`
- `docs/architecture/evidence-register-2026-09-17.md`

These document external systems, papers, standards, and internal projects used to inform design. Evidence records do not override BioHarness contracts by themselves.

### Review/audit records

- `docs/architecture/multi-perspective-review-2026-09-18.md`
- `docs/architecture/workflow-executor-capabilities-and-p0-source-audit.md`

These preserve why the contracts were changed and what sources were inspected. They are non-authoritative rationale records. Final rules have been integrated into the authoritative contract/P0/validation documents.

### Plans

- `docs/superpowers/plans/`

Plans describe intended work. A plan is never proof that the described capability exists.

## 3. Conflict Rule

When records appear to conflict:

1. the core architecture defines stable system boundaries;
2. an authoritative focused contract controls its explicit domain;
3. memory-specific records control memory semantics unless the scientific/run contract explicitly constrains a cross-cutting safety/scientific rule;
4. review/audit/evidence/plan files do not override authoritative contracts;
5. implementation behavior becomes authoritative only when backed by implemented contracts, tests, and fresh execution evidence.

Git history preserves how decisions evolved; normal readers should use the final authoritative documents rather than reconstructing that history from old review wording.

## 4. Stable Architecture

The following remain active:

- BioHarness is headless; Web is a client/workbench, not a scientific source of truth.
- Mature scientific algorithms and workflow engines remain external providers whenever practical.
- Genome-web remains an authoritative biological Data Provider rather than being copied into BioHarness.
- Official computation is governed and historical Run/Artifact evidence is immutable by default.
- Scientific intent, analysis feasibility, authorization, execution completion, validation, Finding/interpretation, and canonical publication are distinct.
- Authoritative state, derived Research Memory, and ephemeral model context are distinct.
- Memory cannot directly become Policy or Canonical state.
- Memory activation, maturity, and scope are separate dimensions.
- Project closeout consolidates/cools memory rather than deleting scientific history.
- Graph/vector infrastructure remains optional until real workload proves value.

## 5. Current P0 Path

```text
registered genome inputs
    -> ResolvedDataRefs + resolved-member provenance
    -> ScientificTaskSpec
    -> ScientificAssessment
    -> ResolvedConfiguration
    -> ContextSnapshot + immutable RunSpec
    -> current PolicyDecision for launch
    -> revision-scoped WorkflowExecutor capability check
    -> local synchronous Genome-web Nextflow RunAttempt
    -> RunEvents + candidate Artifacts
    -> typed ValidationReports evaluated by ValidationProfile
    -> Decision / MemoryCandidate
```

P0 stops before automatic production publication or canonical update.

The current Genome-web pilot is explicitly treated as a synchronous local Nextflow integration. Slurm/SSH/Kubernetes and generic async exactly-once submission are later slices.

## 6. Verification Language

Use these terms consistently:

- `DESIGNED`: contract exists in documentation.
- `IMPLEMENTED`: runtime code exists for the contract.
- `TESTED`: a specified test/scenario has been executed with fresh evidence.
- `VALIDATED`: the stated acceptance criteria were executed and passed for the stated scope.
- `NOT_RUN`: scenario exists only as a specification.

Current state:

```text
architecture/contracts = DESIGNED
BioHarness runtime = NOT_IMPLEMENTED
P0/scenario validation = NOT_RUN
```

No review document, plan, or prose statement should be used as evidence that runtime behavior already works.
