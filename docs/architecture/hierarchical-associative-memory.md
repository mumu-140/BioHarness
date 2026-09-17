# BioHarness Hierarchical Associative Memory Architecture

Date: 2026-09-17
Status: Design record v2 for review
Scope: Brain-inspired research memory retrieval, task working memory, pathway consolidation, project-lifecycle-aware dormancy/reactivation, and controlled plasticity. This document defines BioHarness-specific semantics; storage engines and retrieval infrastructure should be reused from mature projects whenever possible.

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
7. execution outcomes feed back into memory through evidence-backed consolidation;
8. project lifecycle affects memory activation and plasticity, but not scientific validity;
9. project completion triggers consolidation and dormancy, not destructive forgetting;
10. dormant knowledge can be reactivated and partially thawed when a later task makes it relevant again.

This is inspired by long-term memory -> associative activation -> working memory -> action -> consolidation/reconsolidation, but BioHarness does not claim to reproduce biological neural mechanisms.

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
- edit/mutation rate;
- absence of strong contradictions;
- version/scope compatibility.

High-frequency/high-edit-rate pathways are important but still unstable. They should remain actively adaptive until their mutation rate falls and validation remains strong.

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

## 10. Scientific Validity and Activation Are Independent

BioHarness must not equate "rarely used" with "scientifically invalid".

Every durable memory/pathway should separate at least two dimensions:

### Stability / Validity

Question: how mature and trustworthy is this knowledge?

Conceptual factors:

```text
validated success
+ evidence strength
+ cross-task reuse
+ generality
+ time without contradiction
- failure rate
- contradiction
- mutation/edit rate
```

Typical states:

```text
EXPLORATORY
ADAPTIVE
STABLE
CONTRADICTED
DEPRECATED
```

### Activation

Question: how strongly should this memory be recalled for work happening now?

Conceptual factors:

```text
current task relevance
+ active project relevance
+ current user/method relevance
+ recent use
+ semantic/graph similarity
+ explicit pinning
```

Typical states:

```text
HOT
WARM
DORMANT
```

The important case is:

```text
stability = STABLE
activation = DORMANT
```

This means mature knowledge is currently unused, not obsolete.

`DORMANT` and `DEPRECATED` are therefore fundamentally different.

## 11. Project-Lifecycle-Aware Plasticity

Research projects have phases. Memory behavior should follow them.

### Active project phase

During active research, relevant memories/pathways are frequently used, repaired, compared, and refined.

The default posture is:

```text
high activation
high observability
high plasticity for adaptive slots
frequent evidence updates
```

Frequent modification is a signal of importance but not maturity.

### Stabilization phase

When a pathway continues to succeed while its edit rate declines, it may move toward `STABLE`.

### Project completion

Project completion should not delete or invalidate the project's memory. It should trigger explicit consolidation and reduce default activation of project-specific material.

## 12. Project Closeout Consolidation

`Project.close()` is a research-memory event, not only a project-status change.

A closeout consolidation should conceptually perform four operations.

### Preserve exact history

Keep immutable/traceable links among:

- Project;
- ContextSnapshots;
- Runs;
- Artifacts;
- Decisions;
- validated Findings;
- historical pathway revisions.

### Extract reusable knowledge

Classify project knowledge by scope:

```text
project-only knowledge
        ↓ remains Project Memory

reusable method knowledge
        ↓ may become Method Memory

broad validated institutional knowledge
        ↓ may be proposed for Lab Memory
```

Promotion still requires evidence and the normal Decision/Policy gates.

### Consolidate procedural pathways

Replay historical TaskMemoryGraphs and successful Runs to detect repeated, low-volatility, evidence-backed subgraphs that can become reusable Memory Pathways or Memory Packs.

### Cool low-value working traces

Temporary retrieval traces, intermediate TaskMemoryGraphs, and low-value observations should stop participating in default retrieval after closeout unless they were explicitly consolidated or remain necessary for provenance.

Project closeout is therefore analogous to an offline consolidation phase rather than an erasure point.

## 13. Dormancy Is Retrieval-Level Forgetting

BioHarness should primarily "forget" by reducing activation, not by destroying scientific history.

When a project/pathway becomes inactive:

```text
ACTIVE/HOT
   ↓ project completed + low use
WARM
   ↓ sustained inactivity
DORMANT
```

A dormant pathway keeps a lightweight searchable entry, for example:

```yaml
pathway: poplar-rnaseq-deg-go
scope: method
summary: Populus RNA-seq differential expression followed by GO enrichment
concepts:
  - RNA-seq
  - differential expression
  - gene ID mapping
  - GO enrichment
stability: STABLE
activation: DORMANT
last_active: 2026-11-04
source_projects:
  - drought-2026
  - root-development-2026
detail_ref: memory://pathway/2381
```

Default retrieval does not need to load all historical Runs, Papers, Artifacts, and rationale. It only needs enough index metadata to allow future reactivation.

## 14. Reactivation and Partial Thawing

A future relevant task may reactivate a dormant pathway.

```text
DORMANT
  ↓ relevant task / explicit request
REACTIVATED
  ↓ compatibility check
  ├── compatible -> reuse stable core
  └── mismatch -> thaw affected slots
```

Reactivation must not blindly reuse historical configuration.

Compatibility checks may include:

- reference assembly/version;
- data schema/identifier namespace;
- software/tool version;
- annotation/database version;
- workflow/module revision;
- lab/project policy changes;
- current compute/runtime constraints;
- previously recorded contradictions.

Only affected regions need to thaw. A stable downstream chain may remain reused while one upstream segment is replaced.

Example:

```text
Stable core:
DEG set -> ID mapping -> GO enrichment

New task:
scRNA-seq instead of bulk RNA-seq

Thaw/replace:
RNA-seq dataset -> differential-analysis branch

Reuse:
ID mapping -> GO enrichment
```

## 15. Reconsolidation

After a reactivated pathway is changed, BioHarness should treat the update as **reconsolidation**, not silent mutation.

```text
Stable/Dormant Pathway
        ↓ reactivation
Compatibility / contradiction signal
        ↓
Partial thaw
        ↓
TaskMemoryGraph expansion
        ↓
new Run / Evidence / Validation
        ↓
new pathway revision
        ↓
reconsolidated STABLE or ADAPTIVE pathway
```

The previous revision remains addressable for reproducibility.

Reconsolidation is an engineering analogy to memory-update concepts in cognitive/neuroscience literature; BioHarness implements it as explicit versioned graph/pathway revision, not biological learning.

## 16. Module/Workflow Memory Packs

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

## 17. Controlled Plasticity

Memory structures should support different degrees of plasticity.

Recommended plasticity classes:

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

A thaw is an auditable transition that temporarily increases plasticity for selected nodes/edges/slots. It does not erase the previous pathway revision.

## 18. Frozen Core + Adaptive Slots

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

## 19. Shared Base + Scope Overlays

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

## 20. Weighted Associative Edges

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

## 21. Fast Cognition and Slow Consolidation

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
usage + mutation statistics
      ↓
Consolidation Engine
      ↓
strengthen/weaken edges
      ↓
propose/update pathway
      ↓
validated Persistent Memory
```

### Closeout loop

```text
Project.close()
      ↓
replay project history
      ↓
separate project-specific vs reusable knowledge
      ↓
consolidate reusable pathways/memory packs
      ↓
freeze exact provenance history
      ↓
reduce activation of inactive project memories
      ↓
DORMANT indexes retained for future reactivation
```

This allows BioHarness to become more efficient and more consistent with use without turning every new observation into an automatic rule.

## 22. Hard Deletion Policy

Durable scientific memory is not automatically deleted because of age or low use.

Default rule:

> **BioHarness forgets by reducing activation, not by destroying evidence.**

Hard deletion of durable ResearchMemory/MemoryPathway records requires one of:

- explicit authorized human action;
- a defined data-retention/privacy/compliance Policy;
- removal of an invalid temporary/generated record that has no required provenance role.

Examples that may be garbage-collected automatically according to policy:

- caches;
- duplicate embeddings/index material;
- expired scratch workspaces;
- non-promoted TaskMemoryGraph working copies;
- invalid generated summaries whose source evidence remains intact.

Examples that should not be automatically hard-deleted merely because they are old/inactive:

- Run history;
- Artifact provenance metadata;
- Decisions;
- validated Findings;
- historical pathway revisions;
- evidence-backed failure lessons;
- project closeout memory.

## 23. Safety and Governance Invariants

The memory architecture must preserve the following invariants:

1. Memory is derived knowledge; it is not automatically authoritative state.
2. A Memory Pathway cannot override Hard Policy or explicit Decision precedence.
3. Memory cannot directly promote itself into Policy. Promotion follows Evidence -> Validation/Experiment -> Decision -> Policy/Preset.
4. User personalization cannot modify shared scientific truth.
5. Shared-pathway thawing/promotion/reconsolidation must be auditable and versioned.
6. TaskMemoryGraph is temporary by default; only evidence-backed material is consolidated.
7. Retrieval weights never substitute for provenance or scientific validation.
8. Persistent memory must support superseded, contradicted, stale, dormant, deprecated, archived, and retracted semantics rather than naive deletion.
9. Scientific stability/validity and current activation are independent dimensions.
10. `DORMANT` means inactive but potentially valid; it must never be interpreted as `DEPRECATED`.
11. Project closeout triggers consolidation and cooling, not automatic deletion.
12. Hard deletion of durable scientific memory requires explicit human or policy authority.

## 24. Storage and Provider Strategy

Do not build a new vector database, graph database, or general-purpose memory engine unless required by BioHarness-specific semantics.

Initial implementation can use mature infrastructure such as:

- PostgreSQL for authoritative metadata, node/edge metadata, pathway definitions, decisions, lifecycle state, and audit history;
- pgvector or Qdrant for semantic indexes;
- TiMEM concepts/providers for temporal consolidation and retrieval;
- Graphiti/Neo4j only when graph-scale or temporal multi-hop requirements justify them;
- Genome-web and other domain stores as authoritative Data Providers;
- Nextflow/Snakemake as execution providers.

The BioHarness-owned part is the research semantics and lifecycle around TaskMemoryGraph, MemoryPathway, MemoryPack, scope overlays, evidence, promotion, project closeout, dormancy, reactivation, reconsolidation, and plasticity.

## 25. Engineering Analogy

The intended correspondence is:

```text
Long-term memory       -> Persistent Research Memory
Associative activation -> Hybrid Recall / Graph Expansion
Working memory         -> TaskMemoryGraph
Synaptic connection    -> Typed Memory Edge
Connection strength    -> Evidence-linked Edge Strength
Skilled routine        -> Memory Pathway
Memory consolidation   -> Consolidation Engine / Project Closeout
Forgetting             -> Activation reduction / Dormancy
Plasticity             -> Adaptive Slots / Thawing
Inhibition             -> Policy / suppression / precedence
Reactivation           -> Dormant pathway retrieval
Reconsolidation        -> Versioned pathway update after new evidence
Individual differences -> Project/User Overlays
```

The analogy is architectural, not a claim of biological equivalence.

## 26. Key Novelty Boundary

BioHarness should not claim novelty for embeddings, vector search, graph storage, temporal memory, forgetting, or workflow DAGs themselves.

The BioHarness-specific research direction is the combination of:

- hierarchical scientific-memory activation;
- temporary TaskMemoryGraph construction;
- evidence-grounded reusable Memory Pathways;
- module/workflow Memory Packs;
- independent activation and scientific-stability semantics;
- project-lifecycle-aware consolidation and dormancy;
- partial reactivation/thawing and versioned reconsolidation;
- scope overlays;
- outcome-driven consolidation;
- integration with scientific Policy, Run, Artifact, Decision, and provenance semantics.

The key objective is not merely to make an agent remember more. It is to allow a research organization to repeatedly convert scientific activity into inspectable, reusable, adaptable procedural memory without losing evidence or governance, while allowing inactive knowledge to sleep and later return when a new scientific task makes it relevant again.
