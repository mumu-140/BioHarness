# BioHarness Architecture Design

Date: 2026-09-18
Status: Authoritative stable product-boundary design
Runtime status: NOT_IMPLEMENTED
Scope: Stable system boundary, ownership, provider composition, core domain roles, and V1 constraints. Detailed scientific/run semantics live in `docs/architecture/scientific-contracts-and-run-semantics.md`.

## 1. Purpose

BioHarness is a **headless Research Control Plane for computational science**.

It is not a genome database, web portal, new workflow language, graph database, or replacement for mature bioinformatics software. It coordinates humans/agents, scientific data, reusable methods, external execution, evidence, validation, decisions, and research memory so analyses are governed, reproducible, inspectable, and reusable.

The system must remain fully usable through API/CLI/SDK/MCP/notebooks without a Web frontend.

Central question:

> Given a scientific request, available data and methods, current authority, and prior evidence, what analysis may be performed, what exactly ran, what evidence resulted, what can be concluded, and what should be reusable later?

## 2. System Boundary

### Data Providers

Data Providers own source scientific data and domain-specific query semantics.

Examples:

- Genome-web backend/PostgreSQL;
- filesystem/object stores;
- external biological databases;
- transcriptome/phenotype/variant/project stores.

Genome-web remains the first biological Data Provider. BioHarness references/resolves its resources rather than copying its domain schema merely for ownership.

### BioHarness

BioHarness owns cross-cutting research-control semantics:

- Project and actor/task scope;
- ScientificTaskSpec and scientific feasibility contracts;
- Policy/authorization decisions;
- Recipe/Module/Workflow registry metadata;
- ResolvedConfiguration and ContextSnapshot;
- RunSpec/RunAttempt/RunEvent lifecycle;
- Artifact metadata/provenance;
- typed ValidationReports/ValidationProfiles;
- Finding and Decision records;
- CanonicalPointer governance;
- ResearchMemory semantics/lifecycle;
- agent governance and auditability.

### Clients

Clients invoke and present BioHarness:

- CLI;
- REST API;
- SDK;
- MCP/agent clients;
- notebook integrations;
- optional Web workbench.

The frontend never owns authoritative scientific workflow logic, policy, defaults, or canonical state.

## 3. Architectural Position

BioHarness uses a **modular monolith + ports/adapters** initially.

Reuse mature lower-level systems:

- Nextflow/Snakemake/Galaxy for workflow execution;
- existing CLI/Python/R/container/API/MCP/TBtools tools;
- Genome-web and other stores for biological source data;
- PostgreSQL/object storage for BioHarness state/artifacts;
- pgvector/Qdrant or optional graph providers only when workload justifies them.

The distinct layer is the closed loop:

```text
scientific request
  -> explicit task/data/method contracts
  -> feasibility + current authorization
  -> governed execution
  -> immutable evidence + typed validation
  -> Finding / Decision / Memory
  -> future context/configuration proposals
```

BioHarness does not create another general DAG engine or universal scientific ontology.

## 4. Core Invariants

### I1. Reuse mature scientific algorithms

Scientific algorithms remain external whenever practical and are integrated through typed contracts/adapters.

### I2. Headless operation

Removing Web must not prevent planning, execution, validation, result inspection, or memory/policy operation.

### I3. Data Providers remain authoritative for source data

BioHarness stores checkable references, provenance, and analysis state; it does not become a shadow copy of every provider database.

### I4. Governed protected actions

Protected reads, official execution, cancellation, publication, canonical mutation, shared-memory promotion, and policy changes go through current authorization where applicable.

### I5. Historical evidence is immutable by default

RunSpec, RunAttempt history, Artifacts, ValidationReports, Findings, Decisions, and historical ContextSnapshots are not silently overwritten. New analysis/reassessment creates new records/revisions.

### I6. Scientific roles are explicit

Execution completion, validation, Finding, Decision, Memory, and canonical publication are distinct. A file on disk or provider `PASS` is not automatically scientific truth or an official result.

### I7. Memory is evidence-linked and derived

Scientific ResearchMemory preserves scope, time, evidence/provenance, status, and applicability. Model recollection is never authoritative by itself.

### I8. Memory cannot mutate governed state directly

Retrieval can influence proposals/context. Policy, Findings, canonical state, or shared defaults change only through their typed governed operations.

### I9. Provider guarantees are capability-declared

BioHarness does not infer async polling, exactly-once semantics, cancellation, reproducibility, or other guarantees from a provider/tool name.

### I10. Current applicability and historical reproducibility coexist

Historical context explains what was known/allowed at the time. It does not grant current access or prove an old result remains applicable under changed data/method/policy.

## 5. High-Level Architecture

```text
                         USERS / AGENTS
                              |
            CLI / SDK / MCP / Notebook / Web
                              |
                              v
                  +-------------------------+
                  |       BioHarness        |
                  | Research Control Plane  |
                  +-------------------------+
                  | task/assessment         |
                  | context + authorization |
                  | recipe/module registry  |
                  | run/attempt/events      |
                  | artifact/validation     |
                  | finding/decision        |
                  | provenance/memory       |
                  +------+------------+-----+
                         |            |
             +-----------+            +------------------+
             v                                           v
      Data Providers                              Execution/Tools
      Genome-web                                  Nextflow/Snakemake
      files/object store                          CLI/API/MCP
      external DBs                                R/Python/containers
```

Memory providers and retrieval indexes sit behind BioHarness memory semantics; they are not a separate authority plane.

## 6. Core Domain Roles

### Project

Research scope in which analyses, decisions, memories, outputs, and policy applicability are interpreted.

### ScientificTaskSpec

Structured scientific intent and required biological/statistical semantics. It does not contain ordinary provider defaults unless the question explicitly fixes them.

### ResolvedDataRef

Versioned/checkable identity of the scientific data actually resolved/consumed, including collection membership where relevant.

### ScientificAssessment

Pre-execution feasibility/identifiability assessment bound to explicit data and method-contract dependencies. It never means a biological hypothesis is supported.

### Policy / PolicyDecision

Policy is normative governance. PolicyDecision is a current actor/action/resource authorization result. Historical decisions remain evidence, not reusable capability tokens.

A scientific method requirement such as minimum design/replicate adequacy normally belongs to a Module scientific contract/ScientificAssessment. It becomes Policy only when the laboratory/project explicitly chooses to enforce it normatively.

### Recipe

Scientific rationale: what method is being applied, why, assumptions/references, and intended validation.

### Module

Typed reusable computational/scientific capability with inputs/outputs, scientific preconditions, software/provider revision, parameters, QC/validation expectations, interpretation limits, and failure modes.

### Workflow

Executable composition of Modules. BioHarness records/governs it but delegates task-graph execution to mature workflow engines.

### Experiment

Structured comparison of analyses/configurations/methods with explicit variables, metrics, constraints, evidence, and resulting Decision.

### ContextSnapshot

Immutable historical snapshot of resolved context used for planning/execution: project/actor, data refs, policies/decisions considered, method/workflow availability, relevant memories, limitations, and other required context.

It answers what was known/considered at that point; it is not a current authorization token.

### ResolvedConfiguration

One exact executable choice compatible with the TaskSpec/ScientificAssessment, including method/workflow revisions and result-affecting settings.

### RunSpec

Immutable intended-work identity. It freezes result-affecting inputs/configuration/environment contracts and references historical planning context. It is not one concrete external job.

### RunAttempt / RunEvent

RunAttempt is one concrete BioHarness external execution binding for a RunSpec. RunEvent is append-only execution/audit evidence. Provider-engine internal retries remain distinct from new BioHarness launches.

### Artifact

Immutable produced/registered output or execution evidence.

Artifact content does not mutate from CANDIDATE to VALIDATED/CANONICAL. Validation and canonical selection are separate records/state.

### ValidationReport / ValidationProfile

ValidationReport is a typed, revisioned assessment of a specific subject. ValidationProfile is a versioned gate definition over required reports/outcomes.

### Finding

Evidence-linked scoped scientific interpretation/claim from completed work. It may be positive, negative, null, inconclusive, contradicted, superseded, or retracted. A Finding is not automatically canonical or reusable Memory.

### Decision

First-class rationale for a scientific/operational choice: selecting a configuration, excluding a sample, accepting evidence, choosing a canonical result, changing a preset, resolving a contradiction, or promoting knowledge.

### CanonicalPointer

Small governed mutable pointer to the currently selected official Artifact/result role. Updates are current-authorized and revision-checked; history remains traceable.

### ResearchMemory

Time-aware, scoped, evidence-backed reusable knowledge derived from research activity. It remains separate from authoritative state and ephemeral model context.

## 7. Context and Authorization

Context compilation is not top-k memory retrieval. It combines authoritative provider state, exact references, required constraints, project/task state, decisions, and optional memory recall into a reproducible historical ContextSnapshot.

Retrieval channels are conceptually:

```text
mandatory deterministic constraints
+ exact lookup
+ hybrid associative recall
+ graph/hierarchical expansion when useful
```

External/retrieved content is data/evidence, not control-plane instruction.

Authorization is evaluated when protected actions occur. A ContextSnapshot can contain the PolicyDecision used for an earlier action but never substitutes for a new required current decision.

Detailed semantics are authoritative in `scientific-contracts-and-run-semantics.md`.

## 8. Research Memory Plane

The memory system is a semantic layer, not one database product.

Scopes include User, Project, Method/Workflow, and Lab/Shared. Types may include observations, failure lessons, Findings/Decision summaries, preferences, procedure hints, software/version notes, hypotheses, and literature-derived knowledge.

Memory keeps explicit time/lifecycle/provenance and can be ACTIVE, STALE, SUPERSEDED, CONTRADICTED, ARCHIVED, RETRACTED, or DELETED as appropriate.

Promotion is explicit:

```text
observation / candidate
  -> evidence / experiment / validation
  -> scoped memory or Finding
  -> Decision
  -> optional preset/rule/policy change
```

Frequency alone cannot establish scientific reliability or wider scope.

Detailed hierarchical/pathway semantics live in the dedicated memory records and remain constrained by the cross-cutting scientific/run contract.

## 9. Scientific and Execution Lifecycles

### Analysis progression

```text
Explore -> Reproduce/Build -> Validate -> Reuse -> Optimize -> Promote
```

### Execution

The authoritative execution unit is RunAttempt, not a monolithic mutable Run lifecycle:

```text
DRAFT -> SUBMITTING -> QUEUED/RUNNING -> COLLECTING -> FINISHED
                     \-> FAILED / CANCELLED / UNKNOWN
UNKNOWN -> reconciled state | NEEDS_OPERATOR_RECONCILIATION
```

Execution `FINISHED` is independent from validation and interpretation.

### Result designation

Artifacts are immutable. Result trust/designation is expressed through typed ValidationReports, Findings/Decisions, and CanonicalPointer state, not by mutating Artifact content through a universal `SCRATCH -> VALIDATED -> CANONICAL` lifecycle.

Scratch/exploratory outputs may remain outside official Artifact registration until intentionally captured.

## 10. Provider and Adapter Classes

### Data providers

Genome-web API, PostgreSQL-backed stores, object/filesystem stores, external biological services.

### Workflow providers

Nextflow, Snakemake, Galaxy, and other mature executors.

### Tool providers

MCP, REST/RPC, CLI, Python/R, containers, TBtools, lab-developed scientific software such as EvoPM.

### Compute providers

Local process, SSH, Slurm, container/Apptainer, or future server-specific runners behind explicit capability contracts.

### Memory providers

PostgreSQL/pgvector, Qdrant, TiMEM-like providers, optional Graphiti/Neo4j-style graph engines when justified.

Provider choice remains replaceable behind BioHarness-owned semantics.

## 11. Genome-web Integration

Genome-web remains an existing biological asset:

- backend is the first Data Provider;
- existing scripts/Nextflow pilot remain external workflow/module providers;
- existing controlled API/MCP access can remain provider-facing interfaces;
- BioHarness must not copy Genome-web schema/logic solely to gain ownership.

The first P0 is defined in `docs/architecture/p0-genome-web-tf-vertical-slice.md` and is grounded in the audited current TF Nextflow integration.

## 12. Web Architecture

Web is a workbench/client only. It renders backend-defined projects, methods, Runs/Attempts, artifacts, validation, Findings, provenance, memory, decisions, and available actions.

It must not hard-code scientific workflow semantics or become the only way to execute/review an analysis.

## 13. Harness State and Sources of Truth

### Data Providers

Authoritative for source scientific datasets/domain records.

### Git

Authoritative for versioned code, reviewed workflow/module definitions, architecture docs, and configuration/policy definitions where appropriate.

### Harness State Store

Authoritative for BioHarness Project/Task/Context, RunSpec/RunAttempt/RunEvent, Artifact metadata, ValidationReports/profile evaluations, Findings, Decisions, CanonicalPointer history, ResearchMemory, and provenance/audit edges.

### Object/File Storage

Authoritative for immutable large artifact bytes where used.

### AI model context

Never authoritative by itself.

Physical deployment may initially use one PostgreSQL server with a logically separate BioHarness schema/database boundary.

## 14. Reuse over Reinvention

Reference patterns include AiiDA for persistent scientific process/provenance, Nextflow/nf-core and Snakemake for execution, OpenLineage for lineage vocabulary, RO-Crate for export/packaging, GA4GH data/execution abstractions, OPA-style policy separation, and TiMEM/Graphiti/RAPTOR-like memory/retrieval ideas.

These are evidence/pattern sources, not mandatory dependencies. Adoption notes live in the evidence/reference records.

## 15. What BioHarness Owns

BioHarness should own only semantics that bind research work together:

1. scientific task/feasibility contracts;
2. context compilation and action-scoped authorization;
3. Recipe/Module/Workflow registry contracts;
4. RunSpec/RunAttempt lifecycle and provenance;
5. Artifact/validation/Finding/Decision/canonical semantics;
6. evidence-backed ResearchMemory and promotion;
7. provider capability contracts;
8. feedback from validated experience into future context/configuration proposals.

Lower-level algorithms, workflow DAG execution, biological source databases, vector stores, graph engines, and Web presentation remain replaceable providers/clients.

## 16. V1 / P0 Focus

V1 proves one vertical loop before horizontal expansion:

```text
Data Provider resolution
  -> TaskSpec + ScientificAssessment
  -> ResolvedConfiguration + ContextSnapshot/RunSpec
  -> current launch authorization
  -> external WorkflowExecutor RunAttempt
  -> Artifact + typed Validation
  -> optional Finding/Decision
  -> scoped ResearchMemory
  -> observable effect on a later task
```

The selected first slice is the existing Genome-web TF Nextflow pilot. Production publication remains out of scope.

## 17. Explicit Non-Goals for V1

Do not initially:

- rebuild Genome-web models;
- rebuild Nextflow/Snakemake;
- implement custom graph/vector databases;
- clone TiMEM/FlowKit internals;
- build a universal biological ontology;
- require Web for operation;
- allow unrestricted agents to mutate shared/canonical state;
- automatically promote observations into Policy;
- require Kubernetes/microservices;
- claim generic remote execution/exactly-once semantics from the local P0;
- implement automatic Memory Pathway mining before simpler baselines are evaluated.

## 18. Architecture Acceptance Criteria

The design is ready for implementation planning when it supports, at minimum:

1. headless governed analysis;
2. provider data consumption without schema duplication;
3. adapter registration without unrelated core changes;
4. transparent Module scientific/runtime contracts;
5. exact/checkable input and historical provenance;
6. separation of TaskSpec, feasibility, authorization, configuration, RunSpec, RunAttempt, Artifact, validation, Finding, and canonical state;
7. explicit current authorization for protected actions;
8. typed/versioned validation and reproducibility expectations;
9. evidence-linked scoped memory with contradiction/supersession;
10. current applicability checks without rewriting historical Runs;
11. frontend replaceability;
12. one real vertical acceptance scenario with explicit `NOT_RUN` tests before runtime implementation.

## 19. Current State

```text
architecture = DESIGNED
runtime = NOT_IMPLEMENTED
acceptance_scenarios = NOT_RUN
```

Implementation planning should proceed in small vertical slices and must not reinterpret this design as runtime evidence.