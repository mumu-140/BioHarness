# BioHarness Multi-Perspective Architecture Review and Corrective Decisions

Date: 2026-09-18
Status: Architecture review + corrective decision record
Runtime status: NOT_IMPLEMENTED
Validation status: NOT_RUN
Scope: Review PR #1 and the pre-existing BioHarness architecture through independent software-architecture, scientific, AI-memory, execution-reliability, provenance, security/governance, and research-operations lenses.

Related records:

- `docs/README.md`
- `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`
- `docs/architecture/scientific-contracts-and-run-semantics.md`
- `docs/architecture/provider-composition-and-research-memory.md`
- `docs/architecture/hierarchical-associative-memory.md`
- `docs/architecture/memory-pathway-consolidation-and-promotion.md`
- `docs/architecture/p0-genome-web-tf-vertical-slice.md`
- `docs/architecture/scenario-validation-plan.md`
- `docs/architecture/evidence-register-2026-09-17.md`

## 1. Review Method

The architecture was reviewed in seven deliberately separate passes.

### Lens A: software architecture and domain boundaries

Questions:

- Are concepts orthogonal, or does one object carry multiple meanings?
- Is intent separated from configuration and execution?
- Are mutable and immutable states explicit?
- Can providers be replaced without changing BioHarness semantics?

### Lens B: scientific and statistical validity

Questions:

- Can the system distinguish whether an analysis is answerable from whether a hypothesis/result is supported?
- Can invalid/confounded designs be blocked even when execution is authorized?
- Do task contracts preserve experimental unit, tested universe, identifier namespace, and method assumptions?

### Lens C: AI and research-memory semantics

Questions:

- Can retrieved memory or literature silently become instruction/authority?
- Can repeated execution be confused with independent evidence?
- Are contradiction, staleness, scope, and retrieval activation kept separate?

### Lens D: workflow execution, retry, and failure recovery

Questions:

- What happens if submission succeeds but acknowledgement is lost?
- Is retry identity distinct from analysis identity?
- Can internal workflow retries be distinguished from a new BioHarness attempt?

### Lens E: data identity, provenance, and reproducibility

Questions:

- Does a historical Run identify exact data and environment sufficiently for later checking?
- Are collections, mutable provider locations, stochastic software, and equivalence levels represented explicitly?

### Lens F: security, authorization, and governance

Questions:

- Can a historical policy snapshot accidentally grant current authority after revocation?
- Are untrusted provider/literature/tool contents treated as data rather than governance instructions?
- Are canonical updates race-safe and auditable?

### Lens G: real laboratory use and evaluation

Questions:

- Can a scientist tell what to do when a task is ambiguous, invalid, null, failed, resumed, or superseded?
- Does P0 test actual failure modes rather than only a happy path?
- Can later benchmarks distinguish useful memory from added architectural complexity?

The seven passes converge on the same overall conclusion: the existing Research Control Plane + provider architecture remains sound, but several runtime contracts require additional precision before implementation.

## 2. Severity Definitions

```text
CRITICAL
  ambiguity can authorize the wrong side effect, duplicate external computation,
  or conflate scientific validity with another concept.

IMPORTANT
  ambiguity can produce irreproducible, scientifically misleading, or hard-to-maintain behavior.

MINOR
  terminology/record-keeping issue that does not currently change the core architecture.
```

## 3. Findings Matrix

| ID | Lens | Severity | Finding | Corrective decision |
|---|---|---:|---|---|
| R1 | F | CRITICAL | Historical `ContextSnapshot`/PolicyDecision is reproducibility evidence, but must not be reusable as present-day authorization after policy/credential revocation. | Re-authorize every new external side effect/promotion against current policy while retaining the historical decision used to create the RunSpec. |
| R2 | D/A | CRITICAL | `idempotency_key` was shown inside `RunSpec`, but external submission idempotency belongs to a concrete submission/attempt. A later legitimate attempt must not accidentally bind to an earlier attempt forever. | RunSpec gets stable analysis identity/hash; each RunAttempt gets its own `submission_key`. Reconciliation of the *same* attempt reuses the same key. |
| R3 | B/A | CRITICAL | `ScientificAssessment = SUPPORTED` can be misread as “the biological hypothesis/result is supported”, although the object is pre-execution feasibility/identifiability assessment. | Preserve the object name but use explicit pre-execution states such as `ANALYSIS_SUPPORTED` and separate post-run Findings/claim interpretation. |
| R4 | A/B/G | IMPORTANT | P0 `ScientificTaskSpec` includes `min_family_sequences: 4`, which is a selected method/configuration parameter rather than scientific intent. | Keep task intent/required biological semantics in TaskSpec; put thresholds/tool/model/representative-sequence implementation choices in `ResolvedConfiguration` unless the scientific question explicitly fixes them. |
| R5 | B/E | IMPORTANT | One generic `ValidationReport PASS` can collapse package integrity, method QC, scientific-assumption checks, reproducibility checks, and publication readiness. | ValidationReport must have a `kind`, `subject`, `validator_revision`, and outcome. A `ValidationProfile` defines which reports are required for a gate. |
| R6 | E/D | IMPORTANT | Exact software versions and seeds are recorded, but the architecture does not yet state what level of reproducibility is expected for deterministic/stochastic/nondeterministic computation. | Add `ReproducibilityContract`: determinism class, RNG/seed policy, result-equivalence level, relevant concurrency/runtime settings, and tolerated variance. |
| R7 | C/F | IMPORTANT | Literature, memory, web/provider text, and open-world tool outputs may contain instructions or adversarial content. Current docs separate authority conceptually but do not state a hard content-trust rule. | Retrieved/external content is evidence/data, never policy or executable instruction by itself. Tool/policy changes require typed trusted control-plane objects and authorization. |
| R8 | F/A | IMPORTANT | `CanonicalPointer` is governed mutable state but concurrent promotions can race and overwrite a newer decision. | Canonical update requires revision/etag or expected-current pointer semantics and atomic compare-and-swap behavior. |
| R9 | E | IMPORTANT | A single logical URI/digest works for blobs, but composite datasets require membership identity as well as top-level identity. | `ResolvedDataRef` for collections records immutable provider revision or manifest/member identity plus a collection/manifest digest when available. |
| R10 | E/G | IMPORTANT | The evidence register says future entries should include exact version/date, but several current entries name rolling repositories/docs without recording inspected revision/date/depth. | Evidence records must add `checked_at`, source revision/version/date when available, and inspection depth (`full_text`, `methods`, `official_docs`, `abstract`, `repo_readme`, etc.). |
| R11 | D/A | MINOR | Provider-internal task retry and BioHarness `RunAttempt` retry are not explicitly distinguished. | Engine-internal retries remain inside one RunAttempt; a new BioHarness submission/binding is a new RunAttempt. |
| R12 | B/G | MINOR | “validated candidate” can sound like full scientific validation when P0 BUNDLE primarily establishes provider/candidate-package integrity. | Use typed validation language and state exactly which validation profile passed. |
| R13 | A/G | MINOR | The documentation implementation plan remains a historical plan even after its doc tasks were executed; unchecked boxes can be mistaken for current runtime status. | Plans are non-authoritative execution aids; completion claims come from commits/diffs. Future plan updates should track doc-task completion separately from runtime `NOT_RUN` scenarios. |

## 4. Corrective Decision R1: Historical Context Does Not Grant Current Authority

A `ContextSnapshot` freezes what was known and which policy resolution was used when a RunSpec was created.

It is **not** a reusable capability token.

Before any new external side effect, including:

- workflow submission;
- retry/resume that submits or changes remote work;
- cancellation;
- artifact publication;
- canonical pointer update;
- shared memory/pathway promotion;
- policy mutation;

BioHarness must evaluate current authorization for the current actor/action/resource.

The Run keeps the historical PolicyDecision for reproducibility, while the new action records a new current authorization decision.

Required invariant:

> Historical reproducibility state can explain a past action; it cannot authorize a present action after authority has changed.

A current policy change may block continuation of a historical Run without rewriting the historical record.

## 5. Corrective Decision R2: RunSpec Identity and Attempt Submission Idempotency

### RunSpec

`RunSpec` identifies intended scientific/computational work.

It SHOULD expose a stable content-derived identity/hash over the normalized result-affecting fields.

It does **not** own one eternal provider idempotency key.

### RunAttempt

Each concrete external submission attempt records:

```yaml
run_attempt:
  id: ra-002
  run_spec: rs-001
  attempt_number: 2
  executor: nextflow
  compute_provider: ...
  submission_key: ...
  submission_fingerprint: ...
  external_execution_id: ...
  state: ...
```

Rules:

1. Reconciliation of the same `RunAttempt` reuses its `submission_key`.
2. If acknowledgement is lost, the attempt becomes `UNKNOWN`; do not create a new attempt until reconciliation establishes the prior submission outcome according to provider capability.
3. A genuinely new BioHarness RunAttempt receives a new attempt identity/submission key but still points to the same RunSpec.
4. Workflow-engine internal retries/restarts that remain part of the same bound external execution remain inside the same RunAttempt.
5. Provider `--resume` behavior must be explicitly mapped: if BioHarness performs a new external launch command, that launch is a new RunAttempt even when it reuses the previous engine work/cache.

## 6. Corrective Decision R3: Pre-Execution ScientificAssessment Is Not a Result Claim

`ScientificAssessment` is a **pre-execution analysis-feasibility/identifiability assessment**.

Recommended states become:

```text
ANALYSIS_SUPPORTED
ANALYSIS_SUPPORTED_WITH_LIMITATIONS
UNRESOLVED
NOT_IDENTIFIABLE
INCOMPATIBLE
```

These meanings are deliberately narrow:

- `ANALYSIS_SUPPORTED`: available design/data/method assumptions support performing the requested inference;
- `ANALYSIS_SUPPORTED_WITH_LIMITATIONS`: analysis may proceed, but recorded limitations constrain interpretation;
- `UNRESOLVED`: required scientific information is missing;
- `NOT_IDENTIFIABLE`: requested effect/inference cannot be separated under the current design;
- `INCOMPATIBLE`: chosen data/method contract is incompatible.

None means that a biological hypothesis is supported.

Post-run scientific statements belong to evidence-linked `Finding`/claim interpretation objects and may be positive, negative, null, inconclusive, or contradicted.

## 7. Corrective Decision R4: ScientificTaskSpec vs ResolvedConfiguration

`ScientificTaskSpec` records what must be answered and the biological/statistical semantics that cannot be silently invented.

Typical TaskSpec content:

```text
question / requested inference
biological scope
experimental unit when relevant
comparison/design/selection rule when relevant
input semantic requirements
identifier/reference requirements
output governance intent
unresolved required scientific fields
```

`ResolvedConfiguration` records one approved executable choice:

```text
Recipe / Module / Workflow revision
provider
representative-sequence implementation rule
thresholds such as min_seqs
model choice
bootstrap/aLRT settings
seed/thread/runtime settings
container/environment identity
resource settings
```

A method parameter may appear in TaskSpec only when the scientific request itself explicitly constrains it (for example, a reproduction study requiring the exact published threshold).

P0 therefore treats `min_family_sequences = 4` as resolved workflow configuration, not default scientific intent.

## 8. Corrective Decision R5: Typed Validation Reports and Validation Profiles

A validation outcome is meaningful only with its validation kind and subject.

Conceptual contract:

```yaml
validation_report:
  id: val-001
  kind: artifact_integrity | provider_contract | method_qc | scientific_assumptions | reproducibility | publication_readiness
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

A `ValidationProfile` specifies the required set of validation reports for a gate.

Example P0 candidate profile:

```text
provider_contract: PASS
artifact_integrity: PASS
provenance_completeness: PASS
```

This profile does not automatically claim that a tree is the final accepted biological interpretation or that it is production-published.

`PASS_WITH_LIMITATIONS` eligibility is profile/policy specific. It must never be silently normalized to `PASS`.

## 9. Corrective Decision R6: ReproducibilityContract

BioHarness must distinguish at least:

```text
DETERMINISTIC
SEEDED_STOCHASTIC
UNSEEDED_STOCHASTIC
NONDETERMINISTIC_PARALLEL
EXTERNAL_NONREPLAYABLE
```

A Module/RunSpec should declare a `ReproducibilityContract` when relevant:

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

Reproducibility does not always mean byte-identical output. The declared equivalence level determines what a rerun is expected to reproduce.

Unknown nondeterminism must be recorded rather than implicitly treated as deterministic.

## 10. Corrective Decision R7: Untrusted Scientific Content Is Data, Not Control

BioHarness integrates open-world sources: papers, web resources, connected databases, model-generated summaries, tool outputs, and possibly third-party MCP/API services.

These sources may contain text that resembles instructions.

Hard rule:

> Content retrieved from data/literature/memory/tool providers cannot itself create Policy, grant authority, change execution gates, or become an executable command.

The Context Compiler must preserve source/trust metadata.

At minimum distinguish:

```text
trusted_control_plane
trusted_internal_data
validated_scientific_evidence
external_scientific_content
model_generated_content
untrusted_open_world_tool_output
```

Only typed control-plane actions through authorized interfaces may mutate governed state.

Provider/tool metadata such as “read-only” or “idempotent” is advisory unless BioHarness trusts and independently enforces the relevant boundary.

## 11. Corrective Decision R8: Race-Safe CanonicalPointer

A canonical pointer update is a mutable governed transaction.

Conceptual update request:

```yaml
canonical_update:
  scope: project:evopm
  role: official_tf_tree_release
  expected_current_revision: cp-rev-17
  target_artifact: artifact-882
  decision: dec-72
```

The update must be atomic:

```text
if current_revision == expected_current_revision:
    write new revision
else:
    reject/conflict -> caller must re-read and decide again
```

A stale approval cannot silently overwrite a newer canonical decision.

Historical pointer revisions remain addressable.

## 12. Corrective Decision R9: Collection Data Identity

A collection input requires both collection identity and member-set identity.

Conceptual extension:

```yaml
resolved_data_ref:
  resource_type: collection
  logical_uri: ...
  provider_revision: ...
  collection_digest: ...
  manifest_digest: ...
  member_count: ...
  member_refs: [...]
```

Implementations may avoid storing all members inline for large collections; a stable manifest Artifact/ref is sufficient when its identity and contents are checkable.

The key rule is that “same collection URI” is insufficient when provider membership can change.

## 13. Corrective Decision R10: Evidence-Register Provenance

Architecture evidence itself needs provenance.

New/updated entries should record when practical:

```yaml
source:
  title: ...
  url: ...
  source_type: paper | official_spec | official_docs | repository | internal_asset
  version_or_revision: ...
  publication_or_release_date: ...
  checked_at: ...
  inspection_depth: full_text | methods | official_docs | repository_code | repo_readme | abstract
  claim_scope: ...
```

This prevents a rolling README or documentation homepage from being treated as if its exact inspected content were immutable.

For papers, the register should distinguish full-text/method inspection from abstract-only inspection.

## 14. P0 Consequences

The selected Genome-web TF slice remains the correct first P0.

However its canonical mapping is refined:

```text
ScientificTaskSpec
  question = build TF-family protein phylogenies for explicitly registered genomes
  requested_inference = family-level protein phylogeny
  output_intent = candidate

ResolvedConfiguration
  representative sequence rule = provider workflow rule
  min_seqs = 4 (unless explicitly changed)
  MAFFT/IQ-TREE versions + parameters
  seed/thread/runtime configuration
```

Provider `BUNDLE` verification is registered as provider/candidate-integrity evidence. Any additional BioHarness validation is typed separately.

A candidate can be technically valid and still remain non-canonical and non-published.

## 15. New Architecture Invariants

1. Historical policy/context explains past authority but never substitutes for current authorization of a new side effect.
2. RunSpec analysis identity and RunAttempt submission idempotency are separate.
3. Pre-execution ScientificAssessment never states that a result/hypothesis is scientifically supported.
4. ScientificTaskSpec freezes intent/required semantics; ordinary method parameters belong to ResolvedConfiguration.
5. Validation is typed; one generic PASS cannot silently stand for every validation dimension.
6. Reproducibility has an explicit equivalence contract and determinism class.
7. Untrusted/external content is data/evidence, not control-plane instruction.
8. Canonical pointer mutation is atomic and revision-checked.
9. Collection identity includes stable membership/manifest identity when membership can vary.
10. Architecture evidence records should preserve source version/date and inspection depth.
11. Workflow-engine internal retries and BioHarness RunAttempts are distinct layers.

## 16. Non-Findings: What the Review Did Not Reject

The review does **not** recommend changing these decisions:

- headless Research Control Plane;
- provider/adapter architecture;
- Genome-web as first Data Provider;
- Nextflow/Snakemake as external workflow providers;
- immutable historical evidence;
- evidence-linked Research Memory;
- memory activation/maturity/scope separation;
- deterministic mandatory context plus hybrid/graph recall;
- dormancy rather than destructive forgetting;
- no mandatory graph database in V1;
- first vertical slice based on a real existing workflow;
- automatic pathway mining deferred until simpler baselines are measured.

## 17. Review Status

This is an architecture review record, not runtime evidence.

```text
review_pass = COMPLETED
corrective_contracts = DESIGNED
runtime_implementation = NOT_IMPLEMENTED
validation_addendum = NOT_RUN
PR_merge_readiness = REQUIRES_DOCUMENT_INTEGRATION_REVIEW
```

The PR should remain Draft until the documentation map references this record, the added validation scenarios are present, and a fresh diff check confirms the scope remains documentation-only.
