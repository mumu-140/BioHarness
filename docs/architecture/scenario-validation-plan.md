# BioHarness Architecture Scenario Validation Plan

Date: 2026-09-17
Status: Executable-spec design
Execution status: NOT_RUN

This document defines future runtime tests. It does not claim that BioHarness currently implements or passes them.

Each scenario records:

- preconditions;
- action;
- expected state transition or outcome;
- forbidden behavior;
- evidence that must be captured.

## 1. TF-Tree Vertical-Slice Scenarios

### TF-01 Preserve leading-zero UID

Status: `NOT_RUN`

Preconditions:

- Genome registration contains UID `00902`.
- All required TF workflow input files are valid.

Action:

- Resolve data and create a governed RunSpec.

Expected:

- `ResolvedDataRef` and RunSpec preserve `00902` exactly as a string.
- Provider submission receives the same identity.

Forbidden:

- converting UID to integer `902`;
- silently aliasing the two values.

Evidence:

- resolved input snapshot;
- RunSpec serialization;
- provider invocation record.

### TF-02 Reject cross-UID biological identity conflict

Status: `NOT_RUN`

Preconditions:

- two registered genomes contain an ID collision that violates the provider's current global identity contract.

Action:

- resolve inputs and run provider preflight.

Expected:

- ScientificAssessment or provider preflight blocks submission;
- no external workflow is launched.

Forbidden:

- automatic ID renaming;
- merging records across genomes to make the workflow continue.

Evidence:

- conflict details;
- assessment/preflight result;
- absence of external execution ID.

### TF-03 All families explicitly skipped

Status: `NOT_RUN`

Preconditions:

- every TF family contains fewer sequences than the configured `min_seqs` threshold.

Action:

- execute the provider workflow.

Expected:

- provider emits its complete all-skipped candidate/audit representation if consistent with the existing workflow contract;
- BioHarness retains an auditable RunAttempt and Artifact set;
- no MAFFT/IQTREE task is fabricated.

Forbidden:

- treating an empty downstream task list as lost workflow state;
- inventing tree results.

Evidence:

- trace/log;
- candidate manifest;
- validation result.

### TF-04 Resume after tool failure

Status: `NOT_RUN`

Preconditions:

- same immutable RunSpec;
- first RunAttempt fails after at least one cacheable upstream task completes;
- provider work/cache remains intact.

Action:

- create a second RunAttempt using provider-supported resume.

Expected:

- RunSpec remains unchanged;
- RunAttempt identity changes;
- compatible cached work may be reused;
- provenance shows which outputs were reused and which recomputed.

Forbidden:

- mutating the original failed attempt into a successful historical record;
- changing scientific parameters during the retry without creating a new RunSpec.

Evidence:

- both attempt records;
- executor trace/cache evidence;
- final artifact lineage.

### TF-05 Lost submission acknowledgement

Status: `NOT_RUN`

Preconditions:

- provider accepts submission;
- BioHarness loses the acknowledgement before binding an external execution ID.

Action:

- recover the RunAttempt.

Expected:

- state transitions to `UNKNOWN` or equivalent reconciliation state;
- system queries provider state using recorded request/idempotency metadata;
- duplicate submission occurs only if absence of an equivalent external job is established and policy allows retry.

Forbidden:

- immediate blind resubmission.

Evidence:

- submission intent event;
- reconciliation queries;
- provider lookup result;
- final binding decision.

### TF-06 Corrupted candidate package

Status: `NOT_RUN`

Preconditions:

- external Nextflow execution reaches completion;
- candidate bundle is missing or contains a corrupted required artifact.

Action:

- run independent candidate validation.

Expected:

- RunAttempt may be `FINISHED`;
- ValidationReport = `FAIL`;
- no canonical/publication gate opens.

Forbidden:

- deriving scientific validity from external exit code alone.

Evidence:

- artifact inventory;
- validator report;
- publication/canonical state.

### TF-07 IQ-TREE parameter-local invalidation

Status: `NOT_RUN`

Preconditions:

- baseline candidate exists;
- only a result-affecting IQ-TREE parameter changes;
- input sequences and alignment-producing parameters remain identical.

Action:

- create and execute the changed analysis.

Expected:

- new RunSpec;
- provider cache may reuse scientifically identical MAFFT outputs;
- IQ-TREE results and candidate validation rerun;
- lineage links reused alignment artifacts to the new analysis where appropriate.

Forbidden:

- re-labeling the old tree as generated under the new parameters.

Evidence:

- old/new RunSpec hashes;
- trace/cache records;
- new tree provenance;
- new validation report.

### TF-08 No implicit publication

Status: `NOT_RUN`

Preconditions:

- candidate validation passes.

Action:

- complete P0 workflow without a separate publication Decision.

Expected:

- candidate Artifact remains non-canonical/non-production;
- production DB and production paths remain unchanged.

Forbidden:

- automatic loader execution;
- canonical pointer update;
- production API state mutation.

Evidence:

- candidate manifest;
- policy/decision log;
- production-state comparison or mocked publication boundary assertion.

## 2. RNA-seq -> GO Scientific-Contract Scenarios

These scenarios validate architecture semantics before a real RNA-seq provider is selected.

### RNA-01 Ambiguous biological intent

Status: `NOT_RUN`

Request:

> "For this gene, get differential genes and do GO enrichment."

Preconditions:

- no perturbation, contrast, or upstream DEG set is identified from authoritative project context.

Expected:

- `ScientificTaskSpec.unresolved_fields` records the missing comparison/gene-set rule;
- governed execution does not begin.

Forbidden:

- model invents a default treatment/control comparison;
- model substitutes coexpression for differential expression without explicit resolution.

Evidence:

- TaskSpec;
- unresolved-field explanation.

### RNA-02 Unsupported count semantics

Status: `NOT_RUN`

Preconditions:

- data object is labeled as an expression matrix but represents normalized abundance whose semantics do not satisfy the selected DE module contract.

Action:

- assess compatibility.

Expected:

- ScientificAssessment = `INCOMPATIBLE` for that module;
- alternative valid modules may be proposed but not silently substituted in a governed Run.

Forbidden:

- deciding compatibility only from whether matrix values look integer-like or non-negative.

Evidence:

- DataObject semantics;
- Module scientific contract;
- assessment record.

### RNA-03 Perfect confounding

Status: `NOT_RUN`

Preconditions:

- treatment and batch are perfectly confounded, so the requested treatment effect cannot be independently estimated.

Action:

- compile the differential-expression TaskSpec and assessment.

Expected:

- ScientificAssessment = `NOT_IDENTIFIABLE` or equivalent blocker;
- policy authorization does not change that result.

Forbidden:

- "batch correction" used to manufacture a treatment effect from an unidentifiable design.

Evidence:

- sample design matrix/schema;
- identifiability assessment;
- no official DE RunSpec.

### RNA-04 Identifier namespace mismatch before GO

Status: `NOT_RUN`

Preconditions:

- DEG set uses one gene-ID namespace;
- GO annotation provider expects another;
- no validated mapping is currently resolved.

Action:

- build the GO branch.

Expected:

- task is unresolved until an explicit mapping source/revision is selected and mapping QC is available.

Forbidden:

- string heuristics that guess identifiers from prefixes/suffixes;
- dropping unmapped genes without provenance.

Evidence:

- source and target namespaces;
- selected mapping revision;
- mapping coverage/ambiguity report.

### RNA-05 Background universe is provenance-bearing

Status: `NOT_RUN`

Preconditions:

- selected DEG set exists.

Action:

- run GO-enrichment planning.

Expected:

- background universe is explicit and tied to the upstream tested/eligible gene universe and annotation state;
- annotation version, mapping rule, and multiple-testing method are frozen into RunSpec/Artifact provenance.

Forbidden:

- unrecorded switch to "all genes in database";
- background changed solely to increase significant terms.

Evidence:

- selected-gene set identity;
- background set identity;
- annotation/mapping versions;
- enrichment parameters.

### RNA-06 Valid null result

Status: `NOT_RUN`

Preconditions:

- design is identifiable;
- data/module contracts pass;
- workflow and validation pass;
- no gene or GO term passes the predefined significance criteria.

Expected:

- analysis may be scientifically `SUPPORTED` with a null/negative result;
- system does not mark it as failure because discovery count is zero.

Forbidden:

- automatic threshold relaxation;
- repeated parameter search whose reward is the number of discoveries.

Evidence:

- frozen thresholds;
- ValidationReport;
- final interpretation.

## 3. Pathway Reactivation and Change-Impact Scenarios

### MEM-01 Bulk RNA-seq pathway reactivated for single-cell data

Status: `NOT_RUN`

Preconditions:

- a stable/dormant bulk RNA-seq -> DEG -> ID mapping -> GO pathway exists;
- new task uses multi-sample single-cell RNA-seq.

Action:

- reactivate the pathway.

Expected:

- pathway can recall useful components and pitfalls;
- `ChangeImpactContract` flags experimental-unit/statistical-model changes;
- old DEG evidence and old enrichment background are not reused as if scientifically equivalent;
- downstream software components may be reused only after input/assumption compatibility is re-established.

Forbidden:

- preserving old downstream scientific validity because the node/edge topology looks unchanged.

Evidence:

- compatibility report;
- thawed/retained components;
- downstream invalidation set.

### MEM-02 Annotation-release change

Status: `NOT_RUN`

Preconditions:

- prior pathway used annotation release v3;
- current project resolves release v4.

Expected:

- revalidation propagates to ID mapping, selected/background gene membership, annotation coverage, and enrichment as declared by the impact contract;
- unrelated presentation settings remain reusable.

Forbidden:

- treating annotation version as a low-impact slot automatically.

Evidence:

- old/new ResolvedDataRefs;
- impact graph/report;
- recomputed/revalidated artifacts.

### MEM-03 Dormant but valid pathway

Status: `NOT_RUN`

Preconditions:

- pathway is `STABLE + DORMANT` with no version incompatibility or fatal contradiction.

Action:

- run a highly relevant compatible task.

Expected:

- activation can increase without changing maturity or scope;
- historical evidence remains traceable.

Forbidden:

- interpreting dormancy as deprecation.

Evidence:

- activation-state transition;
- unchanged maturity/scope.

## 4. Memory Consolidation and Promotion Scenarios

### PROM-01 Repeated runs on the same data are correlated evidence

Status: `NOT_RUN`

Preconditions:

- ten successful executions use the same source dataset and same biological experiment but occur in different sessions/projects.

Expected:

- `execution_count` may increase to ten;
- independent dataset/study count does not become ten;
- scope promotion does not treat these as ten independent biological validations.

Forbidden:

- PROJECT -> METHOD promotion based on raw execution count alone.

Evidence:

- provenance grouping by source data/experiment;
- support-diversity statistics.

### PROM-02 Fatal contradiction overrides historical frequency

Status: `NOT_RUN`

Preconditions:

- pathway has many historical successful uses;
- new high-quality evidence demonstrates that the core scientific assumption is invalid under the pathway's current scope.

Expected:

- pathway becomes `CONTRADICTED` or is blocked from stable reuse pending review;
- contradiction is mandatory context for relevant future tasks.

Forbidden:

- historical usage frequency outvoting the fatal contradiction numerically.

Evidence:

- contradiction source;
- lifecycle transition;
- future ContextSnapshot showing the contradiction.

### PROM-03 Project-stable does not imply method-wide

Status: `NOT_RUN`

Preconditions:

- pathway is stable across many runs in one project.

Expected:

- maturity may become `STABLE`;
- scope remains `PROJECT` until independent cross-context evidence and a promotion Decision justify broader reuse.

Forbidden:

- automatic `METHOD` or `LAB` promotion from high local frequency.

Evidence:

- maturity/scope histories;
- promotion-gate decision record.

### PROM-04 Memory cannot directly become Policy

Status: `NOT_RUN`

Preconditions:

- a validated failure lesson has strong support.

Action:

- retrieve it in a later relevant task.

Expected:

- memory can affect assessment, warning, experiment proposal, or configuration candidate;
- hard policy changes only through explicit Decision/policy mutation path.

Forbidden:

- memory provider writes/changes Policy automatically.

Evidence:

- memory retrieval record;
- any Decision created;
- policy revision history.

## 5. Retrieval and Context Scenarios

### CTX-01 Exact Run ID bypasses unnecessary hierarchy traversal

Status: `NOT_RUN`

Preconditions:

- user requests `run:183` explicitly.

Expected:

- exact authoritative lookup is attempted first;
- hierarchy/graph expansion is added only if needed for the question.

Forbidden:

- semantic nearest-neighbor result replacing the exact Run record.

### CTX-02 Hard policy and fatal contradiction do not compete in top-k

Status: `NOT_RUN`

Preconditions:

- relevant hard Policy and fatal contradiction exist;
- many semantically similar but non-authoritative memories also exist.

Expected:

- mandatory policy/contradiction context is loaded deterministically;
- semantic retrieval ranks optional/contextual memories separately.

Forbidden:

- safety/scientific blocker omitted because it ranked below top-k.

## 6. Evidence Required Before Any Completion Claim

A future implementation must not mark this validation plan as passed merely because architecture documents exist.

For each executed scenario, record:

```text
scenario_id
implementation revision
test/run command or API action
input fixture/data identity
observed output/state transitions
expected-vs-observed comparison
pass/fail/inconclusive
execution timestamp
supporting logs/artifacts
```

Only then may a scenario move from `NOT_RUN` to an executed status.

## 7. Current Summary

```text
TF scenarios: NOT_RUN
RNA-seq/GO scenarios: NOT_RUN
pathway reactivation scenarios: NOT_RUN
memory promotion scenarios: NOT_RUN
context retrieval scenarios: NOT_RUN
```

No runtime correctness claim is made by this document.
