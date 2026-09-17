# BioHarness Provider Composition and Research Memory Architecture

Date: 2026-09-17
Status: Design record for review
Scope: How BioHarness combines mature external systems while keeping scientific semantics in the BioHarness kernel.

Related documents:

- `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`
- `docs/architecture/reference-architectures.md`

## 1. Decision Summary

BioHarness will use a **Semantic Kernel + Provider/Adapter** architecture.

BioHarness must not become a source-code merger of FlowKit, TiMEM, Nextflow, Snakemake, Genome-web, TBtools, or other mature projects. Instead, BioHarness owns the scientific contracts and lifecycle semantics; mature projects provide capabilities behind stable interfaces.

The intended composition is:

```text
                         Clients
              Web / CLI / MCP / Agent / SDK
                           |
                           v
                +-----------------------+
                |      BioHarness       |
                |  Scientific Kernel    |
                |                       |
                | ResearchContext       |
                | Policy                |
                | Recipe                |
                | Module / Workflow     |
                | Experiment            |
                | Run / Artifact        |
                | Decision              |
                | ResearchMemory        |
                +-----------+-----------+
                            |
                            | Ports
          +-----------------+------------------+
          |                 |                  |
          v                 v                  v
     Data Providers     Execution          Memory
     Genome-web         Nextflow           TiMEM
     filesystem         Snakemake          pgvector/Qdrant
     external DB        CLI/API/MCP        Graphiti/graph DB later
          |                 |                  |
          +-----------------+------------------+
                            |
                            v
                       Harness Events
```

The key architectural principle is:

> BioHarness owns research semantics; providers own implementation capability.

## 2. What BioHarness Owns

BioHarness owns only the concepts whose meaning must remain stable even if every provider is replaced.

Core semantic objects:

- `ResearchContext`
- `Policy`
- `Recipe`
- `Module`
- `Workflow`
- `Experiment`
- `Run`
- `Artifact`
- `Decision`
- `ResearchMemory`

Core service contracts:

- `ContextCompiler`
- `PolicyEngine`
- `DataProvider`
- `ToolProvider`
- `WorkflowExecutor`
- `ComputeProvider`
- `MemoryProvider`
- `ArtifactStore`
- `Validator`

BioHarness Core must not import provider-specific domain semantics such as TiMEM memory levels, Nextflow work-directory structure, Genome-web ORM models, TBtools plugin internals, or FlowKit session files.

## 3. Mature Systems as Providers

### 3.1 Genome-web -> Data Provider

Genome-web remains the primary biological data source for currently curated species data.

It owns domain-specific data such as:

- species/assemblies;
- genes/transcripts/proteins;
- sequence retrieval;
- annotation;
- TF resources;
- structures;
- homology;
- existing biological read models.

BioHarness should reference Genome-web resources through stable logical references rather than duplicate the full biological database.

Example:

```text
genome-web://species/Paxg_84K_T2T
genome-web://proteome/Paxg_84K_T2T
genome-web://gene/PAxG01Gg0010600
```

### 3.2 Nextflow / Snakemake -> Execution Providers

BioHarness does not create a new DAG engine.

A BioHarness `Workflow` resolves into a `RunSpec`; the selected `WorkflowExecutor` submits the scientific computation to Nextflow, Snakemake, CLI, API, MCP, or another execution backend.

BioHarness owns:

- exact input references;
- workflow/module revision;
- normalized parameters;
- resolved context/policy snapshot;
- execution request;
- Run state;
- result registration;
- validation;
- provenance.

The external engine owns the actual task graph and process execution.

### 3.3 FlowKit -> Agent Governance Reference / Provider

FlowKit should be reused primarily for governance concepts, not copied into BioHarness Core.

Relevant reusable concepts:

- Iron Laws / non-bypassable execution rules;
- plan -> execute -> verify lifecycle;
- read-only fast path versus governed state-changing path;
- state/handoff for long-running agent tasks;
- evidence before completion claims;
- experience accumulation;
- recurring loops and signals.

BioHarness maps these into scientific semantics:

```text
FlowKit concept                 BioHarness interpretation
----------------------------------------------------------------
Iron Laws                      Hard Policy
read/write risk routing        Risk Class / Execution Gate
Plan -> Execute -> Verify      Run lifecycle gates
STATE.md                       Agent Task State
Auto Handoff                   Session continuity
Auto-skill                     Memory-candidate capture
Experience records             Evidence-linked ResearchMemory
Loops / signals                Evaluation / maintenance loops
```

Important boundary:

`Agent Task State` is not `ResearchMemory`.

Task state answers "where is this agent task now?" Research memory answers "what has this laboratory learned from scientific work?"

Reference repository:

- https://github.com/FrizzleFur/flowkit

### 3.4 TiMEM -> Memory Provider

TiMEM is a strong candidate for reusable temporal-memory infrastructure.

BioHarness should not reproduce TiMEM's generic capabilities unless provider integration proves insufficient.

Potentially reusable TiMEM capabilities:

- temporal hierarchy and consolidation;
- time-aware memory records;
- session/history relationships;
- semantic retrieval;
- complexity-aware recall;
- vector-store integration;
- long-horizon memory maintenance.

BioHarness does **not** delegate scientific authority to TiMEM. TiMEM-generated or consolidated items enter BioHarness as memory candidates or derived memories, never as canonical facts or policies by default.

Reference repository:

- https://github.com/TiMEM-AI/TiMEM

### 3.5 Graphiti / Graph Database -> Optional Graph Provider

A graph engine is an implementation choice, not a core requirement.

The first version should prefer PostgreSQL tables for memory/provenance nodes and edges. A Graphiti/Neo4j-style provider is justified only when multi-hop graph retrieval becomes a demonstrated bottleneck or core use case.

Reference:

- https://github.com/getzep/graphiti

## 4. Three Layers of Truth

BioHarness must strictly separate three information layers.

### 4.1 Authoritative State

Examples:

- exact Run status;
- workflow/module revision;
- immutable Artifact identity;
- explicit Project Decision;
- current Policy version;
- canonical pointer;
- Git revision;
- recorded validation outcome.

Authoritative state lives in explicit storage such as PostgreSQL, Git, registry manifests, and immutable artifact storage.

### 4.2 Derived Research Memory

Examples:

- a parameter repeatedly performs poorly for a class of datasets;
- a workflow has a known failure mode;
- a project usually requires a particular pre-processing step;
- a method comparison consistently favors one preset under specified conditions.

Research memory must link back to evidence and authority sources. It is derived knowledge, not the original source of truth.

### 4.3 Ephemeral Agent Context

This is the task-specific information loaded into a model context window for a particular operation.

It may contain selected policies, memories, project facts, data references, workflow descriptions, and prior decisions, but it is disposable and non-authoritative.

Architecture invariant:

> Authoritative state, derived memory, and ephemeral model context must never be conflated.

## 5. Research Memory Scope

Research memory is scoped rather than stored in one undifferentiated vector collection.

### Lab Memory

Long-lived laboratory practices and validated shared knowledge.

Examples:

- validated operational lessons;
- lab-wide method caveats;
- shared infrastructure knowledge.

### Method / Workflow Memory

Knowledge specific to a reusable method or workflow.

Examples:

- software-version caveats;
- validated parameter behavior;
- reproduction notes;
- failure patterns;
- compatible environments.

### Project Memory

Contextual knowledge that is true or useful within a particular research project.

Examples:

- why a sample was excluded;
- why a reference version was chosen;
- failed hypotheses;
- project-specific analysis decisions;
- current unresolved questions.

### User Memory

User-specific operating preferences and skill/context information.

Examples:

- preferred explanation depth;
- familiarity with a tool;
- recurring workflow preferences;
- user-specific non-scientific operating conventions.

User memory must not silently alter scientific facts or hard policy.

## 6. Evidence-Grounded Research Memory Contract

Research memory should use a BioHarness-defined semantic contract independent of the underlying memory engine.

Illustrative shape:

```yaml
id: mem-8392
scope:
  type: project
  id: poplar-rnaseq
kind: failure_lesson
claim: STAR parameter X performs poorly for this dataset class
evidence:
  - run:183
  - run:187
  - artifact:qc-882
valid_time:
  from: 2026-08-01T00:00:00Z
  to: null
observed_at: 2026-08-14T09:11:00Z
recorded_at: 2026-09-17T11:00:00Z
status: active
authority:
  level: evidence_supported
confidence: 0.92
supersedes: null
```

Important fields:

- scope;
- memory kind;
- claim;
- evidence links;
- temporal validity;
- recording time;
- confidence/authority;
- lifecycle state;
- supersession/contradiction relationships.

The provider may add implementation metadata, but cannot redefine these semantics.

## 7. Memory Lifecycle Instead of Simple Forgetting

Research knowledge should not decay merely because it is old.

A recent unvalidated agent inference may be less trustworthy than an old validated result.

Therefore BioHarness uses type-aware memory lifecycle rather than a single recency-decay function.

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

Examples:

- scratch observation: short-lived;
- unvalidated inference: relatively fast stale transition;
- software-version tip: becomes stale when the subject version changes;
- failed-run lesson: retained for a long period;
- validated scientific finding: no automatic time decay by default;
- canonical Decision: retained until explicitly superseded;
- Policy: invalidated only by policy lifecycle, not memory decay.

Deletion is exceptional. Supersession and contradiction are preferred because scientific history must remain inspectable.

## 8. Temporal Semantics

A single `created_at` timestamp is insufficient.

Research memory should preserve at least:

- `valid_from` / `valid_to`: when the claim is considered applicable;
- `observed_at`: when supporting evidence was observed;
- `recorded_at`: when the system recorded the memory;
- `superseded_at`: when it was replaced, if applicable.

This allows the system to distinguish:

- when something was true;
- when the laboratory learned it;
- when the system stored it;
- when a newer conclusion replaced it.

## 9. Context Compiler

`ContextCompiler` is a BioHarness-owned core component.

Its job is not merely top-k vector retrieval. It constructs a reproducible scientific context from authoritative sources, policy, memory, providers, and actor/task state.

Inputs may include:

- actor/user;
- project;
- task;
- selected data;
- target workflow/method;
- current policies;
- available tools/environments/models;
- prior decisions;
- relevant research memory.

Output:

```yaml
context_snapshot: ctx-2281
project: evopm
data:
  proteins: genome-web://proteome/Paxg_84K_T2T
policies:
  - lab.raw-data-readonly@v2
  - project.evopm@v5
memories:
  - mem-312
  - mem-519
decisions:
  - dec-72
workflow: evopm.mine@2.3
capabilities:
  - meme
  - nextflow
  - slurm
actor: user-12
created_at: 2026-09-17T12:00:00Z
```

The produced `ContextSnapshot` is immutable and receives a content hash. Every governed `Run` references the exact snapshot used to plan/execute it.

This supports later reconstruction of:

> What did the agent or researcher know, and which rules were active, when this Run was created?

## 10. Context Precedence

Semantic retrieval score must never override authority.

Default precedence:

```text
Hard Policy
    > Explicit Project Decision
    > Canonical / Validated Fact
    > Validated Research Memory
    > Evidence-supported Memory
    > User Preference
    > Unvalidated Observation
    > Agent Inference
```

If a high-similarity memory conflicts with a newer explicit Project Decision, the Decision wins.

The Context Compiler must record conflicts rather than silently blend contradictory claims.

## 11. Policy Engine

The Policy Engine evaluates actions using resolved policy and risk class.

Policy inheritance may include:

```text
Lab
 -> Project
    -> Method/Workflow
       -> Run override
```

Scientific data providers may additionally contribute resource constraints or validity metadata, but provider metadata is not itself a BioHarness policy until explicitly mapped.

Policy outcomes should use a small stable vocabulary such as:

```text
ALLOW
ALLOW_WITH_WARNING
REQUIRE_APPROVAL
DENY
```

Examples:

- gene lookup -> `ALLOW`;
- temporary PCA in scratch -> `ALLOW`;
- 500 CPU-hour workflow -> `REQUIRE_APPROVAL` depending on lab policy;
- direct canonical overwrite -> `DENY`;
- canonical promotion -> `REQUIRE_APPROVAL`.

## 12. Memory Promotion and Scientific Governance

A key invariant is:

> Research memory can influence investigation, but Memory must never directly become Policy.

Required promotion chain:

```text
Observation / Memory Candidate
          |
          v
        Evidence
          |
          v
 Experiment / Validation when needed
          |
          v
        Decision
          |
          v
 Policy / Workflow preset / Canonical recommendation
```

This prevents an LLM-generated summary from silently becoming a laboratory rule.

Examples:

- repeated poor QC creates a `MemoryCandidate`;
- an explicit A/B experiment compares parameter sets;
- validation supports one configuration;
- a human or governed process records the Decision;
- the selected preset may be promoted to a method default;
- only an explicit policy action changes hard laboratory policy.

## 13. Research Feedback Loop

The main learning loop is:

```text
Research Context
      |
      v
    Policy
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
 Validation
      |
      v
  Decision
      |
      v
Research Memory
      |
      +-----------------------> future Context
```

The defining BioHarness behavior is not just memory retrieval; it is evidence-backed feedback from execution into future governed analysis.

## 14. Research Memory Graph

The memory graph should emerge from real research lifecycle edges rather than from an independent knowledge-graph project.

Typical path:

```text
Paper
  -> supports -> Recipe
Recipe
  -> implemented_by -> Workflow
Workflow
  -> executed_as -> Run
Run
  -> produced -> Artifact
Artifact
  -> evidence_for -> Finding
Finding
  -> summarized_as -> ResearchMemory
ResearchMemory
  -> supports -> Decision
Decision
  -> updates -> Policy / Preset
Policy
  -> constrains -> Future Run
```

Other useful edges:

```text
ParameterSet -> tested_by -> Run
ParameterSet -> compared_with -> ParameterSet
Decision -> selected -> ParameterSet
Memory -> supersedes -> Memory
Memory -> contradicts -> Memory
Memory -> derived_from -> Artifact
```

Initial implementation should be possible with relational node/edge tables. Dedicated graph infrastructure is deferred until justified by query workload.

## 15. Event Model

BioHarness components communicate conceptually through domain events even if the first implementation uses a modular-monolith transaction/outbox model.

Examples:

```text
RunPlanned
RunStarted
RunFinished
RunFailed
ArtifactRegistered
ArtifactValidated
ArtifactPromoted
DecisionRecorded
PolicyChanged
MemoryCandidateCreated
MemoryValidated
MemorySuperseded
```

Memory providers subscribe to relevant events and may produce derived memory candidates. Execution providers consume RunSpec-like commands. Data providers resolve logical data references.

The first version does not require Kafka or a distributed event bus.

## 16. Storage Composition

Recommended first-stage logical storage:

### BioHarness PostgreSQL

Stores:

- projects;
- policies;
- recipes;
- modules/workflows metadata;
- experiments;
- runs;
- artifact metadata;
- decisions;
- context snapshots;
- research-memory metadata;
- provenance/memory graph edges;
- audit events.

### Semantic index

Start with either:

- `pgvector`, if operational simplicity is more important;
- Qdrant, if TiMEM integration or retrieval workload makes it preferable.

### Large artifacts

Use object storage or managed filesystem references rather than relational blobs.

### Biological source data

Remain in Genome-web, external databases, project stores, or other Data Providers.

### Graph database

Deferred. Add Graphiti/Neo4j adapter only after demonstrated multi-hop graph requirements.

## 17. Headless Operation

BioHarness must work without the Web frontend.

Equivalent operations should be possible through:

- REST API;
- CLI;
- Python/SDK;
- MCP/agent tools;
- notebook integrations.

The Web application is a presentation and interaction surface only.

It may render:

- workflow DAGs;
- Run progress;
- QC;
- Result summaries;
- provenance;
- memory/decision lineage;
- comparison views.

It must not become the authoritative location of scientific logic.

## 18. Architecture Invariants Added by This Decision

The following invariants should be added to the BioHarness architecture constitution.

1. **Provider independence**: BioHarness Core depends on scientific contracts, not specific FlowKit/TiMEM/Nextflow/Genome-web implementation classes.
2. **Three-layer separation**: authoritative state, derived research memory, and ephemeral agent context are distinct.
3. **Context reproducibility**: governed Runs reference an immutable `ContextSnapshot`.
4. **Authority beats similarity**: semantic retrieval score cannot override Policy, explicit Decision, or canonical validated facts.
5. **Memory is evidence-linked**: actionable research memory must preserve provenance/evidence references.
6. **Memory cannot directly become Policy**: promotion requires explicit evidence/Decision/governance.
7. **Task state is not scientific memory**: agent session continuity and research knowledge are modeled separately.
8. **Graph infrastructure is replaceable**: the graph semantic model belongs to BioHarness; graph databases are adapters.
9. **Execution infrastructure is replaceable**: scientific workflows use external execution providers; BioHarness does not create a general DAG engine.
10. **Web independence**: the analysis/control plane remains fully functional without a frontend.

## 19. Reusable Repositories and Knowledge

Keep these references available during design and implementation.

### Agent governance

- FlowKit: https://github.com/FrizzleFur/flowkit
  - Iron Laws
  - staged execution/verification
  - read/write routing
  - STATE / handoff
  - auto-skill / experience loop
  - recurring loops

### Temporal memory

- TiMEM: https://github.com/TiMEM-AI/TiMEM
  - temporal-hierarchical memory
  - consolidation
  - retrieval
  - time-window semantics
  - vector-store integration

### Temporal / graph memory

- Graphiti: https://github.com/getzep/graphiti
  - temporal graph relationships
  - validity/supersession patterns
  - multi-hop graph retrieval ideas

### Scientific workflow execution

- Nextflow: https://github.com/nextflow-io/nextflow
- nf-core: https://github.com/nf-core
- Snakemake: https://github.com/snakemake/snakemake

### Existing laboratory data/application provider

- Genome-web backend: https://github.com/mumu-140/genome-web-backend
- Genome-web frontend: https://github.com/mumu-140/genome-web-frontend

### Other references already catalogued

See `docs/architecture/reference-architectures.md` for OpenLineage, RO-Crate, GA4GH DRS/TRS/TES, WorkflowHub/Dockstore, KBase, MCP, TBtools, PlantMDCS, and laboratory research software such as EvoPM/ForestConnectome/DomFunc.

## 20. Immediate Design Consequence

Before implementation, the next contracts to stabilize are:

1. `ResearchContext` / immutable `ContextSnapshot`;
2. `Policy` and policy evaluation output;
3. `ResearchMemory` and memory lifecycle/evidence schema;
4. provider interfaces for Data, Memory, and Workflow Execution.

Implementation should not begin by integrating TiMEM or Nextflow directly. The BioHarness contracts come first, followed by provider adapters.
