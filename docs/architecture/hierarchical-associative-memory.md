# BioHarness Hierarchical Associative Memory Architecture

Date: 2026-09-18
Status: Authoritative memory architecture record
Runtime status: NOT_IMPLEMENTED
Validation status: NOT_RUN
Scope: Hierarchical/associative retrieval, TaskMemoryGraph, MemoryPathway, MemoryPack, dormancy/reactivation, and controlled plasticity.

Cross-cutting scientific validity, authorization, data identity, and revalidation rules are authoritative in `scientific-contracts-and-run-semantics.md`.

## 1. Design Thesis

BioHarness should not model research memory as a flat vector-store prompt dump.

The target architecture is:

1. persistent memory is typed/indexed by scientific abstraction, scope, time/version, evidence, and relationships;
2. a new task is decomposed into scientific subproblems;
3. exact references and mandatory constraints are resolved deterministically when available;
4. associative/hierarchical retrieval expands only where useful;
5. activated material forms a temporary `TaskMemoryGraph`;
6. repeated evidence-backed structures may become reusable `MemoryPathway`s;
7. pathways can retain a stable core while selected slots remain adaptive;
8. project lifecycle controls activation/plasticity, not truth;
9. closeout consolidates/cools memory rather than deleting evidence;
10. later tasks may reactivate and selectively thaw pathways under explicit compatibility/change-impact checks.

This is a cognitive engineering analogy, not a claim to reproduce biological neural mechanisms.

## 2. Persistent Research Memory

A memory node may carry:

- semantic embedding/index keys;
- typed scientific concepts/tags;
- scope: User / Project / Method / Lab;
- abstraction level;
- typed edges;
- valid/observed/recorded time;
- software/data/method version constraints;
- evidence/maturity/lifecycle state;
- provenance refs to RunSpec/RunAttempt, Artifact, ValidationReport, Finding, Decision, Paper, or provider data.

Vectors are retrieval infrastructure, not the memory model itself.

Initial retrieval can combine:

```text
exact identifiers
+ keywords
+ vector similarity
+ scope/time/version filters
+ typed hierarchy/graph relations
+ evidence/maturity weighting
```

Mandatory Policy/critical contradiction context never depends on probabilistic top-k recall.

## 3. Scientific Abstraction Hierarchy

Illustrative hierarchy:

```text
L0 Research Domain
  Transcriptomics / Genomics / Evolution / Structure / Statistics

L1 Capability
  RNA-seq / Differential Expression / GO Enrichment / Gene Search

L2 Method / Recipe
  DESeq2 / edgeR / clusterProfiler / nf-core-rnaseq / lab recipes

L3 Concrete Context
  project decision / dataset / configuration / workflow revision

L4 Evidence
  Run / Artifact / Validation / Finding / Paper / failure / benchmark / logs
```

Time is orthogonal metadata rather than the main hierarchy axis.

## 4. Task Decomposition and TaskSpec Relationship

A request is first decomposed enough to expose its scientific ambiguities/branches.

Example:

```text
"for this gene, get differential genes and do GO enrichment"
  -> gene/resource identity
  -> expression dataset / experimental design
  -> requested comparison or gene-set rule
  -> differential-analysis capability
  -> identifier mapping
  -> tested/background universe
  -> enrichment capability
```

Memory retrieval may help the system recall which questions, data providers, pitfalls, or method contracts matter. It must **not** silently invent missing experimental design.

The resulting governed `ScientificTaskSpec` records the resolved scientific intent; unresolved required fields remain blockers.

## 5. Retrieval Modes

### Mandatory deterministic context

Applicable Policy constraints, explicit blocking Decisions, critical contradictions/retractions, and selected exact project/resource context.

### Exact lookup

Use exact Gene/Run/Artifact/DOI/accession/workflow/provider IDs directly rather than forcing root-to-leaf traversal.

### Associative recall

Retrieve relevant ResearchMemory/pathways using semantic, keyword, scope, version, time, and evidence signals.

### Graph/hierarchical expansion

Follow typed relationships when a task requires multi-hop context or exact lookup is insufficient.

Hierarchy is an organization/expansion mechanism, not a mandatory path for every query.

## 6. TaskMemoryGraph: Temporary Working Memory

`TaskMemoryGraph` is temporary task-scoped working context assembled from authoritative refs, candidate methods, retrieved memory, decisions, evidence, and unresolved gaps.

It is not the permanent knowledge graph and does not automatically mutate persistent memory.

Conceptual lifecycle:

```text
Request / decomposition
  -> exact + mandatory context
  -> associative/graph expansion
  -> TaskMemoryGraph
  -> ScientificTaskSpec / ScientificAssessment / ContextSnapshot
  -> RunSpec / execution / evidence
  -> governed consolidation proposals
```

External/retrieved text inside the graph remains data/evidence, not control authority.

## 7. MemoryPathway: Reusable Recall/Reasoning Template

A `MemoryPathway` describes which scientific roles, providers, methods, checks, and memories usually need to be connected for a class of tasks.

Example:

```text
gene/resource
  -> expression dataset
  -> explicit comparison
  -> differential analysis
  -> selected gene set
  -> ID mapping
  -> tested/background universe
  -> enrichment
```

A MemoryPathway is **not** a Workflow:

- Workflow = executable computation/DAG.
- MemoryPathway = reusable recall/reasoning structure and applicability conditions.

It may propose candidate workflows/configuration but cannot bypass ScientificAssessment, PolicyDecision, ResolvedDataRef, or current version checks.

## 8. Pathway Discovery and Promotion

Pathways may be human-authored or automatically proposed from repeated TaskMemoryGraphs.

Automatic proposal may consider:

- recurring structure;
- validated outcomes;
- evidence strength;
- cross-task/project diversity;
- edit/mutation history;
- contradictions;
- version/scope compatibility.

Frequency alone is never scientific reliability.

Initial implementation should prioritize human-reviewed pathways and evidence collection; automatic pathway mining is deferred until simpler retrieval/pathway baselines are evaluated.

## 9. Independent Pathway Axes

Every durable pathway keeps separate dimensions.

### Activation

```text
HOT | WARM | DORMANT
```

How likely should it be recalled now?

### Maturity / Stability

```text
EXPLORATORY | ADAPTIVE | STABLE | CONTRADICTED | DEPRECATED
```

How mature/evidence-supported is the reusable structure under its scope?

### Scope

```text
TASK | PROJECT | METHOD | LAB
```

Where is reuse justified?

Key invariants:

- `STABLE + DORMANT` is valid: mature but inactive;
- maturity does not imply broader scope;
- activation does not imply authority;
- pathway maturity is not a universal scientific-truth score.

## 10. Project Lifecycle and Closeout

During an active project, relevant pathways may be highly active/plastic. Stabilization reduces structural churn. Project closeout should:

1. preserve exact historical provenance;
2. separate project-specific from potentially reusable knowledge;
3. propose evidence-backed pathway/MemoryPack consolidation;
4. cool temporary working traces and project-specific activation.

Closeout should examine **all evidence-bearing outcomes**, including valid null results, blocked scientific designs, failures, and contradictions—not only successful executions.

Project completion changes default activation; it does not automatically invalidate or delete evidence.

## 11. Dormancy

BioHarness primarily forgets by reducing activation rather than destroying scientific history.

```text
HOT -> WARM -> DORMANT
```

A dormant pathway keeps enough index metadata for later discovery while heavy historical details remain behind references.

`DORMANT != DEPRECATED`.

## 12. Reactivation and Dependency-Aware Partial Thaw

Reactivation:

```text
DORMANT
  -> relevant task
  -> compatibility + contradiction + ChangeImpact checks
      -> reuse compatible components/evidence
      -> thaw/recompute/revalidate affected dependencies
```

A stable graph shape does **not** prove that old evidence or downstream assumptions remain valid.

Compatibility may depend on:

- species/reference/annotation version;
- data schema/ID namespace;
- experimental unit/design;
- software/module/workflow revision;
- method assumptions and result-affecting configuration;
- current policy/access constraints;
- contradictions/retractions;
- runtime/reproducibility contract.

### Bulk -> single-cell example

A prior bulk RNA-seq pathway may help recall reusable roles, tools, ID mapping concepts, GO-enrichment requirements, and known pitfalls. It does **not** justify reusing the old DEG evidence or automatically reusing downstream mapping/background/enrichment results.

The new task must re-evaluate:

- independent experimental unit;
- differential model/contrast;
- gene-selection process;
- resulting selected gene set;
- identifier mapping applicability;
- tested/background universe;
- annotation/version compatibility;
- downstream enrichment validity.

Only components/artifacts whose compatibility predicates pass may be reused.

## 13. Reconsolidation

A reactivated/thawed pathway is updated through a new explicit revision:

```text
old stable/dormant revision
  -> reactivation
  -> dependency-aware thaw
  -> new TaskMemoryGraph / evidence / validation
  -> new pathway revision
  -> ADAPTIVE or STABLE after review/evidence
```

Previous revisions remain addressable for reproducibility.

## 14. MemoryPack

Modules, Recipes, or Workflows may expose an optional `MemoryPack`: a versioned index/view pointing to procedural knowledge and evidence.

Typical contents:

- when-to-use / when-not-to-use;
- upstream semantic expectations;
- downstream associations;
- parameter rationale;
- known pitfalls/version caveats;
- validated presets and evidence refs;
- relevant Findings/Decisions;
- interpretation guidance.

Source-of-responsibility rule:

- Module/Recipe/Workflow revision owns authoritative method/interface contract;
- MemoryPack indexes reusable experience/evidence around that contract;
- MemoryPathway describes recall roles/relations/applicability;
- RunSpec binds an executable configuration.

MemoryPack must not duplicate mutable Policy or method contracts as a second source of truth.

## 15. Controlled Plasticity

Useful classes:

```text
LOCKED
ADAPTIVE
EXPLORATORY
```

`LOCKED` means governed institutional/shared knowledge that agents cannot silently mutate; it does not convert memory into Policy.

`ADAPTIVE` pathways expose declared slots but every change remains subject to ChangeImpact/compatibility checks.

`EXPLORATORY` associations may evolve freely inside non-authoritative exploratory scope.

Thawing is audited/versioned and never erases prior revision history.

## 16. Frozen Core and Adaptive Slots

A pathway may have a stable conceptual core and adaptive slots such as species, dataset, contrast, DE method, software version, annotation source, FDR preset, or background universe.

Important rule:

> Declaring a field adaptive means it may vary; it does not mean a change is scientifically low-impact.

A slot change can trigger broad downstream invalidation/revalidation according to the authoritative ChangeImpactContract.

## 17. Scope Overlays

Composition may use:

```text
Shared Base
+ Project Overlay
+ User Overlay
+ Current Task
-> TaskMemoryGraph
```

Project overlays may provide project-specific datasets, reference versions, exclusions, or governed Decisions.

User overlays may alter explanation/presentation preferences but cannot override scientific validity, current Policy, or authoritative data identity.

## 18. Associative Edge Strength

Edge strength may help retrieval ranking using evidence-linked signals such as coactivation, validated reuse, scope relevance, contradictions, staleness, and failures.

Weights remain advisory and provenance-bearing. They never replace Policy, ScientificAssessment, validation, or evidence.

## 19. Fast and Slow Loops

Fast task loop:

```text
request -> exact/mandatory context -> pathway/associative recall
        -> TaskMemoryGraph -> governed planning/execution
```

Slow consolidation loop:

```text
TaskMemoryGraph + execution/validation/Finding/Decision evidence
        -> evidence/statistics review
        -> pathway/memory candidate
        -> governed promotion/revision
```

Closeout loop cools inactive traces while preserving reusable indexes and provenance.

## 20. Deletion

Durable scientific memory is not deleted merely because it is old or inactive.

Hard deletion requires explicit authorized action or a retention/privacy/compliance Policy, except for disposable caches/index material/scratch working copies whose provenance role is not required.

## 21. Memory Safety Invariants

1. Memory is derived knowledge, not automatically authoritative state.
2. TaskMemoryGraph is temporary by default.
3. Memory cannot override current Policy, ResolvedDataRef, ScientificAssessment, typed validation, or a fatal contradiction.
4. Memory cannot directly become Finding, Policy, Decision, or Canonical state.
5. Activation, maturity, and scope are independent.
6. Adaptive-slot changes follow dependency-aware impact/revalidation.
7. Unchanged topology is not evidence of unchanged scientific validity.
8. Shared thaw/promotion/reconsolidation is auditable/versioned.
9. Project closeout consolidates/cools; it does not erase evidence.
10. Hard deletion of durable scientific history requires explicit authority/policy.

## 22. Provider Strategy

Initial implementation may use PostgreSQL for authoritative metadata/edges/pathways, pgvector or Qdrant for semantic indexes, TiMEM-like providers for temporal memory primitives, and Graphiti/Neo4j only if real multi-hop workload justifies it.

BioHarness owns TaskMemoryGraph/MemoryPathway/MemoryPack semantics, scope/evidence/lifecycle/governance—not the underlying vector/graph engine.

## 23. Research Direction

Potential novelty lies in evaluating the combination of:

- hierarchical scientific-memory activation;
- temporary TaskMemoryGraph construction;
- evidence-grounded reusable MemoryPathways;
- MemoryPacks around scientific capabilities;
- activation/maturity/scope separation;
- project-aware dormancy/reactivation;
- dependency-aware thaw/reconsolidation;
- governed integration with data identity, scientific feasibility, execution, validation, Finding, Decision, and provenance.

This remains a research hypothesis until benchmarked against simpler baselines.