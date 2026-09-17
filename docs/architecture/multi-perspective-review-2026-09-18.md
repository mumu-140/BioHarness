# BioHarness Multi-Perspective Architecture Review — 2026-09-18

Date: 2026-09-18
Status: Review record / non-authoritative rationale
Runtime status: NOT_IMPLEMENTED
Validation status: NOT_RUN

> This file records how the 2026-09-18 review was performed and why the authoritative contracts were tightened. Final semantics are integrated into `scientific-contracts-and-run-semantics.md`, `p0-genome-web-tf-vertical-slice.md`, and `scenario-validation-plan.md`. Future implementations should not treat this review as an additional precedence layer.

## 1. Review Scope

PR #1 and the pre-existing architecture were examined through seven deliberately separate lenses:

1. software architecture/domain boundaries;
2. scientific and statistical validity;
3. AI/research-memory semantics;
4. workflow execution/retry/recovery;
5. data identity/provenance/reproducibility;
6. security/authorization/governance;
7. real laboratory use/evaluation.

An additional maintainability/YAGNI pass checked whether the documentation itself was creating unnecessary precedence layers.

## 2. Review Outcome

The review did **not** reject the central design:

- headless Research Control Plane;
- provider/adapter architecture;
- Genome-web as first biological Data Provider;
- Nextflow/Snakemake retained as external workflow engines;
- immutable historical evidence;
- evidence-linked Research Memory;
- separation of memory activation, maturity, and scope;
- deterministic mandatory context plus optional associative/graph recall;
- dormancy rather than destructive forgetting;
- no mandatory graph database in V1;
- first vertical slice based on a real existing workflow.

It did identify ambiguities that needed consolidation before implementation.

## 3. Findings Retained for Audit

| ID | Lens | Severity | Finding | Integrated resolution |
|---|---|---:|---|---|
| R1 | security | CRITICAL | Historical ContextSnapshot/PolicyDecision could be misread as current authority. | Current authorization is required for every new side effect; historical decision remains reproducibility evidence. |
| R2 | execution | CRITICAL | External idempotency identity was shown on RunSpec rather than concrete attempt. | RunSpec carries analysis identity; RunAttempt carries submission identity/key. |
| R3 | science | CRITICAL | Pre-execution `SUPPORTED` could be misread as hypothesis support. | ScientificAssessment now uses `ANALYSIS_SUPPORTED*` feasibility semantics; post-run claims belong to Findings. |
| R4 | architecture/science | IMPORTANT | TaskSpec included ordinary method defaults such as `min_seqs`. | Scientific intent remains in TaskSpec; workflow parameters move to ResolvedConfiguration unless explicitly part of the question. |
| R5 | validation | IMPORTANT | One generic PASS could collapse integrity, QC, provenance, and publication readiness. | Typed ValidationReports + gate-specific ValidationProfiles. |
| R6 | reproducibility | IMPORTANT | Version/seed recording did not state expected equivalence level. | ReproducibilityContract defines determinism class and result equivalence. |
| R7 | AI/security | IMPORTANT | Open-world text could be mistaken for control instruction. | External/retrieved content is evidence/data, never control-plane authority by itself. |
| R8 | governance | IMPORTANT | Canonical promotion could race. | CanonicalPointer update uses expected-revision atomic compare-and-swap. |
| R9 | provenance | IMPORTANT | Composite dataset identity needed member-set identity. | ResolvedDataRef supports manifest/member identity/digests. |
| R10 | evidence | IMPORTANT | Rolling docs/repositories lacked inspection provenance. | Evidence records should preserve check time, revision/version/date, and inspection depth when practical. |
| R11 | execution | MINOR | Workflow-engine internal retry and BioHarness attempt retry were conflated. | Engine retries remain inside one RunAttempt; new BioHarness launch/binding creates a new RunAttempt. |
| R12 | terminology | MINOR | “validated candidate” could imply full scientific acceptance. | Validation is always typed/profile-scoped. |

## 4. Why These Findings Matter

### 4.1 Scientific feasibility is not scientific conclusion

An identifiable RNA-seq design can justify running differential expression without implying that a treatment effect will be detected. This distinction prevents the control plane from turning “analysis is valid to perform” into “hypothesis is supported.”

### 4.2 Authorization is time-dependent

A RunSpec can preserve the policy decision that existed when it was created while a later submission is denied under a newer policy. This keeps history reproducible without letting stale permission act as a capability token.

### 4.3 Execution identity has two levels

The analysis itself can remain the same while infrastructure execution is retried. Therefore stable analysis identity and concrete submission identity cannot be the same object.

### 4.4 Validation is multidimensional

Artifact integrity, provider-contract compliance, scientific assumptions, provenance completeness, reproducibility, and publication readiness are different claims. A provider PASS must not silently satisfy all of them.

### 4.5 Memory/retrieval is not authority

Literature, web content, memory, model output, and tool output can inform reasoning, but only typed authorized control-plane actions may mutate governed state.

## 5. Documentation-Maintainability Finding

During the review, corrective rules initially accumulated as successive ADR-style overrides within the same unmerged PR.

That pattern is useful after released decisions have historical users, but it is unnecessary inside one draft change set because Git already preserves review history.

The accepted optimization is therefore:

```text
review finding
    -> integrate final rule into authoritative contract
    -> keep review file only as rationale/audit history
```

Future agents should read the authoritative files first and consult this record only when they need the design rationale.

## 6. Current Authority Mapping

Authoritative final semantics:

- scientific/run/execution contracts -> `scientific-contracts-and-run-semantics.md`;
- actual first provider slice -> `p0-genome-web-tf-vertical-slice.md`;
- executable acceptance scenarios -> `scenario-validation-plan.md`;
- memory-specific architecture -> the existing memory architecture records;
- evidence sources -> `evidence-register-2026-09-17.md`.

This review file does not override those documents.

## 7. Status

```text
review_record = COMPLETED
final_rules_integrated = DESIGNED
runtime_implementation = NOT_IMPLEMENTED
runtime_validation = NOT_RUN
```
