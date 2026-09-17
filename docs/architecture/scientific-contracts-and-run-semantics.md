# BioHarness Scientific Contracts and Run Semantics

Date: 2026-09-17
Status: Design record v1 for review
Scope: Scientific task validity, reproducible data identity, change-impact propagation, execution identity/recovery, and context/retrieval boundaries.

Related documents:

- `docs/README.md`
- `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`
- `docs/architecture/provider-composition-and-research-memory.md`
- `docs/architecture/hierarchical-associative-memory.md`
- `docs/architecture/memory-pathway-consolidation-and-promotion.md`

## 1. Decision Summary

BioHarness must distinguish four questions that are easy to conflate:

1. **What scientific question is being asked?**
2. **Can the available data and design support the requested inference?**
3. **Is the requested action authorized?**
4. **How should an authorized, scientifically supportable task be configured and executed?**

No single similarity score, memory rank, project Decision, or policy rule can answer all four.

The governing sequence is:

```text
User / Agent Request
      |
      v
ScientificTaskSpec
      |
      +-------> ResolvedDataRefs
      |
      v
ScientificAssessment
      |
      +-------> PolicyDecision
      |
      v
ResolvedConfiguration
      |
      v
ContextSnapshot + RunSpec
      |
      v
RunAttempt(s) -> Artifact(s) -> ValidationReport(s)
      |
      v
Decision / CanonicalPointer / ResearchMemory
```

This record keeps the existing BioHarness headless/provider architecture but tightens the scientific and execution contracts that precede memory reuse and workflow submission.

## 2. Three Independent Resolution Outputs

BioHarness must not use one global precedence ladder to collapse authority, evidence, and configuration into one answer.

### 2.1 PolicyDecision

Question:

> Is this actor allowed to perform this action under the current policies?

Recommended outcomes:

```text
ALLOW
ALLOW_WITH_WARNING
REQUIRE_APPROVAL
DENY
```

Examples:

- reading a gene record: `ALLOW`;
- launching a resource-expensive workflow: `REQUIRE_APPROVAL` under a lab policy;
- overwriting a canonical result directly: `DENY`;
- promoting a validated candidate: `REQUIRE_APPROVAL` when policy requires human review.

Policy can permit or forbid actions. It cannot make an unidentifiable scientific design identifiable.

### 2.2 ScientificAssessment

Question:

> Do the available data, experimental design, method assumptions, and evidence support the requested scientific inference?

Recommended state vocabulary:

```text
SUPPORTED
SUPPORTED_WITH_LIMITATIONS
UNRESOLVED
NOT_IDENTIFIABLE
INCOMPATIBLE
```

A `ScientificAssessment` should record:

- requested claim/inference;
- required design assumptions;
- observed data characteristics;
- applicable method constraints;
- unresolved scientific blockers;
- evidence/reference links;
- limitations that must survive into interpretation.

Examples:

- a treatment effect where treatment is perfectly confounded with batch can be `NOT_IDENTIFIABLE` even if execution is authorized;
- a count matrix whose semantics do not satisfy a module contract can be `INCOMPATIBLE` even if it is numerically integer-like;
- a result with no statistically significant signal may still be `SUPPORTED` as a valid null outcome if the design and method are appropriate.

### 2.3 ResolvedConfiguration

Question:

> Among scientifically supportable and authorized choices, which exact data, method, parameters, environment, and provider are selected for this Run?

A `ResolvedConfiguration` may be influenced by:

- explicit project Decisions;
- validated method defaults;
- current software/environment compatibility;
- resource constraints;
- user preferences that do not alter scientific truth;
- approved adaptive pathway slots.

It must not silently weaken a failed ScientificAssessment.

## 3. ScientificTaskSpec: Freeze Intent Before Workflow Selection

BioHarness must create a structured `ScientificTaskSpec` before selecting a workflow for governed analysis.

The purpose is not to force every user to fill in a long form. Fields can be inferred from authoritative project/data metadata when available. The contract exists so missing scientific information is visible rather than hallucinated.

Minimal conceptual fields:

```yaml
scientific_task_spec:
  id: task-spec-001
  question: ...
  requested_inference: ...
  analysis_class: ...
  biological_scope:
    species: ...
    assembly: ...
    annotation_release: ...
  experimental_unit: ...
  design_or_comparison: ...
  input_semantics: ...
  output_intent: exploratory | candidate | official
  required_identifiers:
    namespace: ...
  unresolved_fields: []
```

Not every analysis uses every field. Each Recipe/Module declares which fields are required.

### Example: differential expression to GO enrichment

The phrase:

> "For this gene, inspect differential expression and perform GO enrichment."

is scientifically ambiguous. It could mean:

- DEGs from a perturbation of the gene;
- DEGs from a treatment condition associated with the gene;
- a coexpression neighborhood around the gene;
- an already defined DEG set whose membership should be interpreted.

BioHarness must resolve this ambiguity before constructing an official DEG -> GO chain.

The task contract should identify at least:

```text
comparison or selection rule
experimental unit
sample grouping/design
source data semantics
reference/annotation identity
gene-ID namespace
gene-set generation rule
background-universe rule
intended status of result
```

If required information is absent and cannot be obtained from an authoritative provider, the governed task remains unresolved rather than being completed with model-invented assumptions.

## 4. ResolvedDataRef: Logical Identity Is Not Enough

Provider URIs are useful stable handles, but a logical URI alone does not prove that the same bytes or biological release will be resolved later.

BioHarness therefore distinguishes a logical resource reference from a resolved versioned data identity.

Conceptual contract:

```yaml
resolved_data_ref:
  provider: genome-web
  resource_type: proteome
  resource_id: Paxg_84K_T2T
  logical_uri: genome-web://proteome/Paxg_84K_T2T

  provider_revision: ...
  content_sha256: ...
  schema_version: ...

  biological_identity:
    species_id: ...
    assembly: ...
    annotation_release: ...
    identifier_namespace: ...

  resolved_at: ...
  retrieval_state: available | external | unavailable
```

Fields may be unavailable for some external providers. Missing identity information must be explicit.

### Required rule

For an official `RunSpec`, BioHarness must store enough identity information to answer:

> Which exact scientific input did this Run consume, and can that identity be checked again?

BioHarness does not need to copy every large input into its own store. It does need to preserve stable identity/provenance and, where applicable, a content digest or immutable provider revision.

## 5. Scientific Contract of a Module

The existing Module contract remains active and should be extended with scientific preconditions.

A Module should be able to declare:

```yaml
scientific_contract:
  required_task_fields: [...]
  input_semantics: ...
  assumptions: [...]
  compatibility_checks: [...]
  invalidating_changes: [...]
  required_validation: [...]
  interpretation_limits: [...]
```

Examples:

- a differential-expression module specifies what its input count semantics must represent;
- an enrichment module specifies identifier namespace, tested gene universe/background semantics, annotation source, and multiple-testing behavior;
- a phylogenetic module specifies whether representative-transcript selection is part of the method or must already be resolved upstream.

A file type alone is insufficient scientific validation.

## 6. ChangeImpactContract: Replace Mutation-Class Heuristics

BioHarness previously distinguished structural pathway mutations from adaptive-slot mutations. That distinction remains useful for describing how a pathway changed, but it must not determine scientific impact by itself.

A small textual or parameter edit can invalidate many downstream results; a graph-topology change can sometimes be presentation-only.

Each adaptive slot or version-sensitive dependency should therefore expose an impact contract.

Conceptual shape:

```yaml
change_impact:
  subject: annotation_release
  compatibility_predicate: ...
  affects:
    - id_mapping
    - enrichment_background
    - annotation_interpretation
  required_revalidation:
    - mapping_validation
    - enrichment_recompute
```

Or:

```yaml
change_impact:
  subject: tree_render_style
  compatibility_predicate: scientific_data_unchanged
  affects:
    - presentation
  required_revalidation:
    - render_check
```

### Core rule

> Revalidation scope is determined by scientific/data dependency impact, not by whether the changed object was labeled a structural node or adaptive slot.

The old structural-vs-slot mutation statistics may still be recorded for pathway maturity, but they cannot bypass explicit impact analysis.

## 7. Dependency-Aware Invalidation and Partial Thawing

Partial thawing remains an important optimization, but the system must identify scientifically affected downstream assumptions.

Recommended sequence:

```text
Changed input / version / slot / policy
      |
      v
ChangeImpactContract
      |
      v
Compatibility check
      |
      +-- compatible --> retain eligible evidence/artifacts
      |
      +-- incompatible --> invalidate affected assumptions
                            |
                            v
                    downstream dependency propagation
                            |
                            v
                    recompute / revalidate affected region
```

### Example: bulk RNA-seq -> single-cell RNA-seq

It may be possible to reuse generic ID-mapping or GO-enrichment software components.

It is not valid to assume that the old differential gene set, independence assumptions, gene-selection process, or enrichment background remain valid merely because the downstream pathway topology is unchanged.

The stable **component** can remain available while the old **evidence and configuration** are invalidated or revalidated.

### Example: annotation release v3 -> v4

Even if the same enrichment executable is used, changes in gene models or identifiers can require revalidation of:

- identifier mapping;
- selected gene membership;
- background universe;
- annotation coverage;
- final enrichment results.

## 8. RunSpec: Identity of an Analysis

A governed analysis requires an immutable `RunSpec` that identifies the intended scientific computation before execution.

Conceptual fields:

```yaml
run_spec:
  id: rs-001
  scientific_task_spec: task-spec-001
  context_snapshot: ctx-001
  resolved_configuration: cfg-001
  workflow_revision: ...
  input_refs: [...]
  normalized_parameters: {...}
  environment_identity: ...
  expected_outputs: [...]
  validation_profile: ...
  idempotency_key: ...
  created_at: ...
```

### New RunSpec versus new RunAttempt

Create a **new RunSpec** when the scientific/computational identity changes, for example:

- input content/revision changes;
- scientific design changes;
- analysis parameters that affect results change;
- workflow/module revision changes in a result-affecting way;
- resolved policy/context changes in a way that affects computation.

Create another **RunAttempt** for the same RunSpec when retrying or recovering execution without changing the intended computation.

## 9. RunAttempt: One External Execution Binding

`RunAttempt` records one attempt to realize a RunSpec on a concrete execution backend.

Conceptual fields:

```yaml
run_attempt:
  id: ra-001
  run_spec: rs-001
  attempt_number: 1
  executor: nextflow
  compute_provider: ...
  external_execution_id: ...
  submitted_at: ...
  state: ...
  last_reconciled_at: ...
```

Recommended lifecycle:

```text
DRAFT
  -> SUBMITTING
  -> QUEUED
  -> RUNNING
  -> COLLECTING
  -> FINISHED

SUBMITTING -> UNKNOWN
QUEUED/RUNNING -> CANCELLING -> CANCELLED | UNKNOWN
any active state -> FAILED
UNKNOWN -> reconciled active/final state
```

`FINISHED` means the external computation ended and outputs can be collected. It does not mean scientific validation passed.

## 10. RunEvent: Append-Only Execution History

Execution-state observations should be append-only events where practical.

Examples:

```text
AttemptCreated
SubmissionRequested
ExternalExecutionBound
ExecutionStarted
ExecutionHeartbeat
ExecutionFailed
ExecutionFinished
ArtifactDiscovered
ArtifactRegistered
ValidationStarted
ValidationReported
```

Events preserve what the system observed and when. A current-state read model may be derived from them.

The first implementation may use a relational transaction/outbox approach; Kafka or another distributed event bus is not required.

## 11. Idempotency and Unknown Submission State

A critical failure mode occurs when the external workflow engine accepts a submission but the client loses the acknowledgement.

BioHarness must not treat this as an ordinary failure and blindly submit again.

### Required behavior

Before external submission, record:

- `RunSpec` identity;
- one `RunAttempt` identity;
- idempotency key / request identity where supported;
- expected executor/provider;
- submission intent event.

If acknowledgement is lost:

```text
SUBMITTING -> UNKNOWN
```

Recovery must attempt to reconcile by querying provider state using the recorded attempt/request identity or provider-supported metadata.

Only when BioHarness can establish that no equivalent external execution exists may it create or submit another attempt according to policy.

### Rule

> Retry is not equivalent to idempotency.

This is especially important for expensive HPC jobs, workflows with side effects, and providers whose submission API is not transactionally coupled to BioHarness state.

## 12. Artifact and ValidationReport Are Separate

An `Artifact` records an immutable produced object or registered scientific result.

Examples:

- alignment;
- tree;
- BAM/VCF;
- DEG table;
- enrichment table;
- motif set;
- report;
- candidate release bundle.

A `ValidationReport` is a later assessment of one or more Artifacts, a RunSpec, or an analysis package.

This allows:

- independent validation after execution;
- multiple validators;
- future revalidation under newer rules;
- preservation of the original Artifact while scientific interpretation changes.

Conceptual states for validation outcomes may include:

```text
PASS
PASS_WITH_LIMITATIONS
FAIL
INCONCLUSIVE
```

Execution completion must never be silently converted into `PASS`.

## 13. CanonicalPointer Is Governed Mutable State

Large scientific outputs should remain immutable. The current preferred/canonical result can be represented by a small governed pointer.

Conceptually:

```yaml
canonical_pointer:
  scope: project:evopm
  role: official_tf_tree_release
  artifact: artifact-882
  decision: dec-72
  updated_at: ...
```

Updating the pointer requires the applicable Policy/Decision gate.

Historical Artifacts and previous pointer revisions remain traceable.

## 14. Context Retrieval Uses Multiple Channels

BioHarness should not require every task to traverse a hierarchy from broad domain to leaf nodes, nor should required constraints compete inside one semantic top-k list.

Recommended channels:

### 14.1 Mandatory deterministic context

Always load when applicable:

- current hard Policy;
- explicit blocking Decisions;
- resource identity/version constraints;
- critical contradictions/retractions;
- selected Project/Run context.

### 14.2 Exact reference lookup

Use when the request contains an exact identifier such as:

- Gene ID;
- Run ID;
- Artifact ID;
- workflow revision;
- paper DOI/accession;
- dataset/provider URI.

### 14.3 Hybrid associative recall

Use semantic similarity, keyword search, scope/time/version filters, and evidence weighting to find relevant ResearchMemory or procedural knowledge.

### 14.4 Graph/hierarchical expansion

Use typed edges and abstraction levels when the task requires multi-step scientific context or an exact reference is insufficient.

### Principle

Hierarchy is an organization and expansion strategy, not a mandatory retrieval path for every query.

## 15. Memory Evidence Must Track Independence

Raw run count is not equivalent to independent scientific support.

Memory/pathway evidence summaries should distinguish at least:

```text
execution_count
successful_execution_count
distinct_input_identity_count
distinct_dataset_or_experiment_count
independent_study_or_project_count
validation_type_count
contradiction_count
```

Two Runs against the same underlying dataset do not become two independent biological replications merely because they occurred in separate Projects.

Scope promotion must consider provenance correlation.

## 16. Negative and Null Results Are Valid Outcomes

BioHarness must not learn that "more significant hits" means "more successful science."

A scientifically valid analysis can conclude:

- no significant differential expression;
- no enriched GO term under the defined test/background;
- no supported motif effect;
- insufficient evidence to distinguish hypotheses;
- current design is not identifiable.

The system must not reward parameter changes merely because they increase the number of discoveries.

Memory consolidation should use validity, reproducibility, QC, and evidence quality rather than discovery count as a success proxy.

## 17. Scientific Assessment Is Versioned and Time-Aware

A historical Run preserves the assessment and context available when it was created.

A later reassessment can differ because of:

- retracted or corrected literature;
- new annotation/reference versions;
- newly discovered confounding;
- tool/version incompatibility;
- a new fatal contradiction;
- improved validation.

BioHarness preserves both:

```text
historical acceptance context
+
current applicability assessment
```

A new assessment does not rewrite the historical Run.

## 18. Relationship to Research Memory and Pathways

`ScientificTaskSpec`, `ScientificAssessment`, `ResolvedDataRef`, and `RunSpec` are authoritative analysis-state objects.

Research Memory remains derived knowledge.

A Memory Pathway may help recall:

- which task fields usually matter;
- which Data Providers should be queried;
- which Recipes/Modules are candidates;
- known pitfalls;
- prior validated defaults;
- previous contradictions.

The pathway cannot:

- invent missing experimental design;
- override current Policy;
- suppress a fatal scientific contradiction;
- replace current data/version resolution;
- silently promote a result to Canonical state.

## 19. Superseded Interpretations in Older Records

This record explicitly narrows or supersedes three earlier interpretations.

### 19.1 Single precedence ladder

`provider-composition-and-research-memory.md` contains an authority-oriented precedence ordering:

```text
Hard Policy > Explicit Project Decision > Canonical Fact > ...
```

That ordering remains useful for authority/configuration conflicts, but it must not be used as a general scientific-truth ranking.

Scientific validity is determined through `ScientificAssessment` and evidence/assumption checks.

### 19.2 Slot mutation receives a smaller stability penalty

`memory-pathway-consolidation-and-promotion.md` distinguishes structural and slot mutation and suggests slot mutation may carry a smaller penalty when declared adaptive.

That remains a possible pathway-stability statistic, but it no longer implies lower scientific impact.

Scientific invalidation/revalidation is determined by `ChangeImpactContract`.

### 19.3 Partial thaw follows only local graph replacement

`hierarchical-associative-memory.md` correctly supports partial thawing, but examples can be read as preserving all unchanged downstream graph structure automatically.

This record clarifies that unchanged topology does not imply unchanged scientific validity. Reuse is allowed only when compatibility and downstream dependency checks support it.

## 20. P0 Acceptance Boundary

The first implementation slice should demonstrate these contracts with one existing scientific workflow provider before introducing automatic pathway mining or a dedicated graph database.

Selected scenario:

- existing Genome-web TF Nextflow pilot;
- explicit registered genome identity;
- candidate-only result;
- no automatic publication;
- recovery/retry semantics exercised;
- independent validation required;
- at least one later task must show that a validated failure/compatibility lesson can affect context without becoming Policy automatically.

See `docs/architecture/p0-genome-web-tf-vertical-slice.md`.

## 21. Architecture Invariants Added by This Record

1. Authorization, scientific validity, and configuration resolution are separate outputs.
2. Policy can govern actions but cannot make an invalid scientific design valid.
3. Official execution starts from a structured ScientificTaskSpec; required unresolved fields remain explicit blockers.
4. Logical provider references are resolved to versioned/checkable data identities for governed Runs.
5. Revalidation scope follows dependency impact, not mutation label alone.
6. RunSpec identifies the intended computation; RunAttempt identifies one external execution attempt.
7. Lost submission acknowledgement produces `UNKNOWN`/reconciliation behavior, not blind resubmission.
8. Artifact existence is independent of ValidationReport outcome.
9. Canonical state is a governed pointer/decision, not a property inferred from file presence.
10. Mandatory policy/critical contradiction context must not depend on semantic top-k retrieval.
11. Repeated Runs do not automatically count as independent scientific support.
12. Null/negative results can be valid successful analyses.
13. Historical acceptance and current applicability are separately preserved.

## 22. Status

This document defines architecture only.

```text
contract_status = DESIGNED
runtime_status = NOT_IMPLEMENTED
scenario_validation = NOT_RUN
```

No statement in this record should be interpreted as evidence that the BioHarness runtime already enforces these contracts.
