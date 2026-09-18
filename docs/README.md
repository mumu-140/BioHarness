# BioHarness Documentation Map

Date: 2026-09-19
Status: Authoritative navigation record

BioHarness now has a provider-agnostic P0 Core runtime kernel with executable Core tests and an implemented/tested Genome-web TF reference adapter. Fresh isolated live acceptance has passed the bounded reference scenarios `TF-01`, `TF-02`, `EXEC-01`, `EXEC-06`, and `DATA-01`; the remaining scenario catalog and advanced memory/pathway, Finding/Decision, canonical-publication, and remote-execution capabilities remain pending unless a narrower document states otherwise.

## 1. Normal Reading Path

Future contributors/agents should normally read:

1. `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`
   - stable product boundary, ownership, provider model, core domain roles, V1 constraints.
2. `docs/architecture/scientific-contracts-and-run-semantics.md`
   - authoritative task/data/feasibility/authorization/configuration/RunSpec/RunAttempt/validation/Finding/reproducibility/canonical contracts.
3. `docs/architecture/p0-genome-web-tf-vertical-slice.md`
   - authoritative first implementation slice, pinned to the audited Genome-web TF provider revision.
4. `docs/architecture/scenario-validation-plan.md`
   - authoritative acceptance-scenario catalog; five Genome-web reference scenarios now have fresh PASS evidence while all unexecuted scenarios remain `NOT_RUN`.
5. Memory records when memory/retrieval/consolidation behavior is relevant:
   - `docs/architecture/provider-composition-and-research-memory.md`
   - `docs/architecture/hierarchical-associative-memory.md`
   - `docs/architecture/memory-pathway-consolidation-and-promotion.md`

This path is intentionally short. Review/audit history is not required to discover final semantics.

## 2. Document Classes

### Authoritative design

- core architecture spec;
- scientific/run contract;
- P0 vertical slice;
- acceptance-scenario catalog;
- three memory architecture records.

Focused contracts control their explicit domain. Cross-cutting scientific/run safety rules constrain memory/provider reuse where the domains intersect.

### Evidence/reference

- `docs/architecture/reference-architectures.md`
- `docs/architecture/evidence-register-2026-09-17.md`
- `docs/validation/records/2026-09-19-genome-web-tf-p0.md`

Evidence informs design but never overrides contracts by itself.

### Review/audit rationale

- `docs/architecture/multi-perspective-review-2026-09-18.md`
- `docs/architecture/workflow-executor-capabilities-and-p0-source-audit.md`

These preserve why decisions changed and what was inspected. They are non-authoritative.

### Plans

- `docs/superpowers/plans/`

Plans describe intended/completed documentation work; they are not runtime evidence.

## 3. Conflict Rule

When records appear to conflict:

1. core architecture controls stable product/system boundaries;
2. authoritative focused contracts control their explicit semantic domain;
3. `scientific-contracts-and-run-semantics.md` controls cross-cutting scientific validity, action-scoped authorization, data/run identity, execution/validation/Finding/reproducibility/canonical rules;
4. memory records control retrieval/pathway/lifecycle semantics subject to those cross-cutting constraints;
5. evidence/review/audit/plan files do not participate in precedence resolution;
6. runtime behavior becomes implementation evidence only when backed by code/tests/fresh execution records.

Git history preserves evolution; normal readers use final authoritative documents.

## 4. Stable Architecture

Active principles:

- headless Research Control Plane; Web is a client/workbench;
- mature algorithms/workflow engines remain external providers;
- Genome-web remains an authoritative biological Data Provider;
- protected access/actions use current action/resource-scoped authorization where applicable;
- historical ContextSnapshot/PolicyDecision explains the past but does not grant present authority;
- ScientificTaskSpec, ScientificAssessment, ResolvedConfiguration, RunSpec, RunAttempt, Artifact, typed validation, Finding, Decision, ResearchMemory, and canonical state remain distinct;
- Artifacts/history are immutable by default; current selection/acceptance lives in separate governed records;
- ResearchMemory is evidence-linked derived knowledge and cannot directly become Policy/Finding/Canonical state;
- memory activation, maturity, and scope are independent;
- dependency-aware impact determines scientific reuse/revalidation, not graph topology or adaptive-slot labels;
- graph/vector infrastructure remains optional until real workload proves value.

## 5. Current P0 Path

```text
requested logical genome resources
    -> current authorization for protected resolution when needed
    -> ResolvedDataRefs + resolved-member provenance
    -> ScientificTaskSpec + candidate method contract
    -> ScientificAssessment
    -> ResolvedConfiguration
    -> reassessment if assumption-relevant config changed
    -> ContextSnapshot + immutable RunSpec
    -> current authorization for launch
    -> revision-scoped WorkflowExecutor capability check
    -> local synchronous Genome-web Nextflow RunAttempt
    -> RunEvents + candidate Artifacts
    -> typed ValidationReports + versioned ValidationProfile evaluation
    -> optional Finding / Decision / scoped MemoryCandidate
```

P0 stops before automatic production publication/canonical mutation.

Audited Genome-web provider revision for this design: `05072cbbcd533ca59afa13996d8d0edd8f939c6e`.

The inspected provider is local/synchronous. Generic Slurm/SSH/Kubernetes, async polling, provider-native exactly-once, durable cancellation, and generic WES/TES behavior are later slices.

## 6. Review/Consolidation Status

Two fresh multi-perspective design passes have been folded directly into the authoritative documents. Review/source-audit records remain rationale only.

The former separate validation addendum was merged into the primary scenario catalog and is not part of the final branch diff.

## 7. Verification Language

Use consistently:

- `DESIGNED`: contract exists in documentation.
- `IMPLEMENTED`: runtime code exists for the stated contract.
- `TESTED`: specified test/scenario executed with fresh evidence.
- `VALIDATED`: stated acceptance criteria executed and passed for the stated scope.
- `NOT_RUN`: scenario exists only as design/acceptance specification.

Current state:

```text
architecture/contracts = DESIGNED
P0 provider-agnostic Core kernel = IMPLEMENTED + TESTED
P0.1H execution/validation hardening = IMPLEMENTED + TESTED
Genome-web TF reference adapter = IMPLEMENTED + TESTED
Genome-web TF targeted live acceptance = VALIDATED (TF-01, TF-02, EXEC-01, EXEC-06, DATA-01)
remaining acceptance scenarios = NOT_RUN
advanced memory/pathway + Finding/Decision/Canonical runtime = NOT_IMPLEMENTED
production publication = OUT_OF_SCOPE_P0
```

Core CI is evidence only for the provider-agnostic kernel and its tested invariants. Genome-web reference claims require the separate pinned live evidence record above; that record validates only its five named scenarios and does not validate the remaining catalog, advanced memory architecture, or production publication.