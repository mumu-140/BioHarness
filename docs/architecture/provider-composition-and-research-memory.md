# BioHarness Provider Composition and Research Memory Architecture

Date: 2026-09-18
Status: Authoritative memory/provider design record
Runtime status: NOT_IMPLEMENTED
Scope: Provider composition, three-layer information model, ContextSnapshot role, ResearchMemory contract/lifecycle, and memory-to-decision governance.

Cross-cutting scientific/run semantics are authoritative in `scientific-contracts-and-run-semantics.md`.

## 1. Decision Summary

BioHarness uses a **Semantic Kernel + Provider/Adapter** architecture.

BioHarness owns research semantics; mature systems own implementation capability. It must not merge FlowKit, TiMEM, Nextflow, Snakemake, Genome-web, TBtools, vector stores, or graph engines into one codebase merely to gain control.

```text
Clients
  Web / CLI / MCP / Agent / SDK
        |
        v
BioHarness Research Control Plane
  task / context / policy
  recipe / module / workflow registry
  RunSpec / RunAttempt / Artifact
  validation / Finding / Decision
  ResearchMemory
        |
        +------ Data Providers
        +------ Workflow / Tool / Compute Providers
        +------ Memory / Retrieval Providers
```

Provider-specific implementation details remain behind adapter contracts.

## 2. Provider Roles

### Genome-web -> Data Provider

Genome-web remains the primary source for curated genome-centric biological records. BioHarness references/resolves Genome-web resources rather than duplicating its full domain schema.

### Nextflow / Snakemake -> Workflow Executors

BioHarness does not create another DAG engine. It owns intended-work identity, data/configuration/context/provenance contracts, and execution governance; the external engine owns task-graph execution.

Concrete executor guarantees are revision-scoped capabilities, not assumptions attached to the word "Nextflow" or "Snakemake".

### CLI / API / MCP / R / Python / container / TBtools -> Tool Providers

Tools remain independent capabilities registered with transparent scientific/runtime contracts.

### TiMEM / pgvector / Qdrant / Graphiti-like systems -> Memory/Retrieval Providers

These may supply temporal organization, indexing, vector recall, graph traversal, or consolidation primitives. They do not redefine BioHarness evidence, scope, lifecycle, Policy, Finding, Decision, or canonical semantics.

A dedicated graph database remains optional until workload demonstrates need.

## 3. Three Information Layers

BioHarness strictly separates:

### 3.1 Authoritative state

Examples:

- Project/Task records;
- ResolvedDataRefs;
- RunSpec/RunAttempt state;
- immutable Artifact identity;
- typed validation results;
- explicit Finding/Decision;
- current Policy revision;
- CanonicalPointer;
- Git/provider revisions.

Authoritative state lives in explicit governed stores, not model recollection.

### 3.2 Derived ResearchMemory

Reusable knowledge derived from evidence, for example:

- recurring workflow failure conditions;
- version-specific incompatibilities;
- project decisions/reasons useful later;
- validated parameter behavior under a stated scope;
- literature-derived method caveats;
- summaries of evidence-linked Findings.

Memory is derived and scope-bound. It is not the original source of truth.

### 3.3 Ephemeral model/task context

Temporary information loaded for one reasoning/action cycle. It is disposable and never authoritative by itself.

Invariant:

> Authoritative state, derived memory, and ephemeral model context must never be conflated.

## 4. ResearchMemory Scope

At minimum:

```text
USER
PROJECT
METHOD / WORKFLOW
LAB / SHARED
```

Scope is explicit. A user preference does not become a laboratory scientific default; a project exception does not become a Method rule merely because it was recalled frequently.

## 5. ResearchMemory Contract

Illustrative shape:

```yaml
research_memory:
  id: mem-8392
  scope: {type: project, id: poplar-rnaseq}
  kind: failure_lesson
  claim: ...
  evidence_refs:
    - run_attempt: ...
    - artifact: ...
    - validation: ...
    - finding: ...
  subject_versions: [...]
  observed_at: ...
  recorded_at: ...
  valid_from: ...
  valid_to: ...
  status: ACTIVE
  maturity: ...
  confidence: ...
  supersedes: ...
  contradiction_refs: [...]
```

Important semantics:

- scope and kind;
- evidence/provenance;
- subject data/software/method versions;
- observation/recording/applicability time;
- lifecycle/maturity;
- supersession/contradiction.

A model-generated statement or retrieval co-occurrence without evidence cannot become stable shared scientific memory.

## 6. Memory Lifecycle

Suggested lifecycle states:

```text
ACTIVE
STALE
SUPERSEDED
CONTRADICTED
ARCHIVED
RETRACTED
DELETED
```

Do not use one generic recency-decay function for all scientific knowledge.

- scratch/model inference may stale quickly;
- software-version lessons stale when subject versions change;
- validated failure lessons can remain useful for long periods;
- evidence-linked Findings do not become false merely because they are old, but their current applicability may change;
- Policy lifecycle is governed separately from memory activation/decay.

Deletion is exceptional; supersession/contradiction is preferred where scientific history matters.

## 7. Temporal Semantics

A single `created_at` is insufficient. Preserve relevant distinctions such as:

- `observed_at` — when evidence was observed;
- `recorded_at` — when BioHarness stored the memory;
- `valid_from` / `valid_to` — asserted applicability interval;
- `superseded_at` — when a newer record replaced it.

Current applicability may be reassessed without rewriting what the laboratory believed historically.

## 8. ContextCompiler

`ContextCompiler` constructs reproducible planning/execution context; it is not a vector top-k wrapper.

Potential inputs:

- actor/project/task;
- authorized/resolved data references;
- candidate methods/workflows and capability snapshots;
- historical/current relevant policies/decisions;
- exact references;
- required contradictions/retractions;
- relevant ResearchMemory;
- current software/environment constraints.

It produces an immutable `ContextSnapshot` for historical reproducibility.

A ContextSnapshot answers:

> What information, constraints, decisions, and memory were considered for this planning/execution state?

It does **not** answer:

> Is this actor still authorized to perform a protected action now?

Current authorization is action-scoped and evaluated separately where required.

## 9. Context Conflict Handling

Semantic similarity never overrides hard authority/constraints.

For **authority/configuration resolution**, a conceptual precedence may be useful:

```text
current Hard Policy
  > explicit governed Decision
  > current canonical selection / validated authoritative state
  > validated/evidence-supported Memory
  > user preference
  > unvalidated observation
  > model inference
```

This is **not a scientific-truth ranking**. Scientific feasibility/claims are evaluated through ScientificAssessment, typed validation, evidence, and Findings.

Conflicts are recorded rather than silently blended.

Mandatory policy/critical contradiction context is deterministic; it does not compete with optional memories in semantic top-k retrieval.

## 10. External Content Trust

Literature, web content, provider/tool output, model text, and recalled memory may contain instruction-like strings.

They remain data/evidence. They cannot by themselves grant authority, create Policy, launch commands, change gates, or mutate canonical state.

Only typed authorized control-plane operations can mutate governed state.

## 11. Memory Promotion and Governance

Research experience becomes reusable/institutional knowledge through explicit evidence and governance, not direct retrieval mutation.

Typical routes:

```text
Observation / MemoryCandidate
  -> evidence / Experiment / typed validation
  -> scoped ResearchMemory and/or Finding
  -> Decision
  -> optional Workflow preset / Rule / Policy / Canonical recommendation
```

Important boundaries:

- ResearchMemory may summarize a Finding but does not replace it;
- Memory does not create a Finding merely by being recalled;
- Memory cannot directly become Policy;
- wider scope requires independent support, not high run count;
- a high-quality fatal contradiction can block reuse regardless of historical frequency.

## 12. Feedback Loop

```text
Task + current data/method state
  -> context / feasibility / authorization
  -> governed execution
  -> Artifact + Validation
  -> Finding / Decision
  -> scoped ResearchMemory
  -> future context/configuration proposals
```

The goal is not "remember more"; it is evidence-backed reuse without losing scientific or governance boundaries.

## 13. Research Memory Graph

Useful graph edges emerge from research lifecycle objects:

```text
Paper -> supports -> Recipe
Recipe -> implemented_by -> Workflow
Workflow -> executed_as -> RunSpec/RunAttempt
RunAttempt -> produced -> Artifact
Artifact + Validation -> evidence_for -> Finding
Finding -> summarized_as -> ResearchMemory
ResearchMemory -> supports/motivates -> Decision
Decision -> updates -> Preset / Policy / CanonicalPointer
```

Other edges include `derived_from`, `contradicted_by`, `supersedes`, `validates`, `invalidates`, `compared_with`, `selected_over`, `reproduced_by`, and `failed_under`.

Initial implementation can use relational node/edge tables plus optional vector indexes. Graph infrastructure is an adapter choice.

## 14. Event Model

Domain events may include:

```text
RunSpecCreated
AttemptCreated
AuthorizationChecked
ExecutionStarted / Finished / Failed
ArtifactRegistered
ValidationReported
FindingRecorded
DecisionRecorded
CanonicalPointerChanged
PolicyChanged
MemoryCandidateCreated
MemorySuperseded / Contradicted
```

A modular-monolith transaction/outbox approach is sufficient initially; Kafka is not required.

## 15. Storage Composition

### BioHarness state store

Stores projects/tasks, policies/decisions, recipe/module/workflow metadata, ContextSnapshots, RunSpec/RunAttempt/RunEvent, artifact metadata, validation, Findings, canonical history, ResearchMemory, provenance edges, and audit events.

### Semantic index

Start with operationally simple retrieval infrastructure such as pgvector; introduce Qdrant or other systems only if workload justifies it.

### Large artifacts

Use object storage or managed filesystem references rather than relational blobs.

### Source biological data

Remain in Genome-web/external/project Data Providers.

## 16. Headless Operation

Equivalent governed operations must be available through API/CLI/SDK/MCP/notebook paths without requiring Web.

Web may render DAGs, RunAttempt progress, validation, Findings, provenance, memory/decision lineage, and comparisons, but is not authoritative for research semantics.

## 17. Provider/Memory Invariants

1. BioHarness owns stable scientific/governance semantics; providers own implementation capabilities.
2. Authoritative state, derived memory, and ephemeral context are separate.
3. ContextSnapshot is immutable historical context, not a current authorization token.
4. Authority/configuration precedence is not a scientific-truth ranking.
5. Mandatory policy/critical contradictions do not depend on semantic top-k retrieval.
6. Memory is evidence-linked and explicitly scoped/version-aware.
7. Memory cannot directly become Policy, Finding, Decision, or Canonical state.
8. Provider guarantees are revision-scoped capabilities.
9. Graph/vector products are replaceable infrastructure.
10. Web remains a client.

## 18. Status

```text
provider_memory_contract = DESIGNED
runtime = NOT_IMPLEMENTED
validation = NOT_RUN
```