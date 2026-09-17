# BioHarness Hierarchical Associative Memory Architecture

Date: 2026-09-17
Status: Design record for review
Scope: Brain-inspired research memory retrieval, task working memory, pathway consolidation, and controlled plasticity. This document defines BioHarness-specific semantics; storage engines and retrieval infrastructure should be reused from mature projects whenever possible.

Related documents:

- `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`
- `docs/architecture/provider-composition-and-research-memory.md`
- `docs/architecture/reference-architectures.md`

## 1. Design Thesis

BioHarness should not model research memory as a flat vector store queried by top-k similarity. The target design is a **brain-inspired hierarchical associative memory system**:

1. persistent memory is primarily an indexable hierarchy/graph rather than a prompt dump;
2. a new task activates relevant high-level memory nodes;
3. those nodes recursively expand into lower-level memories, data, methods, rules, evidence, and capabilities;
4. the activated material forms a temporary **TaskMemoryGraph** for the current task;
5. repeated, useful, validated subgraphs can be consolidated into reusable **Memory Pathways**;
6. stable pathways may be partially frozen while selected slots remain plastic and can adapt to project, user, dataset, software version, or task requirements;
7. execution outcomes feed back into memory through evidence-backed consolidation.

This is inspired by long-term memory -> associative activation -> working memory -> action -> consolidation, but BioHarness does not claim to reproduce biological neural mechanisms.

## 2. Persistent Memory Is an Indexed Research Graph

The persistent memory layer stores small, typed, addressable research memory units and their relationships.

A memory node may carry:

- semantic embedding/vector index;
- typed tags and research domain labels;
- scope: lab, method, project, user;
- hierarchy level;
- typed graph edges;
- valid/recorded time metadata;
- trust/evidence state;
- child indexes or expansion targets;
- software/data/version constraints;
- provenance links to Run, Artifact, Decision, Paper, Policy, or external providers.

Vectors are an important retrieval mechanism but not the memory model itself.

The initial retrieval system should be hybrid:

```text
semantic/vector similarity
+ keyword/index search
+ typed hierarchy
+ graph relations
+ scope filtering
+ time/version filtering
+ evidence/trust weighting
```

## 3. Research Abstraction Hierarchy

Unlike conversational memory systems whose hierarchy is mainly temporal, BioHarness should organize persistent research memory primarily by **scientific abstraction**.

Illustrative levels:

```text
L0 Research Domain
   Transcriptomics / Genomics / Evolution / Structure / Statistics

L1 Research Capability
   RNA-seq / Differential Expression / GO Enrichment / Gene Search

L2 Method / Recipe
   DESeq2 / edgeR / clusterProfiler / nf-core-rnaseq / lab recipes

L3 Concrete Context
   project decision / dataset / parameter preset / workflow revision

L4 Evidence
   Run / Artifact / QC / Paper / failure / benchmark / logs
```

Time is orthogonal metadata on every node, not the primary hierarchy axis.

## 4. Task Decomposition Before Retrieval

A task should first be decomposed into scientific subproblems before memory retrieval.

Example request:

> For this gene, inspect related differential expression and perform GO enrichment.

Possible decomposition:

```text
Task
├── Gene/Data branch
│   ├── species
│   ├── identifier resolution
│   ├── Genome-web lookup
│   └── annotation/expression availability
├── RNA-seq branch
│   ├── project dataset
│   ├── experimental contrast
│   ├── differential-expression method
│   ├── validated parameter preset
│   └── previous decisions/failures
└── GO branch
    ├── gene-ID namespace
    ├── annotation source
    ├── background universe
    ├── enrichment method
    └── multiple-testing policy
```

The system is therefore retrieving a **research chain**, not a single memory fragment.

## 5. Coarse-to-Fine Associative Retrieval

Retrieval proceeds recursively from abstract to concrete.

```text
Task
  ↓
Task Decomposer
  ↓
Seed high-level memories
  ↓
Activate related nodes
  ↓
Expand high-value children/edges
  ↓
Reach actionable leaves
  ↓
Build TaskMemoryGraph
```

Two operations must remain distinct:

### RECALL

Question: which memory nodes are relevant to this task?

Signals may include semantic similarity, keywords, scope, task role, usage history, graph proximity, current project, current user, and software/data version.

### EXPAND

Question: what does this activated node lead to concretely?

Expansion follows typed child relations, provider lookups, validated decisions, workflow/module links, data links, and evidence edges.

A retrieval node is **actionable** only when BioHarness can determine the relevant capability, input, version, parameter/preset, applicable policy, and supporting evidence or identify an explicit unresolved gap.

## 6. TaskMemoryGraph: Temporary Working Memory

`TaskMemoryGraph` is a task-scoped, temporary working-memory structure constructed from persistent memory and authoritative providers.

It is not the permanent knowledge graph and should not automatically mutate persistent knowledge.

Example:

```text
                       Task
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
        Gene          RNA-seq          GO
          |             |              |
   Genome-web      Project data    GO annotation
          |             |              |
       Gene X       Count matrix     ID mapping
                        |              |
                     DESeq2            |
                        |              |
                      DEGs ------------+
                        |
                        v
                  GO enrichment
                        |
                        v
                      Result
```

The graph may also attach Policy, Decision, ResearchMemory, Workflow, Module, Run, Artifact, Paper, QC, and capability-provider nodes.

The lifecycle is:

```text
Persistent Memory
      ↓ recall/expand
TaskMemoryGraph
      ↓ resolve
ContextSnapshot
      ↓
Plan / Workflow / Execution
      ↓
Run / Artifact / Evidence
      ↓
Consolidation
      └──────→ Persistent Memory
```

## 7. Context Compiler Comes After Memory Activation

The Context Compiler is not the primary search engine.

Correct order:

```text
Task Decomposer
      ↓
Hierarchical Memory Index
      ↓
Associative Retriever
      ↓
TaskMemoryGraph
      ↓
Context Compiler
      ↓
Immutable ContextSnapshot
```

The Context Compiler resolves conflicts, applies authoritative precedence, suppresses stale/inapplicable memories, identifies unresolved blockers, and freezes the final execution/scientific context for the Run.

## 8. Memory Pathways: Consolidated Procedural Research Memory

Rebuilding every TaskMemoryGraph recursively from zero is unnecessary when the same scientific reasoning chain is repeatedly useful.

BioHarness therefore introduces **Memory Pathway**:

> A reusable, evidence-backed template describing which research concepts, data providers, methods, rules, and memories should normally be activated together for a class of tasks.

Example:

```text
gene
  → expression dataset
  → experimental contrast
  → differential analysis
  → DEG set
  → gene-ID mapping
  → GO annotation
  → enrichment
```

A Memory Pathway is not a Workflow.

- Workflow answers: **how does computation execute?**
- Memory Pathway answers: **what should the system recall and connect when reasoning about this scientific task?**

A pathway may select/configure one or more workflows, but it must remain logically independent from the execution engine.

## 9. Pathway Mining and Promotion

A pathway can be authored manually or proposed automatically.

Automatic consolidation must not be based on frequency alone. Candidate pathways should consider:

- reuse frequency;
- successful execution rate;
- validation/evidence strength;
- structural similarity across TaskMemoryGraphs;
- reuse across projects/tasks;
- stability over time;
- absence of strong contradictions;
- version/scope compatibility.

Promotion routes:

```text
Repeated TaskMemoryGraphs
        ↓
Pathway Miner
        ↓
Candidate Pathway
        ↓
validation / human review when required
        ↓
Shared Memory Pathway
```

or:

```text
Human-authored Pathway
        ↓
validation
        ↓
Shared Memory Pathway
```

High frequency without good outcomes must never strengthen a scientific pathway merely because it is common.

## 10. Module/Workflow Memory Packs

Modules, Recipes, and Workflows may expose an optional **Memory Pack** that acts as plugin-like procedural memory.

Illustrative contents:

```text
Module: DESeq2
├── executable contract
├── inputs/outputs
├── parameters
└── memory_pack
    ├── when_to_use
    ├── when_not_to_use
    ├── upstream expectations
    ├── downstream associations
    ├── parameter rationale
    ├── known pitfalls
    ├── validated presets
    ├── previous validated runs
    ├── relevant decisions
    └── interpretation guidance
```

Activating a module therefore activates not only executable capability metadata, but also nearby scientific memory useful for planning and interpretation.

Memory Packs must remain replaceable/extendable and must not embed authoritative policy unless that policy is separately referenced by ID/version.

## 11. Controlled Plasticity

Memory structures should support different degrees of plasticity.

Recommended states:

```text
LOCKED
ADAPTIVE
EXPLORATORY
```

### LOCKED

Human-approved hard policy or stable institutional knowledge. Agents cannot mutate it automatically.

### ADAPTIVE

Validated reusable pathways or memory structures whose core is stable but selected slots may adapt.

### EXPLORATORY

New associations, tools, parameters, or candidate pathways that may change freely inside an exploratory scope.

Typical lifecycle:

```text
EXPLORATORY
   ↓ repeated evidence / validation
ADAPTIVE
   ↓ strong validation / explicit promotion
LOCKED or STABLE
```

Contradiction or environmental change may trigger:

```text
STABLE
  ↓ contradiction / version change
THAWED
  ↓ re-evaluation
ADAPTIVE
```

"Thawing" must be explicit and auditable for shared pathways.

## 12. Frozen Core + Adaptive Slots

A reusable pathway should not be treated as completely immutable or completely free-form.

Example stable core:

```text
counts
  → differential analysis
  → DEGs
  → gene-ID mapping
  → enrichment
```

Adaptive slots may include:

- DESeq2 vs edgeR;
- species/reference assembly;
- experimental contrast;
- batch variable;
- FDR threshold/preset;
- GO annotation source;
- background universe;
- visualization/explanation depth.

This allows pathway reuse without overfitting the entire system to one project or species.

## 13. Shared Base + Scope Overlays

Personalization must not silently mutate shared laboratory knowledge.

Use composition:

```text
Shared Base Pathway
       +
Project Overlay
       +
User Overlay
       +
Current Task
       ↓
TaskMemoryGraph
```

Project overlays may specify project-specific datasets, reference versions, exclusions, validated parameter decisions, or contrasts.

User overlays may alter explanation depth, preferred representations, familiar tools, or teaching hints, but must not override scientific truth or hard policy.

## 14. Weighted Associative Edges

Memory edges may carry an associative strength, but this weight must remain interpretable and evidence-linked.

Conceptually:

```text
edge_strength =
    successful_coactivation
  + validation_strength
  + reuse_frequency
  + scope_relevance
  - contradiction_penalty
  - staleness_penalty
  - failure_penalty
```

This is a Hebbian-like engineering analogy: associations that repeatedly co-activate in successful, validated research tasks can become easier to retrieve.

However, BioHarness must preserve provenance for why an edge strengthened or weakened. Edge weights must never replace explicit Policy/Decision precedence.

## 15. Fast Cognition and Slow Consolidation

The architecture intentionally separates a fast task loop from a slower learning loop.

### Fast loop

```text
Task
 ↓
activate high-level memory/pathway
 ↓
existing pathway?
 ├── yes: instantiate + local expansion
 └── no: recursive associative retrieval
 ↓
TaskMemoryGraph
 ↓
ContextSnapshot
 ↓
Execution
```

### Slow loop

```text
TaskMemoryGraph
      ↓
Run outcome
      ↓
Validation / Evidence
      ↓
usage statistics
      ↓
Consolidation Engine
      ↓
strengthen/weaken edges
      ↓
propose/update pathway
      ↓
validated Persistent Memory
```

This allows BioHarness to become more efficient and more consistent with use without turning every new observation into an automatic rule.

## 16. Safety and Governance Invariants

The memory architecture must preserve the following invariants:

1. Memory is derived knowledge; it is not automatically authoritative state.
2. A Memory Pathway cannot override Hard Policy or explicit Decision precedence.
3. Memory cannot directly promote itself into Policy. Promotion follows Evidence -> Validation/Experiment -> Decision -> Policy/Preset.
4. User personalization cannot modify shared scientific truth.
5. Shared-pathway thawing/promotion must be auditable.
6. TaskMemoryGraph is temporary by default; only evidence-backed material is consolidated.
7. Retrieval weights never substitute for provenance or scientific validation.
8. Persistent memory must support superseded, contradicted, stale, archived, and retracted states rather than naive deletion.

## 17. Storage and Provider Strategy

Do not build a new vector database, graph database, or general-purpose memory engine unless required by BioHarness-specific semantics.

Initial implementation can use mature infrastructure such as:

- PostgreSQL for authoritative metadata, node/edge metadata, pathway definitions, decisions, and audit history;
- pgvector or Qdrant for semantic indexes;
- TiMEM concepts/providers for temporal consolidation and retrieval;
- Graphiti/Neo4j only when graph-scale or temporal multi-hop requirements justify them;
- Genome-web and other domain stores as authoritative Data Providers;
- Nextflow/Snakemake as execution providers.

The BioHarness-owned part is the research semantics and lifecycle around TaskMemoryGraph, MemoryPathway, MemoryPack, scope overlays, evidence, promotion, and plasticity.

## 18. Engineering Analogy

The intended correspondence is:

```text
Long-term memory       -> Persistent Research Memory
Associative activation -> Hybrid Recall / Graph Expansion
Working memory         -> TaskMemoryGraph
Synaptic connection    -> Typed Memory Edge
Connection strength    -> Evidence-linked Edge Strength
Skilled routine        -> Memory Pathway
Memory consolidation   -> Consolidation Engine
Forgetting             -> stale/decay/pruning/lifecycle
Plasticity             -> Adaptive Slots / Thawing
Inhibition             -> Policy / suppression / precedence
Relearning             -> contradiction -> thaw -> revalidation
Individual differences -> Project/User Overlays
```

The analogy is architectural, not a claim of biological equivalence.

## 19. Key Novelty Boundary

BioHarness should not claim novelty for embeddings, vector search, graph storage, temporal memory, forgetting, or workflow DAGs themselves.

The BioHarness-specific research direction is the combination of:

- hierarchical scientific-memory activation;
- temporary TaskMemoryGraph construction;
- evidence-grounded reusable Memory Pathways;
- module/workflow Memory Packs;
- controlled plasticity and thawing;
- scope overlays;
- outcome-driven consolidation;
- integration with scientific Policy, Run, Artifact, Decision, and provenance semantics.

The key objective is not merely to make an agent remember more. It is to allow a research organization to repeatedly convert scientific activity into inspectable, reusable, adaptable procedural memory without losing evidence or governance.
