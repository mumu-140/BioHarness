# BioHarness Scientific Contracts and Run Semantics

Date: 2026-09-18
Status: Authoritative design record
Runtime status: NOT_IMPLEMENTED
Validation status: NOT_RUN
Scope: Scientific intent, analysis feasibility, authorization, data identity, configuration, execution identity/recovery, validation, provenance, reproducibility, canonical state, and context boundaries.

Related authoritative records:

- `docs/README.md`
- `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`
- `docs/architecture/p0-genome-web-tf-vertical-slice.md`
- `docs/architecture/scenario-validation-plan.md`

Memory-specific semantics remain in:

- `docs/architecture/provider-composition-and-research-memory.md`
- `docs/architecture/hierarchical-associative-memory.md`
- `docs/architecture/memory-pathway-consolidation-and-promotion.md`

Review/audit records explain why this contract was tightened; they do not override this file.

## 1. Governing Model

BioHarness must keep these questions separate:

1. **Scientific intent** — what question or inference is requested?
2. **Analysis feasibility** — can the available design, data, and method assumptions support performing that inference?
3. **Authorization** — may the current actor perform the requested side effect now?
4. **Configuration** — which exact data, method, parameters, environment, and provider will be used?
5. **Execution** — what concrete attempt ran, where, and what happened?
6. **Validation** — which properties of outputs/provenance/method assumptions were actually checked?
7. **Interpretation/publication** — what Finding or canonical state is justified after execution and validation?

No similarity score, memory rank, project Decision, validation PASS, or policy rule answers all seven.

Canonical sequence:

```text
User / Agent Request
      |
      v
ScientificTaskSpec
      |
      +-------> ResolvedDataRef(s)
      |
      v
ScientificAssessment
      |
      v
ResolvedConfiguration
      |
      v
ContextSnapshot + RunSpec
      |
      v
Current PolicyDecision for side effect
      |
      v
RunAttempt(s) -> RunEvent(s) -> Artifact(s)
      |
      v
ValidationReport(s) evaluated by ValidationProfile
      |
      v
Finding / Decision / CanonicalPointer / ResearchMemory
```

## 2. PolicyDecision: Current Authority, Not Scientific Truth

`PolicyDecision` answers:

> Is the current actor allowed to perform this action on these resources under current policy?

Stable outcomes:

```text
ALLOW
ALLOW_WITH_WARNING
REQUIRE_APPROVAL
DENY
```

Policy can govern actions. It cannot make an unidentifiable scientific design identifiable, make incompatible data compatible, or convert weak evidence into a stronger scientific claim.

### Historical versus current authorization

A historical `ContextSnapshot` and historical `PolicyDecision` are immutable reproducibility evidence. They explain why a past RunSpec or action was considered authorized at that time.

They are **not capability tokens**.

Before every new governed side effect, BioHarness evaluates current authorization for the current actor/action/resource. This includes:

- first workflow submission;
- a new external retry/resume launch;
- cancellation;
- artifact publication;
- canonical pointer mutation;
- shared memory/pathway promotion;
- policy mutation.

If policy or credentials changed after RunSpec creation, the new side effect may be blocked without rewriting historical state.

## 3. ScientificAssessment: Pre-Execution Feasibility Only

`ScientificAssessment` is a pre-execution assessment of whether the requested analysis/inference is supportable with the available design, data semantics, and selected method class.

Use these states:

```text
ANALYSIS_SUPPORTED
ANALYSIS_SUPPORTED_WITH_LIMITATIONS
UNRESOLVED
NOT_IDENTIFIABLE
INCOMPATIBLE
```

Meanings:

- `ANALYSIS_SUPPORTED`: current design/data/method assumptions support performing the requested inference;
- `ANALYSIS_SUPPORTED_WITH_LIMITATIONS`: analysis may proceed, but explicit limitations constrain interpretation;
- `UNRESOLVED`: required scientific information is missing;
- `NOT_IDENTIFIABLE`: the requested effect/inference cannot be separated under the current design;
- `INCOMPATIBLE`: chosen data semantics and method contract are incompatible.

These states do **not** state whether a biological hypothesis is supported.

Post-run scientific claims belong to evidence-linked `Finding`/interpretation objects and may be positive, negative, null, inconclusive, or contradicted.

Examples:

- treatment perfectly confounded with batch -> `NOT_IDENTIFIABLE`;
- normalized abundance passed to a count-based method whose contract requires count semantics -> `INCOMPATIBLE`;
- valid analysis yielding no significant DEGs -> pre-execution assessment can remain `ANALYSIS_SUPPORTED`; the post-run Finding may be null/negative.

## 4. ScientificTaskSpec: Freeze Intent Before Workflow Selection

A governed analysis starts from a structured `ScientificTaskSpec`.

The TaskSpec records the scientific question and required biological/statistical semantics, not ordinary implementation defaults.

Conceptual shape:

```yaml
scientific_task_spec:
  id: task-spec-001
  question: ...
  requested_inference: ...
  analysis_class: ...
  biological_scope:
    species: ...
    assembly: ...
    annotation_release: ...
  experimental_unit: ...
  design_or_comparison: ...
  input_semantic_requirements: ...
  required_identifiers:
    namespace: ...
  output_intent: exploratory | candidate | official
  unresolved_fields: []
```

Not every analysis uses every field. Recipe/Module contracts declare required fields.

Ordinary method parameters belong in `ResolvedConfiguration`, for example:

```text
representative-sequence implementation rule
min_seqs
model choice
bootstrap/aLRT settings
seed
threads
container/runtime
resource settings
```

A method parameter belongs in TaskSpec only when the scientific request itself fixes it, such as an exact reproduction study.

### Ambiguous request example

> "For this gene, get differential genes and do GO enrichment."

This could mean a perturbation experiment, a treatment comparison, a coexpression neighborhood, or interpretation of an already-defined DEG set.

BioHarness must resolve the scientific meaning before constructing an official DEG -> GO chain. It must not silently invent a comparison or substitute another analysis class.

## 5. ResolvedDataRef: Versioned and Checkable Scientific Input

A logical URI is not enough to prove that the same scientific input will be resolved later.

Conceptual single-object contract:

```yaml
resolved_data_ref:
  provider: genome-web
  resource_type: proteome
  resource_id: Paxg_84K_T2T
  logical_uri: genome-web://proteome/Paxg_84K_T2T
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

Missing identity information is explicit rather than guessed.

### Composite collections

For mutable or composite datasets, top-level identity must also preserve membership identity:

```yaml
resolved_data_ref:
  resource_type: collection
  logical_uri: ...
  provider_revision: ...
  collection_digest: ...
  manifest_digest: ...
  member_count: ...
  member_manifest_ref: artifact-or-provider-ref
```

Large member lists may live in an immutable/checkable manifest rather than inline.

Core rule:

> Same logical collection URI does not imply the same scientific input when membership can change.

For an official RunSpec, BioHarness must be able to answer which exact scientific input was consumed and how that identity can be checked again.

## 6. Module Scientific Contract

A Module remains an external capability behind a BioHarness contract.

Its scientific contract may declare:

```yaml
scientific_contract:
  required_task_fields: [...]
  input_semantics: ...
  assumptions: [...]
  compatibility_checks: [...]
  invalidating_changes: [...]
  required_validation: [...]
  interpretation_limits: [...]
```

Examples:

- differential expression declares supported count/data semantics and design requirements;
- enrichment declares identifier namespace, tested/background universe, annotation source, and multiple-testing behavior;
- phylogeny declares whether representative-sequence selection is internal or must be resolved upstream.

File type alone is not scientific validation.

## 7. ResolvedConfiguration

`ResolvedConfiguration` records one authorized, scientifically supportable executable choice.

It may contain:

```text
Recipe / Module / Workflow revision
provider
input bindings
representative-sequence implementation rule
thresholds / model parameters
seed / threads / runtime controls
container/environment identity
compute/resource settings
validation profile
reproducibility contract
```

It may be influenced by explicit project Decisions, validated method defaults, compatibility constraints, resources, and approved adaptive pathway slots.

It must not weaken or hide a failed ScientificAssessment.

## 8. ChangeImpactContract and Dependency-Aware Revalidation

Structural-versus-slot mutation remains useful as pathway history, but it is not a scientific impact model.

Each version-sensitive or adaptive dependency can declare:

```yaml
change_impact:
  subject: annotation_release
  compatibility_predicate: ...
  affects:
    - id_mapping
    - selected_gene_membership
    - enrichment_background
    - annotation_interpretation
  required_revalidation:
    - mapping_validation
    - enrichment_recompute
```

Core rule:

> Revalidation scope follows scientific/data dependency impact, not whether a change was labelled structural or an adaptive slot.

Partial thawing remains valid when compatibility is demonstrated.

Examples:

- bulk RNA-seq -> single-cell may reuse generic ID-mapping software but must re-evaluate experimental unit, statistical model, selected genes, and enrichment background;
- annotation v3 -> v4 may require remapping, background regeneration, coverage checks, and enrichment recomputation even if the executable is unchanged.

## 9. RunSpec: Immutable Analysis Identity

`RunSpec` identifies the intended scientific/computational work before execution.

Conceptual fields:

```yaml
run_spec:
  id: rs-001
  analysis_hash: content-derived-stable-identity
  scientific_task_spec: task-spec-001
  historical_context_snapshot: ctx-001
  resolved_configuration: cfg-001
  workflow_revision: ...
  input_refs: [...]
  normalized_parameters: {...}
  environment_identity: ...
  expected_outputs: [...]
  validation_profile: ...
  reproducibility_contract: ...
  created_at: ...
```

`RunSpec` does **not** own one permanent external submission/idempotency key.

Create a new RunSpec when result-affecting scientific/computational identity changes, including:

- input content/revision/membership;
- scientific design;
- result-affecting parameters;
- result-affecting workflow/module revision;
- relevant environment identity;
- configuration changes that alter computation.

A retry/recovery with unchanged intended computation can create another RunAttempt for the same RunSpec.

## 10. WorkflowExecutorCapabilitySnapshot

BioHarness Core must not assume every executor/provider supports the same execution, recovery, or idempotency behavior.

Each adapter declares a revision-scoped capability snapshot, for example:

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
    supported: true | false | provider_specific
  compute:
    backend: local | slurm | ssh | kubernetes | other
  provenance:
    invocation_record: true | false
    source_hashes: true | false
    tool_fingerprints: true | false
    resolved_manifest_digest: true | false
```

Rules:

1. adapters advertise only capabilities demonstrated by the concrete integration;
2. unsupported capability remains explicit;
3. Core does not fabricate exactly-once, remote lookup, or reconciliation semantics;
4. capability snapshots are tied to provider revision, not to an abstract tool name forever.

## 11. RunAttempt: One BioHarness Submission/Binding

`RunAttempt` records one concrete BioHarness attempt to realize a RunSpec.

Conceptual fields:

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
  state: ...
  submitted_at: ...
  last_reconciled_at: ...
```

`submission_key` is attempt-scoped. Reconciliation of the same attempt reuses the same key. A genuinely new RunAttempt receives a new key while still referring to the same RunSpec.

Workflow-engine internal retries that occur without a new BioHarness external submission remain inside the same RunAttempt and are recorded as provider provenance.

If BioHarness issues a new external launch, including a new provider resume launch, that is a new RunAttempt even if engine work/cache is reused.

Recommended lifecycle:

```text
DRAFT
  -> SUBMITTING
  -> QUEUED/RUNNING
  -> COLLECTING
  -> FINISHED

SUBMITTING/RUNNING -> UNKNOWN
UNKNOWN -> reconciled active/final state
UNKNOWN -> NEEDS_OPERATOR_RECONCILIATION
QUEUED/RUNNING -> CANCELLING -> CANCELLED | UNKNOWN
any active state -> FAILED
```

`FINISHED` means external computation completed sufficiently for collection. It does not mean validation or scientific interpretation passed.

## 12. Idempotency, Reconciliation, and Safe Uncertainty

Retry is not idempotency.

Before submission, record:

- RunSpec identity;
- RunAttempt identity;
- attempt-scoped submission key/request identity where supported;
- executor/provider capability snapshot;
- submission intent event;
- current PolicyDecision authorizing the side effect.

If acknowledgement/connection is lost, move the attempt to `UNKNOWN` and reconcile according to provider capability.

If the provider exposes durable external IDs/lookup, automatic reconciliation may be possible.

If the provider does not expose sufficient evidence, the safe state is:

```text
UNKNOWN -> NEEDS_OPERATOR_RECONCILIATION
```

not blind duplicate submission.

Only after the previous attempt outcome is established according to provider semantics may policy permit a new RunAttempt.

## 13. RunEvent: Append-Only Execution Evidence

Execution observations should be append-only where practical:

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

A mutable current-state read model may be derived from these events.

The first implementation may use a relational transaction/outbox model; Kafka is not required.

## 14. Artifact, ValidationReport, and ValidationProfile

An `Artifact` is an immutable produced or registered object.

A `ValidationReport` is a typed assessment of a specific subject:

```yaml
validation_report:
  id: val-001
  kind: artifact_integrity | provider_contract | method_qc | scientific_assumptions | reproducibility | provenance_completeness | publication_readiness
  subject:
    type: artifact | run_spec | run_attempt | package | finding
    id: ...
  validator: ...
  validator_revision: ...
  inputs: [...]
  outcome: PASS | PASS_WITH_LIMITATIONS | FAIL | INCONCLUSIVE
  limitations: [...]
  evidence: [...]
  created_at: ...
```

A `ValidationProfile` defines which typed reports are required for a particular gate.

Example candidate gate:

```text
provider_contract: PASS
artifact_integrity: PASS
provenance_completeness: PASS
```

A provider's `PASS` message cannot silently mean method QC, scientific truth, publication readiness, and provenance completeness at once.

`PASS_WITH_LIMITATIONS` remains distinct and is accepted only when that profile/policy explicitly permits it.

## 15. ReproducibilityContract

Exact software versions are necessary but not sufficient to define reproducibility.

Supported classes should include at least:

```text
DETERMINISTIC
SEEDED_STOCHASTIC
UNSEEDED_STOCHASTIC
NONDETERMINISTIC_PARALLEL
EXTERNAL_NONREPLAYABLE
```

Conceptual contract:

```yaml
reproducibility:
  class: SEEDED_STOCHASTIC
  random_seed: 12345
  rng_algorithm: ...
  result_equivalence: exact_bytes | exact_structured_values | numerical_tolerance | semantic_qc
  relevant_runtime_controls:
    threads: 4
    accelerator: null
  tolerance: ...
```

Reproducibility does not always mean byte-identical output. Validation uses the declared equivalence level.

Unknown nondeterminism is recorded explicitly rather than treated as deterministic.

## 16. CanonicalPointer: Governed, Mutable, and Race-Safe

Large scientific artifacts remain immutable. The current preferred/canonical result is represented by a small governed pointer.

Conceptual pointer:

```yaml
canonical_pointer:
  scope: project:evopm
  role: official_tf_tree_release
  revision: cp-rev-18
  artifact: artifact-882
  decision: dec-72
  updated_at: ...
```

Mutation uses expected-current compare-and-swap semantics:

```yaml
canonical_update:
  expected_current_revision: cp-rev-17
  target_artifact: artifact-882
  decision: dec-72
```

If the current revision is no longer 17, the mutation is rejected as stale and the caller must re-read/re-decide.

A new canonical mutation also requires current authorization. Historical pointer revisions remain traceable.

## 17. Context Retrieval and Content Trust

Required constraints must not compete inside one semantic top-k list.

Use four channels:

1. **Mandatory deterministic context** — current hard Policy, blocking Decisions, resource/version constraints, critical contradictions/retractions, selected project/run context.
2. **Exact lookup** — Gene ID, Run ID, Artifact ID, DOI/accession, workflow revision, provider URI.
3. **Hybrid associative recall** — keyword/vector retrieval filtered by scope/time/version/evidence.
4. **Graph/hierarchical expansion** — typed multi-hop relationships when needed.

Hierarchy is an organization/expansion strategy, not a mandatory retrieval path.

### External content is data, not control

BioHarness integrates literature, web resources, provider/tool output, memory, and model-generated content. Text from those sources may resemble instructions.

Hard rule:

> Retrieved/external content cannot itself create Policy, grant authority, change execution gates, or become an executable control-plane command.

Context must preserve source/trust metadata, distinguishing at least:

```text
trusted_control_plane
trusted_internal_data
validated_scientific_evidence
external_scientific_content
model_generated_content
untrusted_open_world_tool_output
```

Only typed authorized control-plane actions can mutate governed state.

## 18. Evidence Independence and Research Memory

Raw run count is not equivalent to independent scientific support.

Evidence summaries should distinguish:

```text
execution_count
successful_execution_count
distinct_input_identity_count
distinct_dataset_or_experiment_count
independent_study_or_project_count
validation_type_count
contradiction_count
```

Repeated execution on the same biological experiment remains correlated evidence.

Memory/pathway scope promotion must consider provenance correlation and independent support diversity.

Memory may influence assessment/configuration proposals, but cannot silently become Policy or Canonical state.

## 19. Negative and Null Results Are Valid Scientific Outcomes

BioHarness must not optimize for discovery count.

Valid outcomes include:

- no significant differential expression;
- no enriched term under the predefined test/background;
- no supported motif effect;
- insufficient evidence;
- current design not identifiable.

The system must not relax thresholds or search parameter space merely to increase significant hits.

Memory consolidation uses validity, QC, reproducibility, and evidence quality rather than number of discoveries as a success proxy.

## 20. Historical Acceptance and Current Applicability

A historical Run preserves the TaskSpec, data identity, assessment, configuration, ContextSnapshot, authorization, and validation available at the time.

Later reassessment may differ because of:

- corrected/retracted literature;
- new annotation/reference versions;
- discovered confounding;
- version incompatibility;
- new contradiction;
- improved validation.

BioHarness preserves both historical acceptance context and current applicability. New assessment does not rewrite the historical Run.

## 21. Relationship to Older Memory Records

Three clarifications apply to older architecture records:

1. the authority/configuration precedence ladder is not a general scientific-truth ranking;
2. adaptive-slot mutation may be low structural churn but is not automatically low scientific impact;
3. unchanged graph topology does not prove unchanged downstream scientific validity.

These clarifications are now part of this authoritative contract rather than an additional correction layer.

## 22. P0 Acceptance Boundary

P0 uses the existing Genome-web TF Nextflow pilot as one real WorkflowExecutor integration.

P0 must demonstrate:

- explicit registered biological identity;
- resolved input/member provenance;
- ScientificTaskSpec separate from method configuration;
- pre-execution ScientificAssessment;
- immutable RunSpec and separate RunAttempt;
- revision-scoped executor capability declaration;
- current authorization before launch;
- typed candidate/provenance validation;
- safe uncertainty handling without fabricated exactly-once guarantees;
- candidate-only output with no automatic production publication;
- one evidence-backed MemoryCandidate affecting later context without becoming Policy.

P0 does not validate remote Slurm/SSH/Kubernetes execution or generic WES/TES behavior.

## 23. Architecture Invariants

1. Scientific intent, analysis feasibility, current authorization, configuration, execution, validation, and interpretation are separate concepts.
2. Policy governs actions; it cannot make an invalid design valid.
3. Historical PolicyDecision/ContextSnapshot explains past authority but does not authorize new present-day side effects.
4. ScientificAssessment states analysis feasibility, never biological-hypothesis support.
5. Ordinary method parameters belong to ResolvedConfiguration unless explicitly part of the scientific question.
6. Governed Runs resolve logical references to versioned/checkable scientific input identities, including collection membership where relevant.
7. Revalidation follows dependency impact rather than mutation label or graph topology alone.
8. RunSpec identifies intended work; RunAttempt identifies one BioHarness external submission/binding.
9. Attempt-scoped submission identity and engine-internal retries are distinct lifecycle layers.
10. WorkflowExecutor guarantees are capability-declared and provider-revision scoped.
11. Uncertain execution may require operator reconciliation; blind duplicate submission is forbidden.
12. Artifact existence, validation outcome, scientific Finding, and canonical publication are independent.
13. Validation is typed and gate-specific through ValidationProfiles.
14. Reproducibility declares determinism/equivalence expectations explicitly.
15. Canonical pointer mutation is current-authorized, revision-checked, and atomic.
16. Mandatory policy/critical contradiction context does not depend on semantic top-k retrieval.
17. External/retrieved content is evidence/data, not control-plane authority.
18. Repeated Runs do not automatically count as independent biological support.
19. Null/negative results can be valid scientific outcomes.
20. Historical acceptance and current applicability are separately preserved.

## 24. Status

```text
contract_status = DESIGNED
runtime_status = NOT_IMPLEMENTED
scenario_validation = NOT_RUN
```

No statement in this record is evidence that the BioHarness runtime already enforces these contracts.
