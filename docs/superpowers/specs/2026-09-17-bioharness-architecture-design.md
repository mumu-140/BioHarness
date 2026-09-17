# BioHarness Architecture Design

Date: 2026-09-17
Status: Draft v2 for review
Scope: Architecture only. This document defines the stable boundaries and core semantics of BioHarness; scientific tools, workflow engines, memory engines, model providers, data stores, and presentation components should be reused through adapters whenever possible.

## 1. Purpose

BioHarness is a **headless research analysis harness** for laboratory computational science.

It is not a genome database, not a web portal, not a new workflow language, and not a replacement for mature bioinformatics software. Its role is to make scientific analysis performed by humans and AI agents modular, governed, reproducible, inspectable, reusable, and cumulatively smarter over time.

BioHarness must remain usable without any frontend. The same research operation should be possible through API, CLI, SDK, MCP/agent clients, notebooks, or a Web workbench.

The central question BioHarness answers is:

> Given available scientific data and tools, how should this research task be executed, under which rules, with which context, what evidence was produced, and what should the laboratory remember for the next analysis?

## 2. System Boundary

The system is divided into three independent roles.

### 2.1 Data Providers

Data providers own scientific data and domain-specific query semantics.

Examples:

- Genome-web backend and PostgreSQL
- filesystem/object storage
- external biological databases
- future transcriptome/phenotype/variant stores
- project-specific data repositories

Genome-web remains the first mature biological Data Provider. BioHarness should query or reference it through stable provider interfaces rather than reimplement Gene, Transcript, Protein, Annotation, TF, Structure, Homology, and related domain tables.

### 2.2 BioHarness

BioHarness owns analysis and research governance:

- Research Context
- Policy
- Recipe
- Module Registry
- Workflow
- Experiment
- Run
- Artifact
- Validation
- Decision
- Research Memory
- Provenance
- Agent governance

### 2.3 Clients

Clients only operate and present BioHarness capabilities:

- CLI
- REST API
- SDK
- MCP/agent clients
- notebook integrations
- Web frontend

The Web frontend is optional and must not contain authoritative scientific workflow logic.

## 3. Architectural Position

BioHarness is a **Research Control Plane**.

Its architecture combines mature engineering patterns rather than inventing infrastructure already solved elsewhere:

- modular monolith for the first control-plane implementation
- ports/adapters for tools, data, workflow, compute, model, memory, and presentation providers
- immutable Run/Artifact records
- event/provenance lineage
- policy inheritance and resolved context snapshots
- registry-based capability discovery
- external workflow engines such as Nextflow/Snakemake
- MCP/API/RPC/CLI tool integration
- content-addressed reuse where scientific equivalence is defensible
- CQRS-lite read models for Web presentation

The architectural novelty is not the existence of a workflow engine, vector memory, graph store, or web UI. The distinctive layer is the scientific closed loop connecting **evidence-backed memory, policy, context compilation, execution, validation, and future behavior**.

## 4. Core Invariants

### I1. BioHarness does not reimplement mature scientific algorithms

Scientific software remains external whenever practical and is connected through registered providers/adapters.

### I2. BioHarness is headless

Removing the Web frontend must not prevent analysis, validation, result inspection, or memory/policy operation.

### I3. Data Providers remain authoritative for source scientific data

BioHarness stores stable references, provenance, and analysis state. It does not duplicate mature biological databases merely to achieve ownership.

### I4. Official computation is governed

Agents may explore in scratch contexts, but official runs, publication, promotion, shared workflow changes, and canonical decisions pass through BioHarness contracts.

### I5. Run and Artifact history is immutable by default

Re-analysis creates new Runs/Artifacts. Historical evidence is not overwritten.

### I6. Scientific status is explicit

Artifacts and memories have trust/lifecycle states. A file existing on disk does not make it an official result.

### I7. Memory is evidence-linked, not free-floating model recollection

Scientific memories must preserve source, time, scope, confidence, and where possible direct links to Runs, Artifacts, Papers, Decisions, or Policies.

### I8. Memory can influence future execution only through explicit context/policy resolution

Retrieval alone must not silently rewrite workflow behavior.

### I9. Frontend owns presentation, not research semantics

The UI renders state and invokes commands exposed by BioHarness. It must not become the source of truth for workflow definitions, policies, defaults, or scientific status.

## 5. High-Level Architecture

```text
                          USERS / AGENTS
                               |
        +----------------------+----------------------+
        |                      |                      |
       CLI                   MCP/SDK                Web
        |                      |                      |
        +----------------------+----------------------+
                               |
                               v
                    +------------------------+
                    |      BioHarness        |
                    |  Research Control Plane|
                    +------------------------+
                    | Context Compiler       |
                    | Policy Engine          |
                    | Recipe/Module Registry |
                    | Workflow/Experiment    |
                    | Run Manager            |
                    | Artifact/Validation    |
                    | Decision Engine        |
                    | Provenance             |
                    | Research Memory Plane  |
                    +----+-----------+-------+
                         |           |
              +----------+           +-------------------+
              |                                          |
              v                                          v
      +----------------+                         +------------------+
      | Data Providers |                         | Execution/Tools  |
      +----------------+                         +------------------+
      | Genome-web     |                         | Nextflow         |
      | PostgreSQL     |                         | Snakemake        |
      | files/S3       |                         | nf-core          |
      | external DBs   |                         | MCP/API/RPC/CLI  |
      +----------------+                         | TBtools          |
                                                 | R/Python         |
                                                 | lab tools        |
                                                 +------------------+
```

## 6. Core Domain Objects

BioHarness should keep a small stable core.

### 6.1 Project

The research scope in which analysis, rules, memories, decisions, and outputs are interpreted.

### 6.2 ResearchContext

A resolved, immutable snapshot of what a user/agent was allowed and expected to know for a specific governed action.

It can contain references to:

- project
- user/agent
- scientific data references
- canonical references from Data Providers
- applicable policies
- available workflows/modules
- runtime environments/models
- relevant validated memories
- prior failures/decisions

Every official Run should store a context snapshot ID/hash.

### 6.3 Policy

Normative rules. Examples:

- raw data are immutable
- official results require provenance
- a project excludes sample X23
- a workflow requires at least three replicates
- an agent cannot directly promote a canonical result

Policies are not memories; they prescribe behavior.

### 6.4 Recipe

Scientific intent and rationale.

A Recipe explains **what scientific method is being applied and why**, independent of one executable implementation.

It can originate from:

- a paper
- a laboratory SOP
- a validated historical analysis
- a newly designed method

### 6.5 Module

A typed reusable computational capability.

A Module contract describes:

- inputs/outputs
- software/provider/version
- runtime/environment
- parameters and explanations
- purpose/rationale
- references
- QC criteria
- interpretation guidance
- failure modes

The provider can be CLI, Python/R, container, REST, MCP, RPC, TBtools, or another external service.

### 6.6 Workflow

An executable composition of Modules. BioHarness records and governs workflows but should prefer mature workflow engines rather than create another general-purpose DSL.

### 6.7 Experiment

A structured comparison of Runs, software, workflows, parameters, environments, or models.

Experiment stores:

- baseline
- variables/search space
- candidates
- metrics
- constraints
- validation data
- outcome
- resulting Decision

### 6.8 Run

An immutable execution record containing exact inputs, workflow/module versions, parameters, resolved context/policy, runtime, model versions, compute backend, actor, and timestamps.

### 6.9 Artifact

An immutable output or registered scientific result.

Examples include tables, BAM/VCF, motif sets, trees, networks, structures, embeddings, reports, figures, and models.

### 6.10 Decision

A first-class explanation of why a scientific or operational choice was made.

Examples:

- selecting one parameter set
- excluding a sample
- accepting a reproduced workflow
- promoting one result over another
- changing a workflow default
- superseding a previous policy

### 6.11 ResearchMemory

A time-aware, scoped, evidence-backed memory derived from research activity.

Memory is not authoritative merely because it was generated by an LLM.

## 7. Research Context Compiler

The Context Compiler is a central BioHarness component.

A task should not be handled by simply retrieving the top-N vector memories and appending them to an LLM prompt.

Instead:

```text
User/Agent Request
      +
Project Scope
      +
Data Provider State
      +
Applicable Policies
      +
Workflow/Module Registry
      +
Relevant Memories
      +
Previous Decisions/Failures
      |
      v
Context Compiler
      |
      v
Resolved ResearchContext Snapshot
```

The compiled snapshot must distinguish:

- authoritative data
- mandatory policy
- validated memory
- provisional observation
- agent inference
- stale/superseded knowledge

This makes later audits possible: a Run can be evaluated against the exact context available at execution time.

## 8. Policy Engine

Policy resolution follows scoped inheritance, for example:

```text
Lab Policy
   -> User/Role Policy
      -> Project Policy
         -> Species/Data Policy (when relevant)
            -> Workflow Policy
               -> Run Override
```

The exact hierarchy may evolve, but resolution must be deterministic and frozen for governed Runs.

A policy change affects future Runs; it does not rewrite historical Run context.

Memory and Policy remain separate concepts:

- Memory says what has been observed/learned.
- Policy says what must/should happen.
- Decision explains why a memory or evidence set caused a policy/default to change.

## 9. Research Memory Plane

The memory subsystem is a logical plane, not necessarily one database product.

### 9.1 Memory scopes

At minimum:

- User Memory
- Project Memory
- Method/Workflow Memory
- Lab/Shared Memory

Scopes must remain explicit. A user's preference should not silently become laboratory policy, and a project-specific exception should not become a global default.

### 9.2 Memory types

Recommended semantic types:

- Observation
- Failure/Lesson
- Finding
- Preference
- Procedure Hint
- Software/Version Note
- Decision Summary
- Hypothesis
- Literature-derived Knowledge
- Validated Scientific Finding

Types drive lifecycle, confidence, and retrieval behavior.

### 9.3 Evidence grounding

A scientific memory should be able to reference one or more evidence objects:

```text
ResearchMemory
   -> Run
   -> Artifact
   -> Experiment
   -> Paper/Reference
   -> Decision
   -> Policy Event
```

Example:

```yaml
kind: FailureLesson
scope: project:poplar-rnaseq
statement: Parameter X consistently reduced unique mapping rate.
evidence:
  - run:183
  - run:187
  - artifact:qc-821
confidence: validated
```

### 9.4 Temporal model

Memory must carry explicit time semantics. At minimum:

- observed_at
- recorded_at
- valid_from
- valid_to (optional)
- updated_at
- superseded_at (optional)

A future implementation may adopt bi-temporal semantics more formally.

### 9.5 Memory lifecycle

Do not use a single generic exponential decay for all scientific memory.

Recommended lifecycle states:

```text
ACTIVE
STALE
SUPERSEDED
CONTRADICTED
ARCHIVED
RETRACTED
DELETED
```

Forgetting is type-aware:

- scratch observations decay quickly
- unvalidated agent inference decays quickly
- version-specific software hints become stale when versions change
- repeated failure lessons persist longer
- validated findings do not automatically decay because of age alone
- policies remain active until superseded/retracted

### 9.6 Memory promotion

Research experience becomes institutional knowledge through an explicit path:

```text
Observation
   -> Memory Candidate
   -> supporting evidence / Experiment
   -> Validated Memory
   -> Decision
   -> Workflow preset / Rule / Policy
```

This transition is one of the defining BioHarness behaviors. Retrieval should not directly mutate scientific defaults.

## 10. Research Memory Graph

The graph is not merely an entity relationship graph for conversational memory.

Its important edges describe the research process:

```text
Paper
  -> implemented_by -> Recipe/Workflow
Workflow
  -> executed_as -> Run
Run
  -> produced -> Artifact
Artifact
  -> supports -> Finding/Memory
Memory
  -> motivates -> Decision
Decision
  -> changes/promotes -> Policy/Preset
Policy
  -> constrains -> Future Run
```

Other useful edges include:

- derived_from
- contradicted_by
- supersedes
- validates
- invalidates
- compared_with
- selected_over
- reproduced_by
- failed_under

The first implementation does not require a dedicated graph database. PostgreSQL plus explicit edge tables and vector indexing are acceptable until real multi-hop workloads justify a graph engine.

## 11. Memory -> Policy -> Execution -> Evidence -> Memory Loop

This loop is the architectural center of BioHarness:

```text
Research Memory
      |
      v
Policy / Context
      |
      v
Recipe / Workflow
      |
      v
Run
      |
      v
Artifact / QC
      |
      v
Validation / Decision
      |
      +-------> Research Memory
```

The purpose is not to make an agent "remember more". It is to allow validated experience to change future scientific behavior while preserving evidence and auditability.

## 12. Analysis Modes for Agents and Humans

### Explore Mode

Free-form scratch work using shell/Python/R/notebooks when needed.

Outputs are SCRATCH and non-authoritative.

### Governed Analysis Mode

Runs registered Modules/Workflows under resolved Context and Policy. Produces immutable Run/Artifact records.

### Build Mode

Used to reproduce papers, develop new Modules/Workflows, compare implementations, or optimize parameters. Produces drafts/Experiments that require validation before promotion.

## 13. Scientific Lifecycle

### Analysis lifecycle

```text
Explore -> Reproduce/Build -> Validate -> Reuse -> Optimize -> Promote
```

### Artifact trust lifecycle

```text
SCRATCH
   -> EXPERIMENTAL
   -> CANDIDATE
   -> VALIDATED
   -> CANONICAL
```

### Execution lifecycle

```text
DRAFT -> QUEUED -> RUNNING -> COLLECTING -> VALIDATING -> SUCCEEDED
                                  |                         |
                                  +-> FAILED/CANCELLED <----+
```

Execution success and scientific validity are independent.

## 14. Module Contract: Transparency over Black Boxes

BioHarness must make analysis understandable to beginners and auditable by experts.

A Module contract should expose:

```yaml
id: transcriptomics.example
version: 1.0.0

purpose: ...
rationale: ...
references: [...]

inputs: {...}
outputs: {...}

software:
  provider: ...
  version: ...

environment: ...

parameters:
  parameter_a:
    default: ...
    explanation: ...
    constraints: ...

qc:
  metrics: [...]
  acceptance: ...

interpretation:
  expected_outputs: ...
  limitations: ...
  common_failures: ...
```

A user should be able to answer from the module definition:

- what is happening
- why this tool is used
- what data are consumed
- what parameters mean
- what result is produced
- how quality is checked
- what limitations apply

## 15. Recipe -> Workflow -> Run Separation

BioHarness separates scientific rationale from executable implementation.

### Recipe

Scientific purpose, assumptions, references, rationale, validation expectations.

### Workflow

Executable implementation/DAG, versioned and tied to providers.

### Run

One exact execution against concrete data under a concrete context.

This is especially important for paper reproduction: one paper-derived Recipe may have multiple implementation variants before a validated laboratory Workflow is selected.

## 16. External Providers and Adapters

BioHarness should define ports, not special cases.

### Data providers

- Genome-web API
- PostgreSQL-backed stores
- object/filesystem stores
- external biological services

### Workflow providers

- Nextflow
- Snakemake
- Galaxy where appropriate

### Tool providers

- MCP
- REST API
- RPC
- CLI
- Python/R
- containers
- TBtools
- lab-developed tools such as EvoPM

### Compute providers

- SSH
- Slurm
- containers/Apptainer
- server-specific runners

### Memory providers

- PostgreSQL/pgvector
- Qdrant
- TiMEM-like temporal memory provider
- future graph engines such as Graphiti/Neo4j when justified

Provider choice must remain replaceable behind BioHarness semantics.

## 17. Genome-web Integration

Current Genome-web is an existing asset, not something to rebuild inside BioHarness.

### Genome-web backend

Acts as the first biological Data Provider and continues to own genome-centric source data/query logic.

### Existing Genome-web pipelines

Existing scripts/Nextflow pilot can be wrapped and registered as legacy Workflow/Module providers. They should not be copied into BioHarness merely for ownership.

### Existing Genome-web MCP/API work

The current principle that AI uses controlled APIs rather than direct database access should be retained. Genome-specific MCP tools can remain a provider-facing capability layer beneath BioHarness.

## 18. Web Architecture

Web is a client/workbench only.

The current Genome-web professional biological components should be reused where useful, but the shell/navigation should evolve to expose both source data and BioHarness analysis state.

Recommended top-level concepts:

- Species / Data
- Projects
- Methods
- Runs
- Results
- Agent

The Web should obtain workflow steps, statuses, artifacts, provenance, available actions, and presentation hints from backend APIs rather than hard-code scientific workflows.

A scientific result page should prioritize interpretation and trust state, with raw files/provenance available as deeper views.

## 19. Harness State Store

BioHarness requires its own logical state even when scientific data live elsewhere.

Authoritative Harness state includes:

- Project
- Context Snapshot
- Policy
- Recipe
- Module/Workflow registry metadata
- Experiment
- Run
- Artifact metadata
- Validation
- Decision
- Research Memory
- Provenance edges

Physical deployment can initially use the same PostgreSQL server as other services, but Harness state should remain logically separable (for example, a dedicated schema/database boundary).

## 20. Source-of-Truth Rules

### Data Provider

Authoritative for source scientific datasets and domain-specific biological records.

### Git

Authoritative for versioned workflow/module definitions, code, reviewed policies/configuration, and architecture documentation where appropriate.

### Harness State Store

Authoritative for Runs, Artifacts, decisions, resolved contexts, memory state, validation, promotion, and indexes.

### Object/File Storage

Authoritative for immutable large artifacts and workflow outputs.

### AI memory/model context

Never an authoritative source by itself.

## 21. Reuse over Reinvention

BioHarness should directly borrow or adapt mature systems where they already solve the lower-level problem.

Examples include:

- FlowKit: execution discipline, staged planning/verification, read-vs-write governance, state handoff, experience loops
- TiMEM: temporal-hierarchical memory organization and consolidation concepts
- Nextflow/nf-core: workflow execution and standard pipelines
- Snakemake: research workflow execution
- OpenLineage: lineage event vocabulary/patterns
- RO-Crate: portable research object/export concepts
- GA4GH DRS/TRS/TES: data/tool/execution abstraction ideas
- Galaxy: transparent interactive history and workflow promotion
- WorkflowHub/Dockstore: workflow registry and metadata practices
- MCP: agent-facing tool/resource protocol
- TBtools: mature biological tooling and possible RPC/API provider
- Genome-web: internal biological Data Provider and reusable presentation components

Detailed references and adoption notes live in `docs/architecture/reference-architectures.md`.

## 22. What BioHarness Owns

BioHarness should own only the semantics that bind scientific work together:

1. Research Context compilation
2. Policy resolution
3. transparent Module/Recipe contracts
4. governed Run lifecycle
5. Artifact trust/promotion
6. Decision records
7. evidence-backed Research Memory semantics
8. Memory lifecycle and promotion
9. Memory <-> Policy feedback
10. Memory/Policy/Context -> future execution loop

Everything else should preferentially be reused behind adapters.

## 23. Distinctive Research Direction

The engineering product is useful even without claiming academic novelty.

If BioHarness is later developed into a research contribution, the strongest candidate is not "we added memory". It is the formalization and evaluation of:

**Evidence-grounded scientific memory + research context compilation + memory-to-policy feedback + governed execution.**

A meaningful benchmark would compare ordinary agents, semantic/vector-memory agents, temporal-memory agents, and BioHarness-style research memory on outcomes such as:

- paper workflow reproduction success
- repeated-error rate
- policy violation rate
- stale-knowledge misuse
- provenance completeness
- cross-session task success
- context/token cost
- workflow reuse rate
- result traceability

This remains a research hypothesis until empirically tested.

## 24. V1 Focus

V1 should not attempt to solve every analysis domain.

The architecture should first prove one complete vertical loop:

```text
Data Provider reference
    -> Context + Policy
    -> Recipe/Workflow
    -> governed Run
    -> Artifact/QC
    -> Decision
    -> Research Memory
    -> effect on a later Run
```

The V1 implementation should reuse existing Genome-web data and at least one existing workflow/provider rather than create synthetic infrastructure.

## 25. Explicit Non-Goals for V1

Do not initially:

- rebuild Genome-web database models
- rebuild Nextflow/Snakemake
- implement a custom graph database
- implement a custom vector database
- clone TiMEM memory internals
- clone FlowKit's complete coding workflow
- build a universal biological ontology
- make Web mandatory for operation
- allow unrestricted agents to write shared/canonical state
- automatically promote remembered observations into policy
- require Kubernetes/microservices

## 26. Architecture Acceptance Criteria

The architecture is successful when:

1. A user or agent can perform a complete governed analysis without Web.
2. Genome-web data can be consumed through a provider reference without duplicating its scientific schema.
3. A new tool can be registered via adapter/manifest without changing unrelated core logic.
4. A Module explains purpose, inputs, outputs, software, parameters, QC, and interpretation.
5. Every official Artifact is traceable to Run, context, policy, software/environment, and input data references.
6. Research memories carry scope, time, status, provenance/evidence, and confidence/trust metadata.
7. Superseded/contradicted knowledge can be retained without remaining active.
8. A validated memory can lead to a Decision and then an explicit workflow/policy change.
9. Historical Runs retain the exact context/policy snapshot used at execution time.
10. The frontend can be replaced without changing research semantics.

## 27. Immediate Documentation/Design Follow-up

Before implementation planning, review and lock:

- Context schema
- Policy precedence/conflict semantics
- Recipe/Module/Workflow contracts
- ResearchMemory schema and lifecycle
- Memory evidence/graph edge vocabulary
- Decision/promotion gates
- provider adapter contracts
- first V1 end-to-end scenario

Once this design is approved, implementation planning should proceed in small vertical slices rather than constructing all subsystems at once.
