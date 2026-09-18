# BioHarness Architecture Acceptance Scenario Catalog

Date: 2026-09-18
Updated: 2026-09-19
Status: Authoritative acceptance-scenario design
Execution status: PARTIAL — `TF-01`, `TF-02`, `EXEC-01`, `EXEC-06`, and `DATA-01` have fresh PASS evidence; all other scenarios remain `NOT_RUN`.

This is the primary catalog of architecture/runtime acceptance scenarios. It is **not** itself an executable test harness. Individual scenario status changes require a concrete implementation/test record with fresh evidence.

Before a scenario may move from `NOT_RUN`, its implementation/test record must contain:

```text
scenario_id
setup / fixture identity
implementation revision
provider/workflow revision
input/data identity
action / injected failure
observable assertions
forbidden behavior
expected-vs-observed result
PASS | FAIL | INCONCLUSIVE
executed_at
supporting logs/artifacts/events
```

A future implementation plan converts these acceptance scenarios into concrete tests without weakening their assertions.

## 1. TF / P0 Identity and Intent

### TF-01 Preserve leading-zero UID
Status: `PASS`
Evidence: [`2026-09-19 Genome-web TF P0 reference acceptance`](../validation/records/2026-09-19-genome-web-tf-p0.md).
Assert: `00902` remains exactly `00902` through ResolvedDataRef, resolved manifest, RunSpec, and provider invocation.
Forbidden: coercion to `902` or silent aliasing.

### TF-02 Reject cross-UID identity conflict
Status: `PASS`
Evidence: [`2026-09-19 Genome-web TF P0 reference acceptance`](../validation/records/2026-09-19-genome-web-tf-p0.md).
Assert: provider/scientific preflight blocks launch on an invalid cross-UID identity conflict.
Forbidden: auto-renaming IDs or merging records merely to continue.

### TF-03 Task intent excludes provider defaults
Status: `NOT_RUN`
Assert: TaskSpec captures question/inference/logical biological scope; `min_seqs`, representative-sequence implementation rule, MAFFT/IQ-TREE settings, seed, threads, and runtime controls stay in configuration unless explicitly fixed by the scientific request.

### TF-04 All families explicitly skipped
Status: `NOT_RUN`
Assert: provider emits its auditable all-skipped representation when the configured eligibility rule excludes every family; no fabricated MAFFT/IQ-TREE task exists.

## 2. Authorization

### AUTH-01 Historical authorization cannot authorize a new launch
Status: `NOT_RUN`
Setup: RunSpec was planned under policy P1/ALLOW; current policy becomes P2/DENY before launch.
Assert: historical P1 decision remains immutable evidence; current P2 blocks launch; no external execution binding appears.

### AUTH-02 Protected data access is authorized before resolution
Status: `NOT_RUN`
Setup: requested provider resource requires read authorization.
Assert: current PolicyDecision for actor/action/resource exists before provider content is read/resolved; a DENY yields no ResolvedDataRef containing protected content.
Forbidden: resolving first and checking policy only at workflow submission.

## 3. Planning and Scientific Feasibility

### PLAN-01 Assessment binds to explicit method/data dependencies
Status: `NOT_RUN`
Assert: ScientificAssessment records TaskSpec, ResolvedDataRefs, and candidate scientific-contract revision used for feasibility reasoning.

### PLAN-02 Assumption-relevant configuration change forces reassessment
Status: `NOT_RUN`
Setup: configuration changes a method/parameter participating in an assessment compatibility predicate.
Assert: old assessment cannot authorize execution of the new configuration; assessment is recomputed/revalidated before executable RunSpec state.

### SCI-01 Ambiguous biological intent
Status: `NOT_RUN`
Request: "For this gene, get differential genes and do GO enrichment."
Assert: missing perturbation/contrast/gene-set rule remains explicit; governed analysis does not silently choose one.

### SCI-02 Unsupported count semantics
Status: `NOT_RUN`
Assert: incompatible expression semantics yield `INCOMPATIBLE` for the chosen DE contract.
Forbidden: deciding from integer-looking/non-negative values alone.

### SCI-03 Perfect confounding
Status: `NOT_RUN`
Assert: perfectly confounded treatment/batch yields `NOT_IDENTIFIABLE`; no official DE RunSpec is executable.

### SCI-04 Analysis support is not hypothesis support
Status: `NOT_RUN`
Assert: pre-execution `ANALYSIS_SUPPORTED*` creates no biological-effect Finding. A valid null result remains compatible with the historical feasibility assessment.

### SCI-05 Identifier mismatch before GO
Status: `NOT_RUN`
Assert: GO branch remains unresolved until mapping source/revision and mapping QC are explicit.

### SCI-06 GO background is provenance-bearing
Status: `NOT_RUN`
Assert: selected set, eligible/tested background, annotation version, mapping rule, and multiple-testing method are frozen/traceable.

### SCI-07 Valid null result
Status: `NOT_RUN`
Assert: no significant genes/terms may still be a valid outcome when design/method/QC pass.
Forbidden: threshold relaxation merely to increase discoveries.

## 4. Provider Capability and Execution

### EXEC-01 Capability honesty
Status: `PASS`
Evidence: [`2026-09-19 Genome-web TF P0 reference acceptance`](../validation/records/2026-09-19-genome-web-tf-p0.md).
For audited Genome-web revision `05072cbbcd533ca59afa13996d8d0edd8f939c6e`, assert: synchronous process, local backend, no native idempotency key, no durable async external ID/polling, no durable cancellation interface; limited reconciliation is explicitly constrained/evidenced.

### EXEC-02 Attempt-scoped submission identity
Status: `NOT_RUN`
Assert: reconciliation of `ra-001` uses its own request identity where supported; a legitimate later `ra-002` has a distinct attempt/submission identity but may point to the same RunSpec.
Forbidden: one permanent submission key on RunSpec.

### EXEC-03 Engine-internal retry remains one RunAttempt
Status: `NOT_RUN`
Assert: Nextflow-internal retry/re-execution is provider provenance inside the existing RunAttempt unless BioHarness issues a new external launch.

### EXEC-04 New resume launch is a new RunAttempt
Status: `NOT_RUN`
Assert: a BioHarness-issued new resume launch creates a new RunAttempt; same RunSpec is retained only when intended result-affecting work is unchanged.

### EXEC-05 Unknown outcome without durable lookup
Status: `NOT_RUN`
Inject: launcher/control communication ambiguity where existing evidence cannot prove outcome.
Assert: `UNKNOWN -> NEEDS_OPERATOR_RECONCILIATION`.
Forbidden: automatic duplicate launch merely to make progress.

### EXEC-06 Explicit resume lineage
Status: `PASS`
Evidence: [`2026-09-19 Genome-web TF P0 reference acceptance`](../validation/records/2026-09-19-genome-web-tf-p0.md).
Assert: automated resume is disabled until intended prior session identity can be bound reliably; implicit `last` is never treated as scientific identity.

### EXEC-07 Resume after tool failure
Status: `NOT_RUN`
Assert: failed attempt remains immutable; a new attempt may reuse compatible cache; reused and recomputed work are distinguishable.

### ENV-01 Compatible infrastructure retry retains RunSpec
Status: `NOT_RUN`
Setup: retry moves to a different compatible host/allocation while all result-affecting software/runtime controls satisfy the same environment/reproducibility contract.
Assert: same RunSpec, new RunAttempt; concrete host/allocation changes appear only in attempt provenance.

### ENV-02 Result-affecting runtime change creates new identity
Status: `NOT_RUN`
Setup: a runtime control declared result-affecting by ReproducibilityContract changes.
Assert: analysis identity changes or explicit impact/revalidation rule prevents silent reuse.

## 5. Data Identity and Provenance

### DATA-01 Resolved manifest/member provenance
Status: `PASS`
Evidence: [`2026-09-19 Genome-web TF P0 reference acceptance`](../validation/records/2026-09-19-genome-web-tf-p0.md).
Assert: exact resolved genome manifest/member identities consumed by Nextflow are registered/checkable independently of the original manifest path.

### DATA-02 Mutable collection URI cannot masquerade as same input
Status: `NOT_RUN`
Setup: logical URI unchanged; membership changes `{A,B}` -> `{A,B,C}`.
Assert: provider revision/manifest/member identity changes and therefore input/RunSpec identity changes.

### DATA-03 Annotation-release change propagates scientifically
Status: `NOT_RUN`
Assert: impact propagation reaches identifier mapping, selected/background membership, annotation coverage, and downstream enrichment where relevant.
Forbidden: assuming adaptive-slot changes are low scientific impact.

## 6. Validation and Publication

### VAL-01 Provider PASS is typed
Status: `NOT_RUN`
Assert: provider candidate verification becomes typed `provider_contract` / `artifact_integrity` evidence only; it does not set scientific/canonical/publication state.

### VAL-02 Generic PASS collapse is impossible
Status: `NOT_RUN`
Setup: artifact integrity passes while required provenance fails/inconclusive.
Assert: versioned ValidationProfile keeps the relevant gate closed.

### VAL-03 PASS_WITH_LIMITATIONS is gate-specific
Status: `NOT_RUN`
Assert: limitations remain attached and the exact profile/policy determines eligibility; no silent coercion to `PASS`.

### VAL-04 Corrupted candidate package
Status: `NOT_RUN`
Assert: RunAttempt may be `FINISHED` while validation fails; no canonical/publication gate opens.

### VAL-05 No implicit publication
Status: `NOT_RUN`
Assert: P0 candidate remains non-canonical/non-production until a distinct governed publication Decision/gate.

### VAL-06 ValidationProfile revision is historical
Status: `NOT_RUN`
Setup: candidate passed profile `candidate@v1`; later `candidate@v2` adds a stricter requirement.
Assert: historical v1 evaluation remains immutable; current applicability may require new reports/evaluation under v2; no historical rewrite.

## 7. Findings

### FIND-01 Validation does not automatically create a Finding
Status: `NOT_RUN`
Assert: artifact/technical validation can pass with no biological claim created.

### FIND-02 Finding is evidence-linked and scoped
Status: `NOT_RUN`
Assert: any recorded Finding carries claim, scope, evidence refs, limitations, status, and historical provenance; it does not become canonical or ResearchMemory merely by existing.

### FIND-03 Null/negative Finding is valid
Status: `NOT_RUN`
Assert: evidence can support a null/negative/inconclusive Finding without being scored as pipeline failure.

## 8. Change Impact and Memory Reactivation

### MEM-01 Bulk pathway reactivated for single-cell data
Status: `NOT_RUN`
Assert: procedural components/pitfalls may be recalled, but experimental unit, statistical model, gene-set generation, old DEG evidence, ID/background assumptions, and enrichment applicability are independently re-evaluated.
Forbidden: "unchanged downstream topology" as sufficient reuse evidence.

### MEM-02 Dormant but valid pathway
Status: `NOT_RUN`
Assert: activation may change without silently changing maturity/scope; dormancy is not deprecation.

## 9. Memory Promotion and Evidence Independence

### PROM-01 Repeated runs on one experiment remain correlated evidence
Status: `NOT_RUN`
Assert: execution count increases without pretending independent dataset/study support increased.

### PROM-02 Fatal contradiction overrides frequency
Status: `NOT_RUN`
Assert: pathway becomes contradicted/blocked pending review and the contradiction enters mandatory relevant context.

### PROM-03 Project-stable does not imply method-wide
Status: `NOT_RUN`
Assert: METHOD/LAB scope requires independent cross-context evidence plus governed promotion.

### PROM-04 Memory cannot directly become Policy or Finding
Status: `NOT_RUN`
Assert: memory can affect warnings, assessment, experiments, or configuration proposals; Policy/Finding/Canonical state requires the corresponding typed governed operation.

## 10. Retrieval and Content Trust

### CTX-01 Exact ID bypasses unnecessary hierarchy traversal
Status: `NOT_RUN`
Assert: exact authoritative lookup is attempted before optional semantic/hierarchical expansion.

### CTX-02 Mandatory constraints do not compete in top-k
Status: `NOT_RUN`
Assert: applicable hard policy and critical contradictions/retractions load deterministically; optional memories rank separately.

### SEC-01 External scientific content cannot mutate control state
Status: `NOT_RUN`
Assert: literature/tool/provider/model text remains source-tagged data/evidence and cannot create Policy, approval, command invocation, or canonical mutation by itself.

## 11. Reproducibility and Reuse

### REP-01 Seeded stochastic reproducibility
Status: `NOT_RUN`
Assert: rerun is judged against declared result-equivalence/tolerance, not assumed byte identity.

### REP-02 Unknown nondeterminism remains explicit
Status: `NOT_RUN`
Assert: weaker/nonreplayable class is recorded; no fabricated seed/deterministic guarantee.

### CACHE-01 IQ-TREE-only result-affecting change
Status: `NOT_RUN`
Assert: new RunSpec; compatible MAFFT output may be reused; tree/downstream validation rerun; old tree is not relabelled.

### CACHE-02 Protein-set change affecting one family
Status: `NOT_RUN`
Assert: new RunSpec; only demonstrated-equivalent cached outputs may be reused; affected family and whole candidate package are recomputed/revalidated with lineage.

## 12. Canonical State

### CANON-01 Concurrent canonical promotions use compare-and-swap
Status: `NOT_RUN`
Setup: two callers read pointer revision 17; first writes revision 18.
Assert: second update using expected revision 17 is rejected as stale; last-writer-wins is forbidden.

## 13. Architecture-Evidence Maintenance

### EVID-01 Rolling source records inspection provenance
Status: `NOT_RUN`
Assert: rolling docs/repositories record check date and revision/version when available, inspection depth, bounded claim scope, and explicit non-inferences.

## 14. Current Summary

```text
fresh PASS = TF-01, TF-02, EXEC-01, EXEC-06, DATA-01
all remaining runtime/scientific acceptance scenarios = NOT_RUN
```

The five PASS entries are bounded to the pinned Genome-web reference implementation/provider revisions and evidence record linked above. No correctness claim is made for scenarios that remain `NOT_RUN`.