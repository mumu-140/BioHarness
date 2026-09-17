# BioHarness Multi-Perspective Architecture Review — 2026-09-18

Date: 2026-09-18
Status: Review record / non-authoritative rationale
Runtime status: NOT_IMPLEMENTED
Validation status: NOT_RUN

> This file records why authoritative contracts were tightened. Final semantics live in the core architecture, `scientific-contracts-and-run-semantics.md`, `p0-genome-web-tf-vertical-slice.md`, memory architecture records, and `scenario-validation-plan.md`. This review never participates in precedence resolution.

## Review Lenses

1. software architecture/domain boundaries;
2. scientific/statistical validity;
3. AI/research-memory semantics;
4. workflow execution/retry/recovery;
5. data identity/provenance/reproducibility;
6. security/authorization/governance;
7. laboratory use/evaluation;
8. documentation maintainability/YAGNI.

## First-Pass Findings Retained for Audit

| ID | Severity | Finding | Integrated resolution |
|---|---:|---|---|
| R1 | CRITICAL | Historical policy snapshot could be mistaken for current authority. | Current authorization for new governed actions; historical decision only as evidence. |
| R2 | CRITICAL | Submission identity was conflated with RunSpec identity. | RunSpec = intended-work identity; RunAttempt = concrete submission/binding. |
| R3 | CRITICAL | Pre-execution `SUPPORTED` could imply hypothesis support. | `ANALYSIS_SUPPORTED*`; post-run claims belong to Findings. |
| R4 | IMPORTANT | TaskSpec contained provider defaults. | Intent stays in TaskSpec; method/provider choices in ResolvedConfiguration. |
| R5 | IMPORTANT | Generic validation PASS collapsed multiple claims. | Typed ValidationReports + ValidationProfiles. |
| R6 | IMPORTANT | Reproducibility equivalence was underspecified. | Explicit ReproducibilityContract. |
| R7 | IMPORTANT | Open-world text could be mistaken for control instructions. | External/retrieved content is data/evidence, not authority. |
| R8 | IMPORTANT | Canonical updates could race. | Revision-checked atomic compare-and-swap. |
| R9 | IMPORTANT | Composite dataset identity lacked member-set identity. | Manifest/member identity in ResolvedDataRef. |
| R10 | IMPORTANT | Rolling evidence sources lacked inspection provenance. | Check time/revision/inspection depth/claim scope. |
| R11 | MINOR | Engine-internal retries could be confused with BioHarness retries. | Engine retry stays inside one RunAttempt; new external launch creates a new RunAttempt. |
| R12 | MINOR | “validated candidate” could imply universal scientific acceptance. | Validation language is typed/profile-scoped. |

## Second-Pass Fresh Review Findings

The second pass reviewed the already-consolidated documents as implementation specifications, not as edits to defend.

| ID | Severity | Finding | Integrated resolution |
|---|---:|---|---|
| R13 | CRITICAL | Authorization was still visually positioned mainly at launch, allowing protected reads/resolution to appear pre-authorized. | Authorization is action/resource-scoped; protected reads/resolution are checked before access where policy applies. |
| R14 | IMPORTANT | ScientificAssessment preceded exact configuration although feasibility can depend on selected method/configuration assumptions. | Assessment binds explicit candidate method/data dependencies; assumption-relevant configuration changes force reassessment/revalidation before executable RunSpec. |
| R15 | IMPORTANT | RunSpec environment/resource fields could accidentally make infrastructure retries look like new scientific analyses. | RunSpec stores result-affecting environment contract; RunAttempt stores concrete host/allocation; ReproducibilityContract decides which runtime controls enter analysis identity. |
| R16 | IMPORTANT | `Finding` was used as a boundary concept but lacked a minimum contract. | Added evidence-linked scoped Finding contract distinct from Artifact/Validation/Decision/Memory/Canonical state. |
| R17 | IMPORTANT | ValidationProfile evolution could silently reinterpret historical PASS. | Profiles/gate evaluations are revisioned; historical evaluation remains immutable and current applicability may be re-evaluated separately. |
| R18 | IMPORTANT | Core spec still contained legacy monolithic Run lifecycle and mutable Artifact trust lifecycle. | Core spec now uses RunSpec/RunAttempt semantics and derives result designation from validation/Finding/Decision/CanonicalPointer rather than mutating Artifact content. |
| R19 | IMPORTANT | Memory docs retained stale examples suggesting adaptive-slot changes were low-impact or bulk->single-cell could reuse downstream evidence by topology. | Memory records now defer to dependency-aware ChangeImpact/compatibility; only demonstrated-compatible components/evidence are reused. |
| R20 | IMPORTANT | P0 source audit named a moving `main` branch and overused `limited/provider_specific` capability labels. | Pinned audited Genome-web commit `05072cbbcd533ca59afa13996d8d0edd8f939c6e`; current async ID/poll/cancel capabilities are stated explicitly, with limited reconciliation constraints. |
| R21 | MINOR | Validation document called itself an executable spec although no executable harness exists yet. | Renamed/defined as an acceptance-scenario catalog with mandatory fixture/action/assertion/evidence fields before a scenario can leave `NOT_RUN`. |

## Central Design Retained

Neither review pass rejected the headless Research Control Plane, provider/adapter architecture, Genome-web as the first Data Provider, external workflow engines, immutable historical evidence, evidence-linked ResearchMemory, memory activation/maturity/scope separation, deterministic mandatory context plus optional associative/graph recall, dormancy rather than destructive forgetting, or real-workflow-first vertical slicing.

## Documentation Optimization

Because corrections are still in one unmerged PR, accepted findings are integrated directly into authoritative records. Review/source-audit files retain only rationale/history.

```text
review finding
  -> integrate final rule into authoritative contract
  -> retain review only as non-authoritative audit history
```

## Status

```text
review_passes = 2
review_record = COMPLETED
final_rules_integrated = DESIGNED
runtime_implementation = NOT_IMPLEMENTED
runtime_validation = NOT_RUN
```