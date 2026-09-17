# BioHarness Memory Pathway Consolidation and Promotion

Date: 2026-09-17
Status: Design record v1 for review
Scope: Criteria and lifecycle for turning temporary TaskMemoryGraph structure into reusable Memory Pathways, while keeping activation, scientific maturity, and scope promotion independent.

Related documents:

- `docs/architecture/hierarchical-associative-memory.md`
- `docs/architecture/provider-composition-and-research-memory.md`
- `docs/architecture/reference-architectures.md`
- `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`

## 1. Design Decision

BioHarness must not consolidate a Memory Pathway because a subgraph appears frequently.

A repeated scientific chain can be:

- heavily used but unstable;
- heavily used but wrong;
- reliable but project-specific;
- stable but currently dormant;
- broadly reusable but temporarily inactive.

Therefore pathway learning uses **independent dimensions plus hard promotion gates**, not one opaque scalar score.

The core rule is:

```text
frequency       -> activation
scientific evidence -> reliability
low mutation    -> stability
cross-scope reuse -> generality
```

These signals may contribute to an auxiliary `ConsolidationConfidence`, but no numerical score may bypass evidence, contradiction, validation, or scope-promotion gates.

## 2. Three Independent Axes

Every durable Memory Pathway should expose three separate dimensions.

### 2.1 Activation

Question: how likely should this pathway be recalled now?

Typical states:

```text
HOT
WARM
DORMANT
```

Activation is affected by current task relevance, active-project relevance, recent use, explicit pinning, semantic/graph similarity, and current user/method context.

High frequency primarily affects activation. It does not by itself establish scientific validity.

### 2.2 Maturity / Scientific Stability

Question: how mature and trustworthy is this pathway?

Typical states:

```text
EXPLORATORY
ADAPTIVE
STABLE
CONTRADICTED
DEPRECATED
```

Maturity depends on evidence, successful validated use, contradiction history, mutation rate, and version/scope compatibility.

### 2.3 Scope

Question: where is this pathway justified for reuse?

Recommended scopes:

```text
TASK
PROJECT
METHOD
LAB
```

A pathway can be `STABLE + PROJECT` forever. Maturity never implies broader scope.

This is a hard invariant:

> **Pathway maturity promotion and pathway scope promotion are separate operations.**

## 3. Candidate Discovery

Candidate pathways may originate from either automatic mining or explicit human authorship.

### Automatic proposal

Repeated TaskMemoryGraphs are compared to find structurally similar subgraphs. Task-specific constants are abstracted into candidate slots.

Example observations:

```text
Gene A -> Dataset 1 -> DESeq2 -> DEG -> ID map -> GO
Gene B -> Dataset 2 -> DESeq2 -> DEG -> ID map -> GO
Gene C -> Dataset 3 -> edgeR  -> DEG -> ID map -> GO
```

Possible candidate:

```text
GeneRef
  -> ExpressionDatasetRef
  -> DifferentialAnalysis
  -> DifferentialGeneSet
  -> GeneIdMapping
  -> FunctionalEnrichment
```

Possible adaptive slots:

```text
species
reference assembly
expression dataset
contrast
DE method
software version
annotation source
FDR preset
background universe
```

### Human-authored proposal

A researcher may explicitly define a pathway from a laboratory SOP, paper-derived procedure, or repeatedly used research strategy. Human authorship does not bypass evidence and validation requirements for shared promotion.

## 4. Promotion Gates

A candidate is evaluated by multiple gates. These gates are conceptually independent.

### 4.1 Evidence Gate

The pathway must retain traceable support from authoritative or evidence-bearing objects such as:

- Runs;
- Artifacts;
- QC results;
- Decisions;
- validated Findings;
- Papers/reference workflows;
- benchmark results.

A pathway derived only from model-generated text or retrieval co-occurrence cannot become stable shared scientific memory.

### 4.2 Reliability Gate

Reliability asks whether the pathway produces acceptable scientific outcomes under its stated scope.

Signals may include:

```text
validated successful runs
QC pass rate
manual validation
benchmark agreement
reproducibility across reruns
complete provenance
```

Raw execution success is insufficient. A process can execute without error and still be scientifically wrong.

### 4.3 Stability Gate

Stability asks whether the pathway has stopped changing materially.

BioHarness should distinguish at least two mutation classes.

#### Structural mutation

Changes to pathway topology or scientific reasoning, for example:

```text
DEG -> GO
```

becoming:

```text
DEG -> ID mapping -> background validation -> GO
```

Structural mutation strongly reduces confidence that the pathway is mature.

#### Slot mutation

Changes within declared adaptive slots, for example:

```text
FDR 0.05 -> 0.01
DESeq2 -> edgeR
annotation v3 -> v4
```

Slot mutation may be expected and should carry a much smaller stability penalty when the pathway explicitly declares the slot as adaptive.

Frequent use plus frequent structural editing means the pathway is important but still `ADAPTIVE`, not `STABLE`.

### 4.4 Contradiction Gate

Contradictory evidence is not treated as a simple negative count against many historical successes.

Contradictions should be typed by severity:

```text
MINOR
MAJOR
FATAL
```

- `MINOR`: presentation or non-scientific preference; usually does not affect the stable core.
- `MAJOR`: invalidates an adaptive slot/default or an important branch and triggers partial thaw.
- `FATAL`: challenges the core scientific logic and immediately prevents stable reuse until reviewed.

A single high-quality fatal contradiction can override many prior apparently successful uses.

### 4.5 Generalization Gate

Generalization asks whether the pathway is reusable beyond one local context.

Raw run count is not sufficient.

```text
100 successful runs in one project
```

may still support only `PROJECT` scope.

More informative support includes diversity across:

```text
projects
datasets
species or biological contexts when relevant
task instances
users/agents
software/environment revisions
```

Scope promotion should consider **independent support diversity**, not merely total frequency.

## 5. Lifetime Statistics and Recent-Window Statistics

BioHarness should retain both lifetime history and recent behavior.

Lifetime statistics preserve provenance and long-term evidence.

Recent-window statistics are more informative for current stability.

Example:

```text
first 20 uses: 14 pathway edits
last 12 uses: 0 structural edits, 1 slot update
```

A lifetime mutation ratio alone would incorrectly keep the pathway permanently unstable.

Therefore maturity evaluation should use:

```text
lifetime_support
lifetime_failures
lifetime_mutations
+
recent_support
recent_failures
recent_structural_mutations
recent_slot_mutations
```

The exact recent window can later be implemented as a configurable number of activations, a project phase, or a time window. The contract should not hard-code one choice initially.

## 6. Maturity Promotion

A typical maturity progression is:

```text
OBSERVED SUBGRAPH
      ↓ repeated occurrence or explicit authorship
CANDIDATE
      ↓ evidence + usable outcome
ADAPTIVE
      ↓ strong reliability + declining structural mutation
STABLE
```

`CONTRADICTED` and `DEPRECATED` are not lower confidence values on the same scale; they are explicit scientific/lifecycle states.

A pathway may move from `STABLE` back to `ADAPTIVE` through audited thawing when new evidence, version change, or environmental mismatch requires modification.

## 7. Scope Promotion

Scope is promoted independently from maturity.

A typical route is:

```text
TASK
  ↓
PROJECT
  ↓ independent reuse / abstraction
METHOD_CANDIDATE
  ↓ validation across relevant contexts
METHOD
  ↓ explicit institutional decision when justified
LAB
```

Conceptually:

```text
PROJECT_ADAPTIVE
      ↓ stability
PROJECT_STABLE
      ↓ independent cross-project evidence
METHOD_CANDIDATE
      ↓ abstraction + revalidation
METHOD_STABLE
      ↓ explicit Decision / human approval
LAB_SHARED
```

No automatic rule should convert a stable project-specific pathway into laboratory-wide scientific knowledge merely because it has high frequency or a high aggregate score.

## 8. Automatic vs Human Responsibilities

The first implementation should automate evidence collection and proposals more aggressively than scientific promotion.

### BioHarness may automate

- repeated-subgraph detection;
- candidate pathway creation;
- usage/support statistics;
- success/failure statistics;
- structural and slot mutation statistics;
- contradiction detection/proposals;
- activation adjustment;
- frozen-core/adaptive-slot proposals;
- closeout consolidation proposals;
- dormant reactivation proposals;
- compatibility checks.

### Human/Decision gate should initially remain for

- promoting important shared scientific pathways;
- widening scope from PROJECT to METHOD when scientific applicability is non-trivial;
- LAB_SHARED promotion;
- accepting or resolving MAJOR/FATAL contradictions;
- changing locked institutional knowledge;
- overriding explicit scientific policy.

Later, empirical benchmark evidence may justify relaxing selected gates, but that is not assumed in the initial architecture.

## 9. Consolidation Confidence Is Advisory

A composite confidence may be useful for ranking candidate pathways for review.

Conceptually it may consider:

```text
reliability
stability
evidence strength
reuse diversity
generality
contradiction burden
version compatibility
```

However:

```text
ConsolidationConfidence != scientific truth
ConsolidationConfidence != scope authority
ConsolidationConfidence != policy authority
```

It must never bypass a hard gate.

Initial architecture should avoid embedding arbitrary fixed weights into the domain model. Weighting can be benchmarked later and may differ by memory/pathway type.

## 10. Example: Active Project to Dormant Reusable Knowledge

During an active project:

```text
uses = 38
successful = 31
failures = 7
structural_mutations = 8
slot_mutations = 8
independent_projects = 1
```

Interpretation:

```text
activation = HOT
maturity = ADAPTIVE
scope = PROJECT
```

Later in the same project:

```text
last 12 uses:
  successful = 12
  structural_mutations = 0
  slot_mutations = 1
  fatal_contradictions = 0
```

The pathway may become:

```text
activation = HOT
maturity = STABLE
scope = PROJECT
```

At project closeout:

```text
activation -> WARM -> DORMANT
maturity remains STABLE
scope remains PROJECT unless separately promoted
```

If a later independent project reactivates and successfully adapts the pathway, the system gains evidence for a possible METHOD-level abstraction. It does not automatically perform that promotion.

## 11. Minimal Pathway Record

A pathway record should eventually support at least the following conceptual fields:

```text
identity / revision
scope
maturity
activation

frozen_core
adaptive_slots

support statistics
success/failure statistics
validation evidence
mutation history
contradiction history
scope diversity

source TaskMemoryGraphs
source Runs
source Artifacts
source Decisions
source Papers / references

last_activated_at
last_modified_at
last_validated_at
last_contradicted_at
```

This is a semantic contract, not a final database schema.

## 12. Relationship to Mature Work

BioHarness should reuse mature mechanisms rather than reproducing them.

Relevant inspirations already cataloged in `reference-architectures.md` include:

- **Agent Workflow Memory (AWM)**: induction of reusable routines from historical trajectories;
- **LEGOMem**: modular procedural-memory units rather than only monolithic trajectories;
- **Voyager**: successful behaviors promoted into a reusable skill library;
- **Reflexion / ExpeL**: outcome- and feedback-derived experiential memory;
- **HippoRAG / A-MEM**: associative/graph-based retrieval and evolving memory relationships;
- **TiMEM**: temporal/hierarchical consolidation patterns;
- **Graphiti**: temporal graph infrastructure and evolving relations;
- **Complementary Learning Systems**: conceptual inspiration for fast task memory plus slower consolidation.

BioHarness-specific semantics remain scientific evidence, provenance, project lifecycle, pathway scope, controlled thawing, and explicit Decision/Policy boundaries.

## 13. Architecture Invariants

1. Frequency affects activation more directly than scientific maturity.
2. Execution success is not equivalent to scientific validation.
3. High-frequency/high-mutation pathways remain adaptive.
4. Structural mutation and adaptive-slot mutation are not equivalent.
5. Contradictions are severity-aware; fatal scientific contradiction can block reuse regardless of historical frequency.
6. Recent stability and lifetime provenance are both retained and used for different purposes.
7. Maturity promotion and scope promotion are independent.
8. A pathway may remain `STABLE + PROJECT` indefinitely.
9. Cross-project diversity, not raw run count, is the main signal for broader generalization.
10. Composite consolidation scores are advisory and cannot bypass evidence/contradiction/promotion gates.
11. METHOD/LAB scientific promotion is auditable and initially requires an explicit Decision/human gate where applicability is non-trivial.
12. Scope promotion never directly creates or overrides Policy.

## 14. Open Implementation Choices

The following are intentionally not fixed by this design record and should be benchmarked or chosen during implementation planning:

- exact formula for `ConsolidationConfidence`;
- recent-window size;
- graph-substructure similarity algorithm;
- thresholds for candidate generation;
- exact vector/graph backend;
- whether pathway-mining proposals use deterministic graph mining, LLM-assisted abstraction, or a hybrid;
- which low-risk scope promotions can eventually be automated.

The architecture requires these decisions to remain observable, versioned, and replaceable rather than hidden in an opaque model.
