# BioHarness P0 Runtime Kernel Design

Date: 2026-09-18
Status: APPROVED FOR IMPLEMENTATION PLANNING
Runtime status: NOT_IMPLEMENTED
Acceptance status: NOT_RUN
Branch: `design/p0-runtime-kernel`
Base: `main@56f3dd1362ed5c772a8062df6456bc21a53a7b80`

## 1. Purpose

P0 turns the existing BioHarness architecture contracts into the smallest real runtime that can govern one end-to-end scientific analysis. The audited Genome-web TF Nextflow pilot is the first **reference integration and acceptance case** used to exercise that runtime; it is not part of BioHarness Core.

The goal is not to build a generic agent platform, workflow engine, Web application, or scientific algorithm suite. The goal is to prove one authoritative research-control loop:

```text
ScientificTaskSpec
  -> authorized data resolution through a DataProvider
  -> ResolvedDataRef(s)
  -> ScientificAssessment
  -> ResolvedConfiguration
  -> ContextSnapshot
  -> immutable RunSpec
  -> current launch authorization
  -> RunAttempt / RunEvent
  -> WorkflowExecutor port
  -> external provider/workflow/tooling
  -> Artifact registration
  -> typed ValidationReport / ValidationProfile evaluation
  -> scoped evidence-backed MemoryCandidate
```

The first real acceptance case runs in an isolated BioHarness P0 environment on a server where the Genome-web TF pilot is already runnable. Genome-web source data are read-only. BioHarness uses its own PostgreSQL database and its own run root and does not write Genome-web production outputs.

A successful reference case proves that BioHarness can govern an external scientific system. It does not make that external system a BioHarness subsystem.

## 2. Authoritative Existing Contracts

This runtime design refines implementation mechanics but does not replace the existing authoritative architecture records:

- `docs/superpowers/specs/2026-09-17-bioharness-architecture-design.md`
- `docs/architecture/scientific-contracts-and-run-semantics.md`
- `docs/architecture/p0-genome-web-tf-vertical-slice.md`
- `docs/architecture/scenario-validation-plan.md`
- memory-specific records under `docs/architecture/`

If implementation details conflict with those contracts, the implementation detail must change unless the authoritative contract is explicitly revised through a separate design decision.

The first reference case is pinned to:

```text
repository: mumu-140/genome-web-backend
revision:   05072cbbcd533ca59afa13996d8d0edd8f939c6e
```

Those source observations support only the Genome-web TF reference adapter and its acceptance evidence. BioHarness Core must not hard-code that repository, revision, manifest schema, command line, Nextflow workflow, or provider capability set.

A reference adapter must refuse to silently inherit audited capability claims when configured against a different provider revision.

## 3. Chosen Architecture

P0 uses a Python modular monolith with ports/adapters and PostgreSQL as the authoritative control-plane store.

```text
                         Human / Agent Client
                    CLI now; SDK/MCP/API later
                                |
                                v
                     +---------------------+
                     |   Application Layer |
                     | plan/execute/...    |
                     +----------+----------+
                                |
                  +-------------+-------------+
                  |                           |
                  v                           v
           Domain / Contracts              Ports
                  |                DataProvider / WorkflowExecutor
                  |                           |
                  v                           v
             PostgreSQL               External adapters
                                      /             \
                               provider A        provider B
```

Core/domain code does not import Genome-web, Nextflow, PostgreSQL, Pi, DeepSeek Harness, or Web code. Concrete dependencies stay behind adapters.

P0 includes generic infrastructure adapters only where they are part of the control plane itself, such as PostgreSQL persistence, filesystem artifact access, and a generic local-process execution primitive. Scientific/provider-specific bindings are reference or external integrations, not Core.

P0 does not implement a dynamic plugin loader. Python protocols/interfaces are enough while there are few integrations. A plugin runtime is deferred until multiple independently distributed providers make dynamic composition operationally useful.

### 3.1 Reference-integration boundary

The Genome-web TF case follows four hard rules:

1. `validate_genomes.py`, `run.sh`, `run.py`, the Nextflow pipeline, MAFFT, IQ-TREE, and Genome-web schemas remain owned by Genome-web or their upstream projects.
2. BioHarness does not vendor or copy those scripts into `src/bioharness`.
3. The provider-specific adapter/configuration lives under a reference/example integration boundary and is not required to import or use BioHarness Core.
4. Removing the Genome-web reference integration must leave the BioHarness package, migrations, generic unit tests, and generic contract/integration tests functional.

The reference integration may translate BioHarness port contracts to external commands/files, but it cannot define Core semantics.

## 4. Relationship to Pi and DeepSeek Harness

Pi and DeepSeek Harness are treated as architectural references and future optional Agent Runtime clients, not as the BioHarness runtime base.

BioHarness and those projects solve different authority problems:

```text
Pi / DeepSeek Harness
  model -> agent loop -> tool calls -> session

BioHarness
  scientific intent -> feasibility -> governed run -> evidence -> validation -> finding/memory
```

The following patterns are intentionally adopted:

1. **Durable facts are separate from live runtime observations.** DeepSeek Harness distinguishes durable SessionEvents from live agent/capability events. BioHarness analogously persists scientific/execution facts as `RunEvent`s while transient process observations do not need to become durable events every second.
2. **Capabilities have explicit seams.** Pi/Chord and DeepSeek Harness demonstrate provider/consumer service boundaries. BioHarness implements the same architectural idea through Python ports/adapters in P0.
3. **Agent execution is interceptable, not authoritative.** Future agent clients may propose operations through BioHarness commands/tools, but they do not directly mutate scientific/canonical state or bypass authorization.
4. **Headless operation is primary.** The P0 control plane remains fully operable without an LLM or Web UI.

The following are explicitly not adopted in P0:

- Pi agent loop or session model as scientific authority;
- DeepSeek Harness/Cordis as application runtime;
- TypeScript/Node as the scientific control-plane implementation language;
- dynamic plugin hot reload;
- replicated UI state;
- agent session storage as the owner of RunSpec, Artifact, Validation, Finding, or ResearchMemory.

A future `bioharness-pi` extension or `bioharness-dsh-plugin` may expose BioHarness operations as guarded tools, while BioHarness remains authoritative.

## 5. Technology Baseline

P0 runtime uses:

```text
Python 3.12+
Pydantic 2               domain DTO validation / immutable snapshots
SQLAlchemy 2             persistence mapping and transactions
Alembic                  schema migrations
psycopg 3                PostgreSQL driver
PostgreSQL               authoritative control-plane state
Typer                    CLI
pytest                   unit/contract/integration tests
rfc8785                  RFC 8785 JSON canonicalization
stdlib subprocess/pathlib/hashlib/json
```

`rfc8785` is used rather than a custom canonical-JSON implementation. Hashing uses SHA-256 over explicit versioned projections.

No Celery, Temporal, Redis, Kafka, Neo4j, pgvector, FastAPI, HTTP client dependency, Slurm client, WES server, or generic DAG runtime is introduced in P0.

## 6. Repository Shape

The implementation should remain compact and organized by responsibility:

```text
BioHarness/
├── pyproject.toml
├── src/bioharness/
│   ├── domain/
│   │   ├── task.py
│   │   ├── data.py
│   │   ├── assessment.py
│   │   ├── policy.py
│   │   ├── run.py
│   │   ├── artifact.py
│   │   ├── validation.py
│   │   └── memory.py
│   ├── application/
│   │   ├── resolve_task.py
│   │   ├── plan_analysis.py
│   │   ├── execute_run.py
│   │   ├── reconcile_run.py
│   │   ├── collect_artifacts.py
│   │   └── validate_run.py
│   ├── ports/
│   │   ├── data_provider.py
│   │   ├── workflow_executor.py
│   │   ├── policy.py
│   │   └── repositories.py
│   ├── adapters/
│   │   ├── postgres/
│   │   ├── filesystem/
│   │   └── local_process/
│   ├── identity/
│   │   ├── canonical.py
│   │   └── projections.py
│   └── cli/
├── migrations/
├── examples/
│   └── reference_integrations/
│       └── genome_web_tf/
│           ├── data_adapter.py
│           ├── executor_adapter.py
│           └── README.md
└── tests/
    ├── unit/
    ├── contract/
    ├── integration/
    ├── reference/
    └── fixtures/
```

`examples/reference_integrations/**` is not part of the installed BioHarness Core package and may depend on the external provider repository/environment. Provider-specific scripts remain external and are invoked/referenced, not copied.

Files may be split further when a unit becomes hard to understand independently. P0 must not create generic framework abstractions that have only one speculative consumer.

## 7. Source of Truth and Persistence Model

PostgreSQL is authoritative for BioHarness control-plane state. Filesystem content is authoritative for artifact bytes and execution evidence stored under an isolated BioHarness run root, but control-plane identity, relationships, state transitions, validation, and governance are persisted in PostgreSQL.

This deliberately differs from Sapporo's current approach where run-directory files are master data and SQLite is a rebuildable index. BioHarness may reuse Sapporo's process/reconciliation patterns, but not that source-of-truth model.

P0 tables are intentionally narrow:

```text
projects
scientific_task_specs
policy_decisions
resolved_data_refs
scientific_assessments
resolved_configurations
context_snapshots
run_specs
run_attempts
run_events
artifacts
validation_profiles
validation_reports
validation_evaluations
memory_candidates
```

Large scientific manifests and artifact bodies stay as immutable files referenced by digest and URI/path. JSONB is used for typed snapshot payloads where normalization would add complexity without improving P0 integrity.

### 7.1 Immutability

The following records are append-only or revisioned rather than edited in place after publication:

- ScientificTaskSpec revision;
- PolicyDecision;
- ResolvedDataRef;
- ScientificAssessment;
- ResolvedConfiguration;
- ContextSnapshot;
- RunSpec;
- RunEvent;
- Artifact;
- ValidationReport;
- ValidationProfile revision;
- ValidationEvaluation;
- MemoryCandidate evidence snapshot.

`RunAttempt` has a mutable current-state projection for efficient inspection, but every meaningful transition also appends a `RunEvent`. Historical event rows are never rewritten.

### 7.2 Minimum database constraints

The relational schema must enforce the identities that protect execution semantics rather than relying only on application code:

```text
run_specs.run_spec_hash                         UNIQUE
run_attempts(run_spec_id, attempt_number)      UNIQUE
run_attempts.submission_key                    UNIQUE
run_attempts.provider_attempt_name             UNIQUE within one configured executor/run-root namespace
run_events(run_attempt_id, sequence_no)        UNIQUE
validation_profiles(profile_id, revision)      UNIQUE
```

`analysis_hash` is indexed but is not globally unique: two RunSpecs may intentionally share the same result-affecting analysis identity while preserving different control-plane context or validation plans.

A RunAttempt state transition and its corresponding durable RunEvent append occur in the same PostgreSQL transaction. Application repositories do not expose generic update/delete methods for immutable record types.

## 8. Domain Identity and Hashing

BioHarness uses two different hashes because scientific identity and whole-record integrity answer different questions.

### 8.1 `analysis_hash`

`analysis_hash` represents intended result-affecting work. It is computed from a versioned projection containing only result-affecting scientific/computational identity, for example:

```text
identity_projection_version
ScientificTaskSpec scientific semantics that affect the computation
resolved input/member content identities
workflow/provider source revision
result-affecting method parameters
result-affecting software/environment contract
reproducibility controls declared result-affecting
```

It excludes:

- timestamps;
- UUIDs used only as database identity;
- hostname;
- PID;
- scheduler/external job ID;
- transient paths;
- observed resource allocation unless declared result-affecting;
- ValidationProfile revision unless a validation choice itself affects produced scientific results;
- historical ContextSnapshot references that do not affect the intended computation.

### 8.2 `run_spec_hash`

`run_spec_hash` protects the complete immutable RunSpec snapshot, including control-plane fields not included in `analysis_hash`.

Both hashes use:

```text
SHA-256(RFC8785-canonical-json(versioned_projection))
```

All projections are explicit functions with a named schema/projection version. Adding or changing projection semantics requires a new projection version; it must not silently change hashes for historical records.

## 9. Data Resolution Port and Genome-web Reference Case

BioHarness Core owns a generic `DataProvider` contract. It does not know Genome-web manifest columns, biological table layouts, or `validate_genomes.py`.

A DataProvider implementation is responsible for translating a requested logical scientific resource into a checkable provider result. BioHarness then records the resolved identity and, where configured, independently computes/checks content identities required by its reproducibility contract.

Generic planning flow:

```text
requested logical scientific resources
  -> current read authorization where required
  -> DataProvider.resolve(...)
  -> provider result + provider evidence
  -> BioHarness identity checks/digests required by contract
  -> persist ResolvedDataRef(s)
```

### 9.1 Genome-web reference adapter

The first reference adapter invokes the audited external provider resolver `pipeline/nextflow/scripts/validate_genomes.py`. That script remains part of Genome-web, not BioHarness.

For the reference TF case, the adapter maps the provider result into identities including:

```text
species_id
uid (string, five digits preserved)
genome_build
annotation_release
release_id
gene_tsv identity + SHA-256
transcript_tsv identity + SHA-256
protein_tsv identity + SHA-256
protein_fasta identity + SHA-256
tf_tsv identity + SHA-256
tf_gene_tsv identity + SHA-256
resolved-manifest SHA-256
provider revision
```

The user-supplied/original manifest digest is retained separately from the provider-resolved manifest digest.

These fields are **reference-adapter semantics**, not mandatory fields of every future `DataProvider`.

Immediately before external launch, BioHarness performs a fresh check of the frozen input identities required by the RunSpec outside the database lock/transaction. If a result-affecting member changed, the existing RunSpec is not submitted. The task must be re-resolved/replanned into a new scientific identity.

The live Genome-web reference environment treats the configured release inputs as read-only for the duration of a run. If another provider cannot guarantee an equivalent operational property, its adapter must stage or otherwise bind an immutable input snapshot before claiming equivalent semantics.

The reference provider performs its own validation again at execution time. The reference adapter compares the provider-resolved execution inputs against the frozen planned identity and rechecks required member digests during collection. A mismatch is a provenance/identity validation failure, not a warning that may be ignored.

## 10. Scientific Assessment Boundary

Provider/data preflight and scientific assessment remain distinct.

Provider resolution establishes provider facts. `ScientificAssessment` consumes those facts plus the selected Module/Workflow scientific contract and decides whether the requested analysis is supportable.

For P0, assessment is deterministic application/domain logic, not an LLM judgment.

The Genome-web TF reference case includes checks such as provider identity consistency and candidate-only limitations, but those checks do not become universal BioHarness scientific rules.

The assessment stores a dependency fingerprint over the exact TaskSpec revision, ResolvedDataRefs, scientific-contract revision, and assumption-relevant constraints. Final ResolvedConfiguration must match or explicitly refresh that dependency fingerprint before a RunSpec becomes executable.

## 11. Minimal Policy and Authorization Runtime

P0 needs real action-scoped authorization semantics even though it does not yet need a general organization policy engine.

The domain exposes a `PolicyEvaluator` port. The initial runtime adapter evaluates explicit local P0 rules such as:

- actor identity is present;
- configured provider source roots are read-only inputs when policy requires that property;
- BioHarness writes only under configured allowed run/artifact roots;
- configured protected/production roots are denied;
- production publication/canonical mutation is denied in P0;
- policy revision is explicit and persisted.

Provider-specific policies may add stricter constraints in a reference/external integration without changing the Core policy model.

Every authorization decision is immutable and records actor, action, resource/scope, policy revision, outcome, timestamp, and warnings/obligations when applicable.

A historical ALLOW never authorizes a later action. Protected resolution and workflow launch each perform a fresh evaluation immediately before the protected action.

Tests use a deterministic policy adapter so AUTH-01/AUTH-02 can inject policy changes without touching production systems.

## 12. Resolved Configuration and RunSpec Creation

Provider defaults are resolved into `ResolvedConfiguration`; they are not silently inserted into ScientificTaskSpec.

The generic model records result-affecting provider/workflow revision, method parameters, software/environment identity requirements, validation-profile revision, ReproducibilityContract, and planned environment/resource controls as required by the selected scientific contract.

For the Genome-web TF reference case, configuration includes at least:

```text
provider/workflow revision
min_seqs
IQ-TREE model
bootstrap
aLRT
seed
MAFFT threads
IQ-TREE threads
Nextflow version
Python/Biopython identity
MAFFT executable fingerprint
IQ-TREE executable fingerprint
validation-profile revision
ReproducibilityContract
planned environment/resource controls
```

For the first reference case, planning occurs on the intended execution host and runs an environment probe before publishing an executable RunSpec. The exact result-affecting tool/runtime identities required by the reproducibility contract are therefore bound before RunSpec publication. The external provider later records its own fingerprints, and collection/validation compares those observed identities against the frozen plan.

If the execution environment cannot satisfy or determine a required result-affecting identity, BioHarness does not publish an executable RunSpec for that configuration.

RunSpec creation is an immutable publication step. Once created, changes to result-affecting input/configuration produce another RunSpec rather than updating the existing row.

## 13. RunAttempt and RunEvent Model

Each BioHarness-issued external launch is one RunAttempt. Provider/workflow-engine internal retries remain within that RunAttempt. A new BioHarness resume/relaunch is a new RunAttempt even when compatible cached work is reused.

P0 attempt states are:

```text
SUBMITTING
RUNNING
COLLECTING
FINISHED
FAILED
UNKNOWN
NEEDS_OPERATOR_RECONCILIATION
```

A RunAttempt is created only when BioHarness is actually preparing a concrete external submission, so P0 does not create a separate unused `DRAFT` attempt state. Planning state belongs to TaskSpec/Assessment/Configuration/RunSpec.

The generic P0 kernel does not fabricate queue/cancel semantics. An adapter may expose stronger capabilities later through its capability snapshot; the first local-process reference case does not advertise durable queueing or cancellation.

Durable RunEvents include at least:

```text
AttemptCreated
AuthorizationChecked
SubmissionIntentRecorded
ExternalProcessBound
ExecutionStarted
ExecutionExited
ExecutionOutcomeUnknown
ArtifactDiscovered
ArtifactRegistered
ValidationReported
ReconciliationRequired
ReconciliationResolved
```

Transient observations such as repeated stdout tail updates or periodic process-alive checks do not need a durable event on every observation.

## 14. Exactly-Once Is Not Claimed

BioHarness has a generic executor capability model. It claims provider-native idempotency or durable external identity only when the active WorkflowExecutor adapter explicitly supports and evidences those capabilities.

The audited Genome-web TF reference provider has no native idempotency key and no durable async external execution ID, so that reference case does not claim provider exactly-once submission.

`submission_key` is a BioHarness-local attempt correlation/idempotency-intent identifier only unless an adapter explicitly binds it to a provider-native guarantee.

The critical safety rule is:

> After BioHarness has durably committed a submission intent for a RunAttempt, an ambiguous interruption never causes an automatic second external launch of that same attempt.

A new attempt may be created only after the prior attempt's status has been established sufficiently under the active provider's actual evidence/capabilities or an operator explicitly resolves the ambiguity according to policy.

## 15. Launch Transaction Boundary

External process creation cannot be made atomic with PostgreSQL, so the local-process P0 executor uses an explicit preflight + intent-before-side-effect protocol.

### Phase 0: fresh launch preflight, no database lock

Immediately before submission BioHarness:

1. rechecks the frozen input identities required by the RunSpec;
2. verifies the planned provider/workflow revision and execution-environment fingerprints;
3. verifies configured writable roots remain isolated from protected roots;
4. produces a short-lived launch-preflight evidence record bound to the RunSpec identity.

Failure here creates no external RunAttempt and no external side effect.

### Phase A: durable pre-submission transaction

In one short PostgreSQL transaction:

1. lock the target RunSpec attempt-allocation scope;
2. confirm the RunSpec is executable and the fresh preflight evidence matches its frozen identity;
3. evaluate and persist the current launch PolicyDecision;
4. allocate the next attempt number under the unique `(run_spec_id, attempt_number)` constraint;
5. create the RunAttempt in `SUBMITTING`;
6. allocate its unique local `submission_key` and provider attempt name;
7. append `AttemptCreated`, `AuthorizationChecked`, and `SubmissionIntentRecorded` events;
8. commit.

No large file hashing or external process call occurs while this transaction/lock is held.

Only after this commit may the executor produce an external side effect.

### Phase B: external process bind

The generic local-process adapter uses `subprocess.Popen` with an immutable adapter-produced invocation specification. BioHarness Core does not construct provider-specific commands.

For the Genome-web TF reference case only, the reference executor adapter points the generic local-process primitive at the existing external Genome-web `run.sh`/launcher. The launcher and command semantics remain outside BioHarness Core.

The executor immediately records observable process binding evidence such as host identity, PID, command fingerprint, provider attempt name, and timestamps, then appends `ExternalProcessBound`/`ExecutionStarted` and moves the read model to `RUNNING` in one state-plus-event transaction.

### Phase C: completion/ambiguity

When the child exits normally:

- non-zero exit -> `FAILED`, preserving logs/evidence;
- zero exit -> `COLLECTING`, then artifact/provenance collection;
- successful collection -> `FINISHED` execution state, independent from validation outcome.

If BioHarness loses the ability to establish what happened after submission intent was committed, the attempt becomes `UNKNOWN`; it is never silently recreated.

A user interrupt of the BioHarness CLI stops local waiting/observation but does not pretend the provider was cancelled. If the external outcome cannot be established, the attempt is recorded as `UNKNOWN` and later reconciled.

## 16. Reconciliation

P0 reconciliation is deliberately evidence-based and capability-limited.

The generic executor/reconciliation contract may inspect adapter-declared evidence such as:

```text
BioHarness RunAttempt state/events
recorded host/process binding
provider execution/workspace identifiers
provider invocation metadata
provider logs/trace
provider/session/cache identifiers where exposed
output/candidate markers
captured process exit evidence
lock/process observations
```

The Genome-web TF reference adapter maps its `invocation.json`, resolved manifest, Nextflow log/trace/session evidence, candidate manifest, and launch/process observations into that generic evidence vocabulary. Those filenames are not BioHarness Core concepts.

Reconciliation rules prefer strong terminal evidence:

1. valid provider completion evidence plus compatible captured process exit can establish completed execution;
2. explicit captured non-zero exit establishes failure;
3. a still-running process may keep the attempt active only when process identity is sufficiently consistent with the recorded binding;
4. a stale PID alone is not proof because PID reuse is possible;
5. conflicting or insufficient evidence yields `NEEDS_OPERATOR_RECONCILIATION` rather than a guessed state.

Automatic engine resume remains disabled for an adapter until the intended prior external/session identity can be bound reliably. Provider shorthands such as implicit `last` are never treated as scientific identity.

## 17. Artifact and Filesystem Model

A typical isolated server layout is:

```text
/srv/bioharness-p0/
├── runs/
├── artifacts/
├── work/
└── logs/
```

Exact deployment paths are configurable. All writable P0 paths must remain disjoint from configured protected/production roots.

Provider attempt output under the BioHarness run root is treated as immutable after registration. P0 registers important scientific outputs and execution evidence declared by the active adapter/contract.

For the Genome-web TF reference case, examples include:

- resolved manifest;
- external provider `invocation.json`;
- Nextflow log and trace;
- candidate manifest;
- representative protein bundles;
- alignments;
- trees;
- family/batch summary and audit tables.

Those artifact roles are reference-case mappings, not a universal BioHarness output schema.

Workflow-engine work/cache directories are execution cache, not automatically an Artifact collection.

Every registered Artifact records at least immutable ID, role/type, content SHA-256, size, URI/path, creating RunAttempt/RunSpec references, created/discovered time, and relevant provider metadata.

P0 does not duplicate large files into PostgreSQL.

## 18. Validation

Provider completion and provider `PASS` are not universal validation.

P0 creates separate typed ValidationReports. At minimum the generic P0 model supports:

```text
provider_contract
artifact_integrity
provenance_completeness
```

Each report has one `kind`; if the same evidence supports multiple kinds, separate reports are created rather than storing an ambiguous combined kind.

A versioned candidate ValidationProfile declares which report kinds/outcomes are required. ValidationEvaluation records the exact profile ID/revision and report IDs used.

`RunAttempt.FINISHED` means execution/collection finished. It may coexist with a failing ValidationEvaluation.

No P0 gate may convert a candidate into canonical/production output. Production publication is outside P0.

## 19. MemoryCandidate

P0 implements the smallest evidence-backed memory loop without vectors or a graph database.

A `MemoryCandidate` contains:

```text
scope (initially project/method limited)
kind/category
statement/lesson
tags/index keys
applicability constraints
RunSpec/RunAttempt/Artifact/Validation evidence refs
status
created_at
```

Examples include a version incompatibility, a reproducible preflight failure mode, a provider resume limitation, or a validated operational procedure.

P0 retrieval is deterministic/hybrid-light: exact tags, scope, provider/workflow revision, and simple text/metadata matching. No automatic MemoryPathway mining is implemented.

A later task may receive a matching MemoryCandidate as optional context. It cannot become Policy, Finding, ResolvedConfiguration, or canonical state without the corresponding governed operation.

## 20. CLI Boundary

P0 CLI is a thin client over application use cases. Command names may be grouped as follows:

```text
bioharness task create
bioharness task show
bioharness plan

bioharness run start
bioharness run show
bioharness run reconcile

bioharness artifact list
bioharness validate
bioharness memory list
```

CLI output must expose stable IDs and scientific/control-plane state rather than only human-readable success text.

The CLI never bypasses application/domain services to invoke a provider/workflow directly.

## 21. Reuse Policy for External Projects

P0 follows three reuse modes.

### Direct dependency

Use mature libraries instead of copying generic infrastructure: Pydantic, SQLAlchemy, Alembic, psycopg, Typer, pytest, RFC 8785 implementation, and standard Python process/hash/file primitives.

### Direct external invocation

Keep mature scientific/provider logic in its owning project and invoke it through adapters. The Genome-web resolver/launcher/Nextflow workflow, MAFFT, and IQ-TREE are the first reference case of this rule; they remain external sources of truth and are not BioHarness components.

### Pattern-level adaptation

Small process/reconciliation patterns from mature projects such as Sapporo may be adapted where semantics match. Non-trivial copied code must retain required attribution/license notices and be documented in third-party notices.

P0 does not copy whole control-plane modules whose source-of-truth/lifecycle semantics conflict with BioHarness merely to reduce initial code volume.

## 22. Testing Strategy

Implementation follows test-first development. The existing architecture scenario catalog is converted into executable tests without weakening assertions.

### Unit tests

Pure domain/identity rules:

- immutable model validation;
- projection/canonical-hash determinism;
- RunSpec versus RunAttempt identity;
- state-transition guards;
- assessment dependency fingerprint;
- validation profile evaluation;
- memory authority boundaries.

### Generic contract tests

BioHarness-owned ports and adapters are tested without Genome-web:

- DataProvider result -> ResolvedDataRef mapping contract;
- WorkflowExecutor capability snapshot semantics;
- local submission key never represented as provider exactly-once unless explicitly supported;
- UNKNOWN forbids blind duplicate launch;
- provider PASS can map only to typed validation evidence;
- artifact identity/digest registration contract.

### Integration tests

Use PostgreSQL plus temporary filesystem and a deterministic fake/small provider process to test transaction boundaries, concurrent attempt allocation, crash windows, artifact registration, reconciliation, policy changes, and immutable history. These tests must pass without the Genome-web repository or biological data.

### Reference-integration tests

Genome-web-specific tests live under the reference boundary and may exercise:

- five-digit UID preservation;
- cross-UID failure propagation;
- provider capability snapshot pinned to the audited revision;
- resolved-manifest/member digest capture;
- reference provider PASS mapping;
- explicit Nextflow resume identity limitations.

These tests validate the adapter/case, not BioHarness Core semantics.

### Live P0 acceptance run

Run only in the isolated server environment with real Genome-web source data and the audited TF pilot. It records the complete acceptance evidence required by `scenario-validation-plan.md`.

GitHub CI may run unit/generic contract/integration tests that do not require private biological data or installed MAFFT/IQ-TREE/Nextflow. The live scientific P0 reference run is not silently substituted with a mock CI run.

## 23. Initial Acceptance Slice

The implementation plan must prioritize the scenarios needed to prove the first vertical slice rather than attempting every future architecture scenario at once.

### Core-kernel slice

The following scenario semantics must be implementable without relying on Genome-web internals:

```text
TF-03  TaskSpec excludes provider defaults
AUTH-01 historical authorization cannot authorize new launch
AUTH-02 protected resolution authorized before access
PLAN-01 assessment dependency binding
PLAN-02 assumption-relevant config change forces reassessment
EXEC-02 attempt-scoped submission identity
EXEC-03 engine retry is not a new RunAttempt
EXEC-05 unknown outcome does not duplicate submission
VAL-01 provider PASS is typed
VAL-02 generic PASS collapse impossible
VAL-05 no implicit publication
PROM-04 Memory cannot directly become Policy/Finding
SEC-01 external content cannot mutate control state
```

`TF-03` retains its historical scenario ID but tests a generic BioHarness rule: provider defaults are configuration, not scientific intent.

### Genome-web TF reference slice

These scenarios are reference-adapter/acceptance evidence rather than Core product coupling:

```text
TF-01  leading-zero UID
TF-02  cross-UID conflict
EXEC-01 capability honesty for audited Genome-web revision
EXEC-06 implicit Nextflow last is not resume identity
DATA-01 resolved Genome-web manifest/member provenance
```

Other catalog scenarios remain authoritative but may follow after this minimal execution slice unless they become necessary for implementation correctness.

## 24. Deployment and Safety Boundary

Generic P0 deployment requires:

```text
PostgreSQL database/schema: dedicated to BioHarness environment
provider source data:      protected/read-only as configured
BioHarness run root:       isolated writable path
protected production roots:no BioHarness writes
production publication:    disabled in P0
```

The first Genome-web reference acceptance environment is one concrete instance of that policy.

BioHarness does not perform package installation, production build/deploy, or scientific run execution on the user's local Mac. Runtime validation belongs on the designated remote/test environment.

The initial policy adapter must enforce configured protected roots and deny production/canonical publication actions.

## 25. Failure Philosophy

BioHarness prefers explicit uncertainty over fabricated progress.

Examples:

```text
ambiguous biological intent
  -> UNRESOLVED

incompatible scientific semantics
  -> INCOMPATIBLE

input content changed after planning
  -> block launch and require replanning

lost execution outcome
  -> UNKNOWN / NEEDS_OPERATOR_RECONCILIATION

provider completed but artifact corrupted
  -> FINISHED execution + failed validation

valid null biological result
  -> not treated as pipeline failure
```

Retry, validation, scientific interpretation, and publication are separate operations.

## 26. Explicit P0 Non-Goals

P0 does not implement:

- FastAPI/Web UI;
- generic REST service;
- Pi/DeepSeek Harness runtime dependency;
- autonomous multi-agent planning;
- dynamic plugin installation/HMR;
- graph database;
- vector memory;
- automatic MemoryPathway mining;
- Celery/Temporal/Redis/Kafka;
- Slurm/SSH/Kubernetes/WES/TES executors;
- distributed locking;
- fabricated provider-native exactly-once semantics;
- durable provider cancellation unless a future adapter actually supports it;
- automatic implicit workflow-engine resume;
- production publication or canonical mutation;
- RNA-seq/DE/GO scientific contracts;
- provider-specific scientific algorithms or scripts inside BioHarness Core;
- reimplementation of Genome-web/Nextflow/MAFFT/IQ-TREE biological logic.

## 27. Success Criteria

The P0 kernel is implemented only when executable evidence demonstrates all of the following:

1. a real task can be represented as ScientificTaskSpec without leaking provider defaults into intent;
2. protected input resolution and launch are independently/currently authorized;
3. exact provider-resolved scientific input identities can be frozen and rechecked before execution;
4. ScientificAssessment is bound to explicit data/method dependencies;
5. one immutable RunSpec can own one or more distinct RunAttempts without conflating identity;
6. external submission intent is durable before process creation;
7. an uncertain launch can remain UNKNOWN without blind duplicate submission;
8. provider/workflow execution occurs through a declared adapter/capability boundary rather than provider-specific code embedded in Core;
9. execution evidence and scientific artifacts are immutable/checkable by digest;
10. provider PASS remains typed/provider-scoped rather than universal scientific validation;
11. candidate output cannot become production/canonical state in P0;
12. one scoped MemoryCandidate can be retrieved for a later task while remaining non-authoritative;
13. generic unit/contract/integration tests pass without the Genome-web repository or data.

The Genome-web TF reference case additionally demonstrates that an external existing scientific workflow can satisfy these contracts without being absorbed into BioHarness. Its acceptance record includes provider revision, implementation revision, data identity, assertions, observed results, timestamps, and supporting evidence.

Until those executable records exist, repository documentation must continue to report P0 runtime as `NOT_IMPLEMENTED`/acceptance as `NOT_RUN`.

## 28. Implementation Order Implied by This Design

This section fixes dependency order without serving as the detailed implementation plan:

```text
1. Python package + domain immutable models
2. canonical identity projections/hashes
3. PostgreSQL repositories + migrations
4. minimal policy evaluator and authorization records
5. generic DataProvider / WorkflowExecutor contracts
6. deterministic ScientificAssessment + ResolvedConfiguration
7. RunSpec publication
8. generic local-process executor + intent-before-side-effect RunAttempt lifecycle
9. generic reconciliation evidence model
10. artifact collection/digests
11. typed validation/profile evaluation
12. MemoryCandidate retrieval
13. generic unit/contract/integration tests
14. Genome-web TF reference adapters under examples/reference_integrations
15. isolated live Genome-web TF P0 acceptance run
```

The reference case is deliberately last in the dependency direction: it depends on BioHarness contracts, while BioHarness Core does not depend on the reference case.

The detailed task/file/test sequence is created only after this written spec is reviewed and approved.