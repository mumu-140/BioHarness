# BioHarness Memory Pathway Consolidation and Promotion

Date: 2026-09-18
Status: Authoritative memory-promotion design record
Runtime status: NOT_IMPLEMENTED
Validation status: NOT_RUN
Scope: How temporary TaskMemoryGraph structure becomes reusable MemoryPathway knowledge while keeping activation, maturity, scope, scientific impact, and evidence independence separate.

Cross-cutting scientific/run semantics are authoritative in `scientific-contracts-and-run-semantics.md`.

## 1. Decision

BioHarness must not consolidate a MemoryPathway merely because a subgraph appears frequently.

A repeated pathway can be common but wrong, stable but project-specific, reliable but dormant, or frequently edited while still immature.

Therefore pathway learning uses independent dimensions plus hard gates rather than one opaque scalar score.

Conceptually:

```text
frequency / task relevance   -> activation
scientific evidence          -> reliability
structural consistency       -> maturity signal
independent context diversity-> scope/generalization signal
change-impact compatibility  -> reuse/revalidation requirement
```

No aggregate score can bypass evidence, contradiction, scientific-assumption, or scope-promotion gates.

## 2. Independent Axes

### Activation

```text
HOT | WARM | DORMANT
```

How likely should this pathway be recalled now?

### Maturity / Stability

```text
EXPLORATORY | ADAPTIVE | STABLE | CONTRADICTED | DEPRECATED
```

How mature/evidence-backed is the reusable structure under its stated scope?

### Scope

```text
TASK | PROJECT | METHOD | LAB
```

Where is reuse justified?

Hard rule:

> Maturity promotion and scope promotion are separate operations.

A pathway may remain `STABLE + PROJECT` indefinitely.

## 3. Candidate Discovery

Candidates may be human-authored or proposed from repeated TaskMemoryGraphs.

Automatic proposal may abstract task-specific values into declared slots, for example:

```text
GeneRef
  -> ExpressionDatasetRef
  -> DifferentialAnalysis
  -> DifferentialGeneSet
  -> GeneIdMapping
  -> FunctionalEnrichment
```

Possible adaptive slots include species, assembly, dataset, contrast, DE method, software version, annotation source, FDR preset, and background universe.

Declaring a slot adaptive means the field is expected to vary; it does **not** say changes are scientifically low-impact.

## 4. Promotion Gates

### 4.1 Evidence Gate

A candidate retains traceable support from evidence-bearing objects such as:

- RunSpec/RunAttempt;
- Artifacts;
- typed ValidationReports;
- Findings;
- Decisions;
- Papers/reference workflows;
- benchmark evidence.

Model-generated text/retrieval co-occurrence alone cannot produce stable shared scientific memory.

### 4.2 Reliability Gate

Reliability asks whether the pathway supports scientifically acceptable work under its stated scope.

Signals may include typed validation, appropriate QC, manual review, benchmark agreement, reproducibility, correct null/negative outcomes, complete provenance, and known failure handling.

Raw execution success is insufficient.

### 4.3 Structural Stability Gate

Record whether pathway topology/reasoning roles change materially over time.

Examples:

```text
DEG -> GO
```

becoming:

```text
DEG -> ID mapping -> background validation -> GO
```

is a meaningful structural revision and usually indicates the pathway is still adapting.

Slot mutations are recorded separately from structural mutations for maturity/history statistics.

### 4.4 Scientific Change-Impact Gate

Structural-versus-slot classification does **not** determine scientific invalidation.

Every result-/assumption-sensitive slot change is evaluated by the authoritative `ChangeImpactContract` and compatibility predicates.

Examples:

- display/explanation preference may be presentation-only;
- FDR change alters selection and downstream gene-set evidence;
- annotation v3 -> v4 may invalidate mapping/background/enrichment;
- DESeq2 -> edgeR may alter method assumptions/results;
- bulk -> single-cell changes experimental-unit/model assumptions even if the pathway graph looks similar.

A small slot change can therefore require more revalidation than a larger-looking structural/presentation change.

### 4.5 Contradiction Gate

Contradictions are typed by severity, for example:

```text
MINOR
MAJOR
FATAL
```

- `MINOR`: does not affect scientific core/applicability;
- `MAJOR`: invalidates an important default/branch/assumption and triggers targeted thaw/revalidation;
- `FATAL`: challenges core applicability and blocks stable reuse until resolved.

One high-quality fatal contradiction can override many historical uses.

### 4.6 Generalization Gate

Run count is not independent support.

Scope promotion considers diversity/correlation across relevant dimensions such as:

```text
independent experiments/datasets
projects
species/biological contexts when relevant
method/software revisions
users/agents only when operationally relevant
validation types
```

Repeated reruns of one biological experiment do not establish METHOD/LAB generality.

## 5. Evidence Statistics

Useful summaries distinguish lifetime and recent behavior, while keeping scientific independence explicit:

```text
execution_count
successful_execution_count
valid_null_or_negative_count
distinct_input_identity_count
distinct_experiment_count
independent_project_or_study_count
contradiction_count
lifetime_structural_mutations
recent_structural_mutations
lifetime_slot_mutations
recent_slot_mutations
```

These statistics support review/ranking; none is scientific truth by itself.

## 6. Maturity Promotion

Typical progression:

```text
OBSERVED SUBGRAPH
  -> CANDIDATE
  -> ADAPTIVE
  -> STABLE
```

Promotion requires evidence/reliability plus decreasing unresolved structural churn under the stated scope.

`CONTRADICTED` and `DEPRECATED` are lifecycle/scientific states, not low numerical confidence.

A stable pathway can return to `ADAPTIVE` through explicit thaw/reconsolidation when new evidence/version changes require revision.

## 7. Scope Promotion

Typical route:

```text
TASK
  -> PROJECT
  -> METHOD_CANDIDATE
  -> METHOD
  -> LAB
```

METHOD/LAB promotion requires independent support under the intended scope and an explicit governed Decision/review when scientific applicability is non-trivial.

High use or high maturity in one project cannot silently create shared institutional knowledge.

## 8. Automatic vs Human/Governed Responsibilities

BioHarness may automate:

- repeated-subgraph detection;
- candidate creation;
- usage/evidence statistics;
- contradiction proposals;
- activation adjustment;
- frozen-core/adaptive-slot proposals;
- compatibility/change-impact checks;
- closeout/reactivation proposals.

Initial human/governed gates remain for:

- important PROJECT -> METHOD/LAB scope widening;
- accepting/resolving MAJOR/FATAL contradictions;
- changing locked shared knowledge;
- promoting scientific defaults/policy/canonical recommendations.

Automatic pathway mining itself is deferred until simpler memory baselines are evaluated.

## 9. Consolidation Confidence

A composite confidence may rank candidates for review but remains advisory.

```text
ConsolidationConfidence != scientific truth
ConsolidationConfidence != scope authority
ConsolidationConfidence != Policy authority
```

Do not hard-code arbitrary universal weights before benchmark evidence exists.

## 10. Reactivation / Reconsolidation

Reactivation never means "reuse unchanged graph = reuse valid evidence".

Required sequence:

```text
dormant/stable pathway
  -> relevant task
  -> current data/method/policy/contradiction resolution
  -> ChangeImpact + compatibility traversal
  -> reuse compatible components/evidence only
  -> thaw/recompute/revalidate affected dependencies
  -> new evidence
  -> new versioned pathway revision
```

The old revision remains addressable.

## 11. Project Closeout

Closeout can replay project history to propose reusable knowledge, but it should inspect all evidence-bearing outcomes:

- successful analyses;
- valid null/negative Findings;
- failed executions with reusable lessons;
- scientifically blocked designs;
- contradictions;
- Decisions and validation evidence.

Closeout separates project-only knowledge from reusable Method/Lab candidates and reduces activation of low-value working traces. It does not delete historical evidence.

## 12. MemoryPathway Promotion Invariants

1. Frequency primarily affects recall/activation, not scientific authority.
2. Activation, maturity, and scope remain separate.
3. Run count is not independent biological evidence.
4. Slot changes are not automatically lower scientific impact than structural changes.
5. Dependency-aware ChangeImpact determines reuse/revalidation.
6. Fatal contradictions can block reuse regardless of historical frequency.
7. Shared scope widening requires independent support and governed promotion.
8. Null/negative outcomes can support a reliable pathway when scientifically valid.
9. Automatic discovery/proposals do not bypass human/governed scientific promotion gates.
10. Previous pathway revisions remain traceable through thaw/reconsolidation.

## 13. Status

```text
pathway_promotion_contract = DESIGNED
runtime = NOT_IMPLEMENTED
validation = NOT_RUN
```