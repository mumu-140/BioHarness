# BioHarness Architecture Scenario Validation Plan

Date: 2026-09-18
Status: Authoritative executable-spec design
Execution status: NOT_RUN

This file is the single primary catalog of future architecture/runtime acceptance scenarios. It does not claim that BioHarness currently implements or passes them.

Every executed scenario must record:

```text
scenario_id
implementation revision
provider/workflow revision
input fixture/data identity
command/API action
observed state transitions
expected-vs-observed result
pass/fail/inconclusive
execution timestamp
supporting logs/artifacts
```

## 1. TF / P0 Identity and Scientific-Intent Scenarios

### TF-01 Preserve leading-zero UID
Status: `NOT_RUN`

Expected: `00902` remains exactly `00902` through ResolvedDataRef, resolved manifest, RunSpec, and provider invocation.

Forbidden: coercion to `902` or silent aliasing.

### TF-02 Reject cross-UID identity conflict
Status: `NOT_RUN`

Expected: assessment/provider preflight blocks submission; no external execution is launched.

Forbidden: auto-renaming IDs or merging records merely to continue.

### TF-03 Task intent excludes ordinary workflow defaults
Status: `NOT_RUN`

Expected:

- TaskSpec captures the scientific question/inference and candidate intent;
- `min_seqs`, representative-sequence implementation rule, MAFFT/IQ-TREE settings, seed, threads, and runtime appear in ResolvedConfiguration/RunSpec unless explicitly fixed by the scientific request;
- changing a result-affecting method parameter creates a new RunSpec without rewriting the scientific question.

### TF-04 All families explicitly skipped
Status: `NOT_RUN`

Expected: provider emits its complete auditable all-skipped representation when allowed by provider contract; no fabricated MAFFT/IQ-TREE task exists.

## 2. P0 Provider-Capability and Execution Scenarios

### EXEC-01 Capability honesty
Status: `NOT_RUN`

Expected for the current Genome-web TF pilot:

- `submission.mode=synchronous_process`;
- `compute.backend=local`;
- no remote-scheduler, provider-native exactly-once, or durable async lookup capability is fabricated;
- capability snapshot is tied to the inspected provider revision.

### EXEC-02 Attempt-scoped submission identity
Status: `NOT_RUN`

Expected:

- reconciliation of `ra-001` reuses its own request/submission identity where supported;
- a legitimate later `ra-002` points to the same RunSpec but has distinct attempt/submission identity;
- old attempt history remains immutable.

Forbidden: one permanent external submission key stored as RunSpec identity or blind duplicate submission while the prior attempt is unresolved.

### EXEC-03 Engine-internal retry remains inside one RunAttempt
Status: `NOT_RUN`

Expected: provider/Nextflow internal retry is execution provenance within the bound RunAttempt; it does not create a new BioHarness RunAttempt.

### EXEC-04 New resume launch is a new RunAttempt
Status: `NOT_RUN`

Expected: a new BioHarness-issued `--resume` launch creates a new RunAttempt while retaining the same RunSpec if intended computation is unchanged; reused cache lineage remains explicit.

### EXEC-05 Unknown state without reliable provider lookup
Status: `NOT_RUN`

Expected: when available evidence cannot establish the prior local/synchronous launch safely,

```text
UNKNOWN -> NEEDS_OPERATOR_RECONCILIATION
```

Forbidden: automatic duplicate launch merely to make progress.

### EXEC-06 Explicit resume lineage
Status: `NOT_RUN`

Expected: automated resume binds to explicit prior Nextflow session/run identity when reliably available; implicit `last` is not treated as scientific identity.

### EXEC-07 Resume after tool failure
Status: `NOT_RUN`

Expected: failed attempt remains immutable; a new attempt may reuse compatible cache; lineage distinguishes reused from recomputed work.

## 3. Data Identity and Provenance Scenarios

### DATA-01 Resolved manifest/member provenance
Status: `NOT_RUN`

Expected: exact resolved genome manifest/member identities consumed by Nextflow are registered/checkable independently of the original user-supplied manifest path.

### DATA-02 Mutable collection URI cannot masquerade as identical input
Status: `NOT_RUN`

Expected: changing membership from `{A,B}` to `{A,B,C}` changes provider revision/manifest/member identity and therefore RunSpec input identity even if the logical URI is unchanged.

### DATA-03 Annotation-release change propagates scientifically
Status: `NOT_RUN`

Expected: impact propagation reaches identifier mapping, selected/background membership, annotation coverage, and enrichment where relevant.

Forbidden: treating annotation version as automatically low-impact because it is an adaptive slot.

## 4. Validation and Publication Scenarios

### VAL-01 Provider PASS is typed
Status: `NOT_RUN`

Expected: provider candidate verification becomes typed `provider_contract` / `artifact_integrity` evidence; it does not set canonical/publication state by itself.

### VAL-02 Typed validation prevents generic PASS collapse
Status: `NOT_RUN`

Expected: artifact-integrity may pass while provenance-completeness fails/inconclusive; the relevant ValidationProfile keeps the gate closed.

### VAL-03 PASS_WITH_LIMITATIONS is gate-specific
Status: `NOT_RUN`

Expected: limitations remain attached and profile/policy explicitly determines eligibility; no silent coercion to `PASS`.

### VAL-04 Corrupted candidate package
Status: `NOT_RUN`

Expected: execution may be `FINISHED` while artifact/provider validation fails; no publication/canonical gate opens.

### VAL-05 No implicit publication
Status: `NOT_RUN`

Expected: a P0 candidate remains non-canonical/non-production until a separate publication Decision/gate.

## 5. Scientific Feasibility: RNA-seq -> GO

### SCI-01 Ambiguous biological intent
Status: `NOT_RUN`

Request: "For this gene, get differential genes and do GO enrichment."

Expected: TaskSpec records the missing perturbation/contrast/gene-set rule; governed execution does not begin.

### SCI-02 Unsupported count semantics
Status: `NOT_RUN`

Expected: incompatible expression semantics yield `ScientificAssessment=INCOMPATIBLE` for the chosen DE module.

Forbidden: judging compatibility only from integer-looking/non-negative values.

### SCI-03 Perfect confounding
Status: `NOT_RUN`

Expected: perfectly confounded treatment/batch yields `NOT_IDENTIFIABLE`; no official DE RunSpec.

### SCI-04 Pre-execution support is not hypothesis support
Status: `NOT_RUN`

Expected: assessment may be `ANALYSIS_SUPPORTED*` before execution, but no biological-effect Finding is created until evidence exists. A valid null result remains compatible with the historical feasibility assessment.

### SCI-05 Identifier namespace mismatch before GO
Status: `NOT_RUN`

Expected: GO branch remains unresolved until mapping source/revision and mapping QC are explicit.

### SCI-06 GO background universe is provenance-bearing
Status: `NOT_RUN`

Expected: selected set, tested/eligible background universe, annotation version, mapping rule, and multiple-testing method are frozen/traceable.

### SCI-07 Valid null result
Status: `NOT_RUN`

Expected: no significant genes/terms may still be a valid outcome when design/method/QC pass; no threshold relaxation or discovery-count reward loop.

## 6. Change-Impact and Pathway Reactivation

### MEM-01 Bulk pathway reactivated for single-cell data
Status: `NOT_RUN`

Expected: useful components/pitfalls may be recalled, but experimental unit/statistical model, old DEG evidence, gene-selection process, and enrichment background are re-evaluated before reuse.

### MEM-02 Dormant but valid pathway
Status: `NOT_RUN`

Expected: activation can increase without silently changing maturity/scope; dormancy is not deprecation.

## 7. Memory Promotion and Evidence Independence

### PROM-01 Repeated runs on the same experiment remain correlated evidence
Status: `NOT_RUN`

Expected: execution count may increase while independent dataset/study support does not.

### PROM-02 Fatal contradiction overrides historical frequency
Status: `NOT_RUN`

Expected: pathway becomes contradicted/blocked pending review and contradiction enters mandatory relevant context.

### PROM-03 Project-stable does not imply method-wide
Status: `NOT_RUN`

Expected: broader METHOD/LAB scope requires independent cross-context evidence plus promotion Decision.

### PROM-04 Memory cannot directly become Policy
Status: `NOT_RUN`

Expected: memory can influence warnings/assessment/experiments/configuration candidates; hard Policy changes only through governed mutation.

## 8. Retrieval and Content Trust

### CTX-01 Exact ID bypasses unnecessary hierarchy traversal
Status: `NOT_RUN`

Expected: exact authoritative lookup is attempted before semantic/hierarchical expansion.

### CTX-02 Hard policy and fatal contradiction do not compete in top-k
Status: `NOT_RUN`

Expected: mandatory policy/contradiction context is loaded deterministically; optional memories rank separately.

### SEC-01 External scientific content cannot mutate control state
Status: `NOT_RUN`

Expected: retrieved literature/tool/provider instructions remain source-tagged evidence/data and cannot create Policy, Decision, approval, command invocation, or canonical mutation by themselves.

## 9. Reproducibility

### REP-01 Seeded stochastic reproducibility
Status: `NOT_RUN`

Expected: repeated execution is judged against the declared result-equivalence/tolerance contract, not assumed byte identity.

### REP-02 Unknown nondeterminism remains explicit
Status: `NOT_RUN`

Expected: weaker/nonreplayable class is recorded; no fabricated seed or deterministic guarantee.

## 10. Canonical State and Authorization

### AUTH-01 Historical authorization cannot authorize a new side effect
Status: `NOT_RUN`

Expected: historical P1/ALLOW remains immutable evidence while current P2/DENY blocks a new launch or mutation.

### CANON-01 Concurrent canonical promotions use compare-and-swap
Status: `NOT_RUN`

Expected: a stale update using an older expected revision is rejected; last-writer-wins is forbidden.

## 11. Parameter-Local Reuse

### CACHE-01 IQ-TREE-only parameter change
Status: `NOT_RUN`

Expected: new RunSpec; compatible MAFFT output may be reused; tree and candidate validation rerun; old tree is not relabelled.

### CACHE-02 Protein-set change affecting one family
Status: `NOT_RUN`

Expected: new RunSpec; only scientifically identical cached family outputs may be reused; affected family and whole candidate package are recomputed/revalidated with explicit lineage.

## 12. Architecture-Evidence Maintenance

### EVID-01 Rolling source records inspection provenance
Status: `NOT_RUN`

Expected: rolling docs/repositories record `checked_at`, version/revision/date when available, inspection depth, and bounded claim scope.

## 13. Current Summary

```text
all architecture/runtime scenarios = NOT_RUN
```

No runtime correctness claim is made by this document.
