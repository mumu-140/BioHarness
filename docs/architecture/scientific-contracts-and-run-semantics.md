# BioHarness Scientific Contracts and Run Semantics

Date: 2026-09-18
Status: Authoritative design record
Runtime status: NOT_IMPLEMENTED
Validation status: NOT_RUN
Scope: Scientific intent, analysis feasibility, authorization, data identity, configuration, execution identity/recovery, validation, findings, provenance, reproducibility, canonical state, and context boundaries.

Related authoritative records:

- `docs/README.md`
- `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`
- `docs/architecture/p0-genome-web-tf-vertical-slice.md`
- `docs/architecture/scenario-validation-plan.md`

Memory-specific semantics remain in the memory architecture records. Review/audit records explain design history but do not override this contract.

## 1. Governing Model

BioHarness keeps seven questions separate:

1. **Scientific intent** — what question/inference is requested?
2. **Analysis feasibility** — can the design, data semantics, and method assumptions support performing it?
3. **Authorization** — may the current actor perform this protected action on these resources now?
4. **Configuration** — which exact data, method, result-affecting parameters, and environment contract will be used?
5. **Execution** — what concrete attempt ran, where, and what happened?
6. **Validation** — which properties of data, outputs, provenance, reproducibility, and assumptions were checked?
7. **Interpretation/publication** — what evidence-linked Finding or canonical state is justified?

No similarity score, memory rank, PolicyDecision, ValidationReport, or file-presence check answers all seven.

Canonical planning/execution flow:

```text
User / Agent Request
      |
      v
ScientificTaskSpec
      |
      +-------> authorized data/resource resolution as required
      |               |
      |               v
      |         ResolvedDataRef(s)
      |
      +-------> candidate Recipe/Module scientific contract
      |
      v
ScientificAssessment
      |
      v
ResolvedConfiguration
      |
      +-------> reassess if assumption-relevant configuration changed
      |
      v
ContextSnapshot + immutable RunSpec
      |
      v
current authorization for external launch
      |
      v
RunAttempt(s) -> RunEvent(s) -> Artifact(s)
      |
      v
ValidationReport(s) + versioned ValidationProfile evaluation
      |
      v
Finding / Decision / CanonicalPointer / ResearchMemory
```

Authorization is **action-scoped**, not one gate used forever. Sensitive reads/resolution, submission, cancellation, publication, canonical mutation, shared-memory promotion, or other protected actions may each require a current PolicyDecision.

## 2. PolicyDecision: Current Authority, Not Scientific Truth

`PolicyDecision` answers:

> May this actor perform this action on these resources under the current policy state?

Stable outcomes:

```text
ALLOW
ALLOW_WITH_WARNING
REQUIRE_APPROVAL
DENY
```

A PolicyDecision records at least actor, action, resource/scope, policy revision(s), outcome, timestamp, and relevant approval/audit references.

Policy can govern access or actions. It cannot make an unidentifiable design identifiable, make incompatible data compatible, or strengthen a scientific claim.

### Historical versus current authorization

Historical ContextSnapshots and PolicyDecisions are immutable reproducibility evidence. They explain what was allowed at that time; they are not capability tokens.

A new protected action is checked against current policy even when it belongs to an old RunSpec. Policy/credential changes can therefore block continuation without rewriting history.

## 3. ScientificTaskSpec: Freeze Intent, Not Provider Defaults

A governed analysis starts from a structured `ScientificTaskSpec` containing the scientific question and required biological/statistical semantics.

Conceptual shape:

```yaml
scientific_task_spec:
  id: task-spec-001
  question: ...
  requested_inference: ...
  analysis_class: ...
  biological_scope:
    species_or_logical_resources: [...]
    required_assembly_or_annotation: ...
  experimental_unit: ...
  design_or_comparison: ...
  input_semantic_requirements: ...
  required_identifiers:
    namespace: ...
  output_intent: exploratory | candidate | official
  unresolved_fields: []
```

Not every analysis needs every field. Recipe/Module contracts declare required fields.

Ordinary implementation choices belong to `ResolvedConfiguration`, for example representative-sequence rules, thresholds, models, bootstrap settings, seeds, threads, containers, and resource settings. They enter TaskSpec only when the scientific request itself fixes them, such as an exact reproduction study.

Ambiguous scientific meaning remains unresolved rather than being filled with model-invented assumptions.

## 4. ResolvedDataRef: Versioned, Checkable Scientific Input

A logical URI alone does not prove that later resolution yields the same scientific input.

Conceptual single-resource identity:

```yaml
resolved_data_ref:
  provider: genome-web
  resource_type: proteome
  resource_id: ...
  logical_uri: ...
  provider_revision: ...
  content_sha256: ...
  schema_version: ...
  biological_identity:
    species_id: ...
    assembly: ...
    annotation_release: ...
    identifier_namespace: ...
  resolved_at: ...
  retrieval_state: available | external | unavailable
```

For mutable/composite collections, preserve member-set identity as well:

```yaml
resolved_data_ref:
  resource_type: collection
  logical_uri: ...
  provider_revision: ...
  collection_digest: ...
  manifest_digest: ...
  member_count: ...
  member_manifest_ref: ...
```

Large member lists may live in an immutable/checkable manifest. Missing identity information is explicit.

Protected data resolution/access is authorized before the access occurs where policy requires it. The resulting historical resolution and access decision can then be frozen into ContextSnapshot/RunSpec provenance.

## 5. Module Scientific Contract

A Module is an external capability behind a BioHarness-owned scientific contract:

```yaml
scientific_contract:
  revision: ...
  required_task_fields: [...]
  input_semantics: ...
  assumptions: [...]
  compatibility_checks: [...]
  invalidating_changes: [...]
  required_validation: [...]
  interpretation_limits: [...]
```

Examples:

- differential expression declares count/data semantics and design requirements;
- enrichment declares identifier namespace, tested/background universe, annotation source, and multiple-testing behavior;
- phylogeny declares representative-sequence assumptions and interpretation limits.

File type alone is not scientific validation.

## 6. ScientificAssessment: Pre-Execution Feasibility Only

`ScientificAssessment` answers whether the requested inference is supportable under an explicit evidence/dependency set. It must bind to:

- ScientificTaskSpec revision;
- relevant ResolvedDataRefs;
- candidate Recipe/Module scientific-contract revision(s);
- design/data observations used for the assessment;
- assumption-relevant configuration constraints known at assessment time.

States:

```text
ANALYSIS_SUPPORTED
ANALYSIS_SUPPORTED_WITH_LIMITATIONS
UNRESOLVED
NOT_IDENTIFIABLE
INCOMPATIBLE
```

These states never mean that a biological hypothesis is supported.

If later ResolvedConfiguration changes a parameter, method revision, input binding, or runtime control that participates in a scientific assumption/compatibility predicate, the assessment must be recomputed or explicitly revalidated before RunSpec is executable. A RunSpec therefore references an assessment whose dependency fingerprint matches the finalized configuration.

Examples:

- treatment perfectly confounded with batch -> `NOT_IDENTIFIABLE`;
- incompatible count semantics -> `INCOMPATIBLE`;
- valid analysis yielding no significant DEGs -> pre-execution assessment may remain `ANALYSIS_SUPPORTED`, while the later Finding is null/negative.

## 7. ResolvedConfiguration

`ResolvedConfiguration` records one executable choice that is compatible with the current ScientificAssessment. Configuration creation is not itself blanket authorization for later protected actions.

It may contain:

```text
Recipe / Module / Workflow revisions
provider and input bindings
result-affecting method parameters
representative-sequence rule
software/container/environment requirements
validation-profile revision
reproducibility contract
planned compute/resource controls
```

Project Decisions, validated defaults, compatibility constraints, resources, and approved adaptive pathway slots may influence configuration. Configuration cannot weaken or hide a failed ScientificAssessment.

## 8. ChangeImpactContract and Dependency-Aware Revalidation

Structural-versus-slot mutation is useful history, not a scientific impact model.

Version-sensitive/adaptive dependencies may declare:

```yaml
change_impact:
  subject: annotation_release
  compatibility_predicate: ...
  affects: [id_mapping, selected_gene_membership, enrichment_background]
  required_revalidation: [mapping_validation, enrichment_recompute]
```

Core rule:

> Revalidation scope follows scientific/data dependency impact, not mutation labels or unchanged graph topology.

Partial thaw is allowed only where compatibility is demonstrated.

## 9. RunSpec: Immutable Intended-Work Identity

`RunSpec` freezes the intended scientific/computational work, not one concrete machine execution.

```yaml
run_spec:
  id: rs-001
  analysis_hash: ...
  scientific_task_spec: ...
  scientific_assessment: ...
  historical_context_snapshot: ...
  resolved_configuration: ...
  workflow_revision: ...
  input_refs: [...]
  expected_outputs: [...]
  validation_profile_revision: ...
  reproducibility_contract: ...
  planned_environment_contract: ...
  created_at: ...
```

`analysis_hash` includes result-affecting scientific/computational identity. It excludes attempt-only facts such as timestamps, hostnames, scheduler job IDs, transient paths, or resource allocation details unless the ReproducibilityContract/ChangeImpactContract says they affect result equivalence.

A new RunSpec is required when result-affecting input, design, method/configuration, workflow revision, or environment contract changes. Infrastructure recovery on a compatible host can remain the same RunSpec.

RunSpec does not own one permanent external submission/idempotency key.

## 10. WorkflowExecutorCapabilitySnapshot

Every executor adapter declares revision-scoped capabilities; Core never assumes generic guarantees from a tool name.

```yaml
workflow_executor_capabilities:
  provider: ...
  provider_revision: ...
  submission:
    mode: synchronous_process | async_remote
    native_idempotency_key: true | false
    durable_external_execution_id: true | false | limited
  observation:
    poll: true | false | limited
    reconcile_after_disconnect: true | false | limited
    logs: true | false
    trace: true | false
  retry_resume:
    engine_resume: true | false
    explicit_resume_identity: true | false | limited
  cancellation:
    supported: true | false | limited
  compute:
    backend: local | slurm | ssh | kubernetes | other
  provenance:
    invocation_record: true | false
    source_hashes: true | false
    tool_fingerprints: true | false
    resolved_manifest_digest: true | false
  limitations: [...]
  evidence_refs: [...]
```

`limited` must be explained in `limitations` and tied to inspectable evidence. Unsupported capability remains explicit; Core does not fabricate exactly-once, polling, cancellation, or reconciliation semantics.

## 11. RunAttempt: One Concrete BioHarness Execution Binding

A `RunAttempt` records one concrete launch/binding for a RunSpec.

```yaml
run_attempt:
  id: ra-001
  run_spec: rs-001
  attempt_number: 1
  executor: ...
  compute_provider: ...
  capability_snapshot: ...
  submission_key: ...
  submission_fingerprint: ...
  external_execution_id: ...
  observed_runtime_environment: ...
  observed_resource_allocation: ...
  state: ...
  submitted_at: ...
  last_reconciled_at: ...
```

`submission_key` is attempt-scoped. Reconciliation of the same attempt reuses it; a genuinely new RunAttempt gets a new attempt/submission identity while pointing to the same RunSpec.

Workflow-engine internal retries that occur without a new BioHarness external launch remain provider provenance inside the same RunAttempt. A new BioHarness-issued resume launch is a new RunAttempt even when engine cache/work is reused.

Recommended lifecycle:

```text
DRAFT -> SUBMITTING -> QUEUED/RUNNING -> COLLECTING -> FINISHED
SUBMITTING/RUNNING -> UNKNOWN
UNKNOWN -> reconciled active/final state | NEEDS_OPERATOR_RECONCILIATION
QUEUED/RUNNING -> CANCELLING -> CANCELLED | UNKNOWN
any active state -> FAILED
```

`FINISHED` means execution ended sufficiently for collection; it does not mean validation or scientific interpretation passed.

## 12. Idempotency, Reconciliation, and Safe Uncertainty

Retry is not idempotency.

Before a protected external submission, record RunSpec, RunAttempt, capability snapshot, submission intent, request identity where supported, and the current PolicyDecision authorizing that submission.

If acknowledgement/connection is lost, move the attempt to `UNKNOWN` and reconcile only using capabilities/evidence the adapter actually exposes.

If the prior outcome cannot be established safely:

```text
UNKNOWN -> NEEDS_OPERATOR_RECONCILIATION
```

Blind duplicate submission is forbidden. Only after prior-attempt status is established according to provider semantics may a new RunAttempt be created/submitted.

## 13. RunEvent: Append-Only Execution Evidence

Examples:

```text
AttemptCreated
AuthorizationChecked
SubmissionRequested
ExternalExecutionBound
ExecutionStarted
ExecutionHeartbeat
EngineRetryObserved
ExecutionFailed
ExecutionFinished
ArtifactDiscovered
ArtifactRegistered
ValidationStarted
ValidationReported
ReconciliationRequired
```

A mutable read model may be derived from append-only events. A relational transaction/outbox model is sufficient initially; Kafka is not required.

## 14. Artifact, ValidationReport, and Versioned ValidationProfile

An `Artifact` is immutable produced/registered scientific output or execution evidence.

A `ValidationReport` is a typed assessment of a specific subject:

```yaml
validation_report:
  id: val-001
  kind: artifact_integrity | provider_contract | method_qc | scientific_assumptions | reproducibility | provenance_completeness | publication_readiness
  subject: {type: artifact | run_spec | run_attempt | package | finding, id: ...}
  validator: ...
  validator_revision: ...
  inputs: [...]
  outcome: PASS | PASS_WITH_LIMITATIONS | FAIL | INCONCLUSIVE
  limitations: [...]
  evidence: [...]
  created_at: ...
```

A `ValidationProfile` is versioned and declares which reports/outcomes are required for a particular gate. Every gate evaluation records:

```text
validation_profile_id + revision
report IDs/revisions used
outcome
evaluated_at
applicable policy/decision references
```

The RunSpec freezes the planned profile revision. Later validation rules may produce new reports/evaluations without rewriting historical acceptance.

A provider `PASS` cannot silently mean artifact integrity, scientific truth, provenance completeness, and publication readiness at once. `PASS_WITH_LIMITATIONS` is never silently coerced to `PASS`.

## 15. ReproducibilityContract

Supported classes include at least:

```text
DETERMINISTIC
SEEDED_STOCHASTIC
UNSEEDED_STOCHASTIC
NONDETERMINISTIC_PARALLEL
EXTERNAL_NONREPLAYABLE
```

```yaml
reproducibility:
  class: SEEDED_STOCHASTIC
  random_seed: 12345
  rng_algorithm: ...
  result_equivalence: exact_bytes | exact_structured_values | numerical_tolerance | semantic_qc
  result_affecting_runtime_controls: [...]
  tolerance: ...
```

The contract determines which runtime controls must enter RunSpec/analysis identity and which concrete execution details may vary between compatible RunAttempts.

Unknown nondeterminism is recorded explicitly rather than treated as deterministic.

## 16. Finding: Evidence-Linked Scientific Interpretation

A `Finding` is a scoped post-run scientific claim/interpretation supported by explicit evidence. It is not an Artifact, ValidationReport, Decision, Memory, or canonical publication state.

Minimal shape:

```yaml
finding:
  id: finding-001
  claim: ...
  scope: project | dataset | method | broader-reviewed-scope
  subject_refs: [...]
  evidence_refs: [artifact:..., validation:..., run_spec:...]
  limitations: [...]
  status: candidate | supported | contradicted | superseded | retracted
  created_at: ...
  supersedes: ...
```

A Finding may be positive, negative, null, inconclusive, or contradicted. Validation establishes specific checked properties; it does not automatically create a scientific claim. A Decision may select or act on Findings. ResearchMemory may later summarize/reuse a Finding under explicit scope/evidence rules.

## 17. CanonicalPointer: Governed, Mutable, Race-Safe

Large Artifacts remain immutable. Current preferred/canonical selection is a small governed pointer:

```yaml
canonical_pointer:
  scope: project:evopm
  role: official_tf_tree_release
  revision: cp-rev-18
  artifact: artifact-882
  decision: dec-72
```

Mutation uses expected-current compare-and-swap. A stale revision is rejected; caller must re-read/re-decide. Every new canonical mutation requires current authorization. Historical pointer revisions remain traceable.

## 18. Context Retrieval and Content Trust

Required constraints never compete in one semantic top-k list.

Use four channels:

1. **Mandatory deterministic context** — current applicable policy constraints, blocking Decisions, resource/version constraints, critical contradictions/retractions, selected project/run context.
2. **Exact lookup** — Gene ID, Run ID, Artifact ID, DOI/accession, workflow revision, provider URI.
3. **Hybrid associative recall** — keyword/vector retrieval filtered by scope/time/version/evidence.
4. **Graph/hierarchical expansion** — typed multi-hop relationships when needed.

Hierarchy is an organization/expansion strategy, not a mandatory retrieval path.

Retrieved literature, memory, provider/tool output, web content, or model-generated text is data/evidence, not control-plane authority. It cannot itself create Policy, grant access, change gates, or become an executable command. Only typed authorized control-plane actions mutate governed state.

## 19. Evidence Independence and Research Memory

Raw run count is not independent scientific support. Evidence summaries distinguish execution count from distinct input/dataset/experiment/study support and contradiction/validation diversity.

Repeated execution on one biological experiment remains correlated evidence. Memory/pathway scope promotion considers provenance correlation and independent support diversity.

Memory may influence assessment/configuration proposals but cannot silently become Policy, Finding, Decision, or Canonical state.

## 20. Negative and Null Results

BioHarness never optimizes for discovery count. Valid outcomes include no significant differential expression, no enriched term under the predefined test/background, no supported motif effect, insufficient evidence, or an unidentifiable design.

Threshold relaxation or parameter search merely to increase significant hits is not a success signal. Memory consolidation uses validity, QC, reproducibility, and evidence quality.

## 21. Historical Acceptance and Current Applicability

A historical Run preserves TaskSpec, data identity, assessment, configuration, ContextSnapshot, relevant authorization decisions, RunAttempts, validation evidence, and Findings available at the time.

Later reassessment/revalidation may differ because of corrected literature, new reference/annotation versions, discovered confounding, version incompatibility, contradiction, or improved validation. New evaluations do not rewrite historical records.

## 22. Relationship to Memory Records

Cross-cutting clarifications that constrain older memory records:

1. authority/configuration precedence is not a general scientific-truth ranking;
2. adaptive-slot mutation is not automatically low scientific impact;
3. unchanged graph topology does not prove unchanged downstream validity;
4. reactivation reuses components/evidence only where ChangeImpact/compatibility checks support it;
5. current authorization is evaluated independently of recalled historical policy context.

## 23. P0 Acceptance Boundary

P0 uses the existing Genome-web TF Nextflow pilot as one real WorkflowExecutor integration and must demonstrate:

- explicit registered biological scope plus resolved/checkable input identity;
- TaskSpec separate from provider defaults;
- assessment bound to explicit method/data dependencies;
- immutable RunSpec and separate concrete RunAttempts;
- revision-scoped capability declaration;
- action-scoped authorization for protected access/submission;
- typed/versioned validation;
- safe uncertainty handling without fabricated exactly-once guarantees;
- candidate-only output with no automatic production publication;
- one evidence-backed scoped MemoryCandidate affecting later context without becoming Policy.

P0 does not validate remote Slurm/SSH/Kubernetes or generic WES/TES behavior.

## 24. Architecture Invariants

1. Scientific intent, feasibility, authorization, configuration, execution, validation, Finding, and canonical publication are distinct.
2. Authorization is action/resource scoped and current; historical decisions explain but do not grant present authority.
3. ScientificAssessment is pre-execution feasibility tied to explicit data/method dependencies, never hypothesis support.
4. Provider/method defaults are configuration unless explicitly part of scientific intent.
5. Governed Runs resolve logical data references to checkable version/member identities.
6. Revalidation follows dependency impact rather than mutation labels or graph topology.
7. RunSpec identifies intended result-affecting work; RunAttempt identifies one concrete execution binding.
8. Reproducibility/impact contracts decide which runtime controls belong in analysis identity.
9. WorkflowExecutor guarantees are revision-scoped, evidence-backed, and capability-declared.
10. Safe uncertainty is preferable to blind duplicate execution.
11. Artifact, typed validation, Finding, Decision, Memory, and CanonicalPointer remain separate objects/roles.
12. Validation profiles are versioned; later gate rules do not rewrite historical acceptance.
13. Canonical mutation is currently authorized, revision-checked, and atomic.
14. Mandatory constraints do not depend on semantic top-k retrieval.
15. External/retrieved content is evidence/data, not control authority.
16. Repeated Runs do not automatically count as independent biological support.
17. Null/negative results can be valid scientific outcomes.
18. Historical acceptance and current applicability are separately preserved.

## 25. Status

```text
contract_status = DESIGNED
runtime_status = NOT_IMPLEMENTED
scenario_validation = NOT_RUN
```

No statement in this record is evidence that BioHarness runtime already enforces these contracts.