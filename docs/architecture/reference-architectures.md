# BioHarness Reference Architectures and Reusable Components

Date: 2026-09-17
Purpose: Preserve external systems, repositories, papers, standards, and internal assets that BioHarness should reuse or learn from. This is a design reference catalog, not a dependency lockfile.

## 1. Adoption Principle

BioHarness should not claim novelty for infrastructure already solved elsewhere.

For every capability, prefer this order:

1. adopt a mature protocol/standard directly;
2. wrap a mature implementation behind an adapter;
3. adapt a proven architectural pattern;
4. build new infrastructure only when BioHarness-specific scientific semantics require it.

The main design question is therefore not "can we implement this?" but:

> Which layer is already mature, and which layer genuinely requires BioHarness-specific scientific semantics?

## 2. FlowKit

Repository: https://github.com/FrizzleFur/flowkit

### What it already solves well

FlowKit is an AI-native engineering workflow/governance framework. Relevant concepts include:

- structured flow/flow-deep execution stages;
- Iron Laws for TDD, verification, debugging, and review discipline;
- read-only versus state-changing task routing;
- multi-agent fan-out and integration;
- STATE.md for recoverable long-running work;
- Auto Handoff for long-context continuity;
- auto-skill for cross-session experience recall and accumulation;
- explicit experience/knowledge records with freshness/version considerations;
- loops/signals for recurring system maintenance and learning.

### What BioHarness should reuse

Do not clone FlowKit wholesale. Reuse its governance ideas:

- execution gates;
- evidence before completion claims;
- low-risk read path vs governed write path;
- staged plan -> execute -> verify lifecycle;
- explicit cross-session state;
- experience records with trigger/outcome evidence;
- policy-like "iron laws" that agents cannot silently bypass.

### What BioHarness adds

FlowKit's primary object is the software-engineering task. BioHarness applies analogous governance to scientific analysis where the key outputs are Runs, Artifacts, Decisions, Policies, and Research Memories.

BioHarness-specific semantics include scientific trust states, provenance, evidence-linked memory, workflow/parameter experiments, and memory-to-policy promotion.

## 3. TiMEM

Repository: https://github.com/TiMEM-AI/TiMEM
Paper/research direction: Temporal-Hierarchical Memory for long-horizon agents.

### What it already solves well

TiMEM organizes memory into explicit temporal levels:

- L1 fragment
- L2 session
- L3 daily
- L4 weekly
- L5 high-level/monthly

Its memory model includes:

- user identity;
- explicit time windows;
- creation/update timestamps;
- child/historical memory relationships;
- semantic retrieval scores;
- active/archived/deleted status;
- hierarchical consolidation and retrieval.

The project also points toward relation graphs, event graphs, thematic indexing, multi-hop reasoning, and multi-agent shared memory.

### What BioHarness should reuse

Potentially reuse or adapt:

- temporal hierarchy concepts;
- consolidation versus raw event separation;
- time-aware memory records;
- retrieval complexity routing;
- memory provider APIs/SDK patterns;
- Qdrant/vector-store integration patterns.

TiMEM may later be used as a Memory Provider rather than reimplemented.

### What BioHarness adds

BioHarness memory is not primarily conversational/persona memory. Its important semantic units are:

- Run
- Artifact
- Experiment
- Finding
- Failure lesson
- Paper
- Decision
- Policy
- Workflow/Method

BioHarness requires scientific evidence links and explicit promotion from memory/observation to Decision/Policy. It must also distinguish user, project, method, and laboratory scope.

## 4. Graphiti / Temporal Knowledge Graph Patterns

Repository: https://github.com/getzep/graphiti

### Relevant ideas

Graph-oriented memory systems are useful references for:

- temporal edges;
- valid/invalid intervals;
- supersession without destructive deletion;
- relationship-centric retrieval;
- multi-hop traversal.

### BioHarness use

Treat Graphiti as a candidate graph/memory provider, not as the BioHarness semantic model itself.

BioHarness first needs to define its own research edge vocabulary, for example:

- produced
- derived_from
- supports
- contradicts
- validates
- invalidates
- supersedes
- selected_over
- reproduced_by
- failed_under
- motivates
- constrains

A dedicated graph engine should be introduced only when real multi-hop workloads justify it. PostgreSQL plus explicit edge tables is acceptable for V1.

## 5. Nextflow and nf-core

Repositories:

- https://github.com/nextflow-io/nextflow
- https://github.com/nf-core

### What they solve

- reproducible workflow execution;
- process-level caching;
- portable compute backends;
- container/environment integration;
- standard community pipelines;
- versioned workflow definitions.

### BioHarness use

BioHarness should not implement another scientific workflow language.

Use Nextflow/nf-core as Workflow/Execution Providers where appropriate. BioHarness owns the surrounding scientific semantics:

- Recipe
- Policy/Context
- Run registration
- Artifact ingestion
- validation
- decision/promotion
- memory feedback.

Current Genome-web Nextflow work should be treated as an existing provider candidate.

## 6. Snakemake

Repository: https://github.com/snakemake/snakemake

### BioHarness use

Keep Snakemake as another Workflow Provider, especially for laboratory-specific research pipelines that already exist or fit Snakemake's model well.

Do not force all existing workflows into one engine merely for uniformity; normalize them through BioHarness contracts instead.

## 7. Galaxy

Repository: https://github.com/galaxyproject/galaxy
Website/docs: https://galaxyproject.org/

### Useful architectural lesson

Galaxy demonstrates that interactive analysis history can become a reusable workflow and that users can inspect tool/data lineage rather than operating an opaque black box.

### BioHarness use

Borrow the principle:

> exploratory analysis should have a promotion path into a reusable, governed workflow.

Galaxy itself may also become an external provider for suitable interactive workflows, rather than something BioHarness must reproduce.

## 8. OpenLineage

Repository: https://github.com/OpenLineage/OpenLineage
Specification/docs: https://openlineage.io/

### Useful ideas

OpenLineage provides a mature vocabulary centered on Job, Run, Dataset, and lineage events.

### BioHarness use

Reuse lineage/event concepts where compatible. Extend them with scientific semantics rather than inventing an unrelated provenance universe.

BioHarness-specific additions include:

- resolved ResearchContext;
- Policy snapshot;
- scientific validation state;
- Decision;
- Research Memory evidence links;
- Artifact trust state.

## 9. RO-Crate / Research Object

Specifications/docs: https://www.researchobject.org/ro-crate/

### Useful ideas

RO-Crate provides a portable packaging model for research objects, metadata, workflows, inputs, outputs, and related entities.

### BioHarness use

Use RO-Crate concepts for export/archive/exchange of reproducible analysis packages rather than inventing a proprietary portable bundle format.

## 10. GA4GH DRS / TRS / TES

GA4GH: https://www.ga4gh.org/

Relevant standards:

- DRS: Data Repository Service
- TRS: Tool Registry Service
- TES: Task Execution Service

### Useful ideas

These standards provide mature abstractions for:

- stable logical data references;
- tool/workflow discovery;
- task execution across heterogeneous backends.

### BioHarness use

BioHarness does not need to implement full standards compliance in V1, but should avoid designs that make future alignment impossible.

Use the patterns to keep Data Provider, Tool Registry, and Execution interfaces clean.

## 11. WorkflowHub and Dockstore

Repositories/sites:

- https://workflowhub.eu/
- https://github.com/dockstore/dockstore

### Useful ideas

- workflow metadata;
- versioning;
- discoverability;
- sharing/reuse;
- publication/identification of workflow releases.

### BioHarness use

Borrow registry metadata practices rather than inventing a completely bespoke workflow catalog.

BioHarness adds laboratory validation, project-scoped context, Decisions, and memory feedback.

## 12. KBase

Website: https://www.kbase.us/
GitHub organization: https://github.com/kbase

### Useful architectural lesson

KBase is a strong reference for typed scientific data objects, Apps, narratives/workspaces, provenance, and integrated computational research.

### BioHarness use

Borrow the idea that analysis operates over explicit research objects rather than anonymous files.

Do not copy its full application/data model; BioHarness is deliberately narrower and headless-first.

## 13. MCP

Specification/ecosystem: https://modelcontextprotocol.io/

### Useful ideas

MCP is an agent-facing protocol for tools/resources/prompts and is suitable as one client/provider boundary.

### BioHarness use

MCP should be an adapter surface, not the core architecture.

BioHarness should expose semantic scientific operations while allowing providers to be implemented by MCP, REST, RPC, CLI, or direct SDK integrations.

## 14. TBtools

Repository: https://github.com/CJ-Chen/TBtools-II

### Useful ideas

TBtools already provides mature biological operations, visualization, plugin concepts, and increasingly RPC/AI-oriented integration surfaces.

### BioHarness use

Do not rebuild TBtools functionality merely to obtain ownership.

Where suitable, expose TBtools capabilities through a Tool Provider/Adapter and attach BioHarness Module metadata, rationale, QC, provenance, and lifecycle semantics around it.

## 15. PlantMDCS

Project/paper reference: PlantMDCS, a modular toolkit for rapid deployment of plant multi-omics databases.

### Useful lesson

PlantMDCS demonstrates practical plant multi-omics presentation and analysis integration.

### BioHarness use

Borrow usability and data-presentation lessons, but keep BioHarness separate from a database-centric product architecture. BioHarness's core remains headless analysis/governance.

## 16. Internal Asset: Genome-web Backend

Repository: https://github.com/mumu-140/genome-web-backend

### Existing reusable capabilities

- mature plant/genome biological database;
- FastAPI API-first backend;
- gene/transcript/protein/annotation/homology/TF/structure/query capabilities;
- controlled MCP/API access patterns;
- data-processing pipeline with validation;
- Nextflow pilot with explicit inputs, isolated workspaces, candidate packages, caching, and validation;
- regression tests and production experience.

### BioHarness role

Treat Genome-web as the first Data Provider and a source of legacy Workflow/Tool Providers.

Do not migrate its full biological schema into BioHarness.

## 17. Internal Asset: Genome-web Frontend

Repository: https://github.com/mumu-140/genome-web-frontend

### Existing reusable capabilities

- React/Vite/TypeScript application;
- TanStack Query API boundary;
- scientific viewers/components;
- genome/gene/TF/structure/network/browser presentation experience.

### BioHarness role

Reuse professional presentation components where valuable. Refactor the shell/navigation so the Web can carry Projects, Methods, Runs, Results, and Agent interaction without making Web a required part of BioHarness.

## 18. Internal Research Software

Examples:

- EvoPM
- ForestConnectome
- DomFunc
- future structure-search or comparative-genomics methods

### BioHarness role

Keep independent scientific software in its own repository when it has independent research identity.

Register it as a Module/Workflow provider with:

- source revision;
- environment/container;
- typed inputs/outputs;
- parameter schema;
- rationale/reference;
- validation/QC;
- provenance hooks.

## 19. Research-Memory Design: Reuse vs Ownership

### Reuse directly

- vector database: pgvector/Qdrant/etc.
- graph database/engine if needed
- temporal memory implementation ideas from TiMEM
- graph temporal semantics from Graphiti-like systems
- embedding models
- LLM providers
- workflow engines

### BioHarness must own

- ResearchMemory semantic types;
- scientific scope rules (user/project/method/lab);
- evidence requirements;
- memory trust/lifecycle states;
- memory promotion to Decision/Policy;
- conflict/contradiction semantics;
- Context Compiler behavior;
- Policy resolution;
- links between memory and future execution.

These are the parts that differentiate BioHarness from a generic agent-memory layer.

## 20. Innovation Boundary

The following are **not** sufficient innovation claims on their own:

- vector search;
- memory graph;
- user/project memory;
- timestamps;
- forgetting/decay;
- temporal hierarchy;
- workflow DAG;
- MCP integration;
- provenance storage.

These are mature ingredients.

The stronger BioHarness research hypothesis is:

> Evidence-grounded research memories can be compiled with policy and project context to govern future scientific execution, while preserving full provenance and explicit promotion from observations to institutional knowledge.

Potential research components:

1. evidence-grounded scientific memory;
2. scoped research memory graph;
3. type-aware temporal lifecycle/forgetting;
4. Research Context Compiler;
5. memory -> Decision -> Policy promotion;
6. Policy/Execution -> evidence -> memory feedback;
7. evaluation against ordinary agents and generic memory systems.

This should remain framed as a hypothesis until experimentally benchmarked.

## 21. Candidate Evaluation Dimensions

If BioHarness later becomes a methods/research paper, candidate metrics include:

- published workflow reproduction success;
- repeated-error rate across sessions;
- policy/rule violation rate;
- stale-information misuse rate;
- provenance completeness;
- ability to identify the canonical/validated result;
- cross-session task completion;
- context token consumption;
- workflow reuse rate;
- parameter-decision traceability;
- recovery after contradictory evidence;
- accuracy of project-context retrieval.

## 22. Maintenance Rule for This Catalog

Whenever BioHarness adopts an external component or major idea, update this file with:

- source repository/paper/standard;
- exact capability being reused;
- whether it is a direct dependency, provider, adapter target, or conceptual reference;
- what BioHarness deliberately does **not** reimplement;
- version/date notes if behavior is version-sensitive.

This prevents the project from repeatedly rediscovering mature solutions or accidentally claiming external ideas as BioHarness-specific innovation.
