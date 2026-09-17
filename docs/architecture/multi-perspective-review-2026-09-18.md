# BioHarness Multi-Perspective Architecture Review — 2026-09-18

Date: 2026-09-18
Status: Review record / non-authoritative rationale
Runtime status: NOT_IMPLEMENTED
Validation status: NOT_RUN

> This file records why the authoritative contracts were tightened. Final semantics live in `scientific-contracts-and-run-semantics.md`, `p0-genome-web-tf-vertical-slice.md`, and `scenario-validation-plan.md`. This review never participates in precedence resolution.

## Review Lenses

1. software architecture/domain boundaries;
2. scientific/statistical validity;
3. AI/research-memory semantics;
4. workflow execution/retry/recovery;
5. data identity/provenance/reproducibility;
6. security/authorization/governance;
7. laboratory use/evaluation;
8. documentation maintainability/YAGNI.

## Findings Retained for Audit

| ID | Severity | Finding | Integrated resolution |
|---|---:|---|---|
| R1 | CRITICAL | Historical policy snapshot could be mistaken for current authority. | Re-authorize every new side effect; preserve historical decision only as evidence. |
| R2 | CRITICAL | Submission identity was conflated with RunSpec identity. | RunSpec = analysis identity; RunAttempt = submission identity. |
| R3 | CRITICAL | Pre-execution `SUPPORTED` could imply hypothesis support. | Use `ANALYSIS_SUPPORTED*`; post-run scientific claims belong to Findings. |
| R4 | IMPORTANT | TaskSpec contained provider defaults. | Scientific intent stays in TaskSpec; method/provider choices live in ResolvedConfiguration. |
| R5 | IMPORTANT | Generic validation PASS collapsed multiple claims. | Typed ValidationReports + ValidationProfiles. |
| R6 | IMPORTANT | Reproducibility equivalence was underspecified. | Explicit ReproducibilityContract. |
| R7 | IMPORTANT | Open-world text could be mistaken for control instructions. | External/retrieved content is data/evidence, not authority. |
| R8 | IMPORTANT | Canonical updates could race. | Revision-checked atomic compare-and-swap. |
| R9 | IMPORTANT | Composite dataset identity lacked member-set identity. | Manifest/member identity in ResolvedDataRef. |
| R10 | IMPORTANT | Rolling evidence sources lacked inspection provenance. | Record check time/revision/inspection depth/claim scope. |
| R11 | MINOR | Engine-internal retries could be confused with BioHarness retries. | Engine retry stays inside one RunAttempt; new external launch creates a new RunAttempt. |
| R12 | MINOR | “validated candidate” could imply universal scientific acceptance. | Validation language is typed/profile-scoped. |

## Central Design Retained

The review did not reject the headless Research Control Plane, provider/adapter architecture, Genome-web as the first Data Provider, external Nextflow/Snakemake workflows, immutable historical evidence, evidence-linked Research Memory, memory activation/maturity/scope separation, deterministic mandatory context plus optional associative/graph recall, dormancy rather than destructive forgetting, or real-workflow-first vertical slicing.

## Documentation Optimization

Because all corrections were still in one unmerged PR, same-PR ADR layering was unnecessary. The accepted optimization was:

```text
review finding
    -> integrate final rule into authoritative contract
    -> retain review only as rationale/audit history
```

## Authority Mapping

- scientific/run/execution contracts -> `scientific-contracts-and-run-semantics.md`;
- first provider slice -> `p0-genome-web-tf-vertical-slice.md`;
- executable scenarios -> `scenario-validation-plan.md`;
- memory semantics -> existing memory architecture records;
- evidence -> `evidence-register-2026-09-17.md`.

## Status

```text
review_record = COMPLETED
final_rules_integrated = DESIGNED
runtime_implementation = NOT_IMPLEMENTED
runtime_validation = NOT_RUN
```
