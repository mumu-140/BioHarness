# BioHarness Workflow Executor Capabilities and P0 Source Audit

Date: 2026-09-18
Status: Source audit + focused architecture decision record
Runtime status: NOT_IMPLEMENTED
Validation status: NOT_RUN

## 1. Scope

This record audits the selected P0 provider against the actual current Genome-web TF Nextflow pilot rather than assuming a generic asynchronous workflow service.

Source files inspected on `mumu-140/genome-web-backend/main`:

- `pipeline/nextflow/run.sh`
- `pipeline/nextflow/scripts/run.py`
- `pipeline/nextflow/scripts/validate_genomes.py`
- `pipeline/nextflow/main.nf`
- `pipeline/nextflow/nextflow.config`
- `pipeline/nextflow/README.md`

The purpose is to make the P0 contract match what exists today and to prevent BioHarness from claiming capabilities that the provider does not expose.

## 2. Observed Provider Behavior

### 2.1 Launcher shape

`run.sh` loads the existing Genome-web environment/configuration and `exec`s the Python launcher.

`run.py` then:

1. validates explicit paths/parameters;
2. requires Nextflow 25.10.4;
3. fingerprints Python/Biopython, MAFFT, IQ-TREE, and workflow source files;
4. creates a unique attempt directory;
5. resolves/validates the genome manifest;
6. writes `invocation.json`;
7. invokes Nextflow synchronously with `subprocess.run(..., check=True)`;
8. requires `output/candidate/manifest.json` after successful process exit.

This is not currently a server-style submit/poll API.

### 2.2 Compute backend

The current `nextflow.config` fixes:

```text
process.executor = local
executor.cpus = 4
executor.memory = 8 GB
```

Therefore the selected P0 currently exercises the WorkflowExecutor/provider boundary, not a remote Slurm/SSH/Kubernetes compute abstraction.

### 2.3 Concurrency protection

The launcher takes an exclusive non-blocking `fcntl` lock on:

```text
RUN_ROOT/.launch.lock
```

for the duration of validation and the synchronous Nextflow execution.

This serializes launches within one run root, but it is not a distributed idempotency service and does not establish global exactly-once submission.

### 2.4 Attempt identity

Attempt directories are explicit and non-reusable:

```text
RUN_ROOT/attempts/<attempt>
```

If the directory already exists, the launcher fails and requires a new attempt name.

This aligns naturally with BioHarness `RunAttempt` identity.

### 2.5 Resume

The launcher accepts:

```text
--resume
--resume <session>
```

The bare form passes Nextflow `-resume` (last session), whereas an explicit value passes `-resume <session>`.

For automated BioHarness recovery, explicit prior session identity is preferable to an implicit `last` selection whenever the provider exposes it reliably.

### 2.6 Provenance currently recorded

`invocation.json` records, among other fields:

- full command;
- Nextflow version;
- MAFFT/IQ-TREE versions and executable fingerprints;
- Python/Biopython identity and executable fingerprint;
- source-file SHA256 values;
- SHA256 of the original genomes manifest;
- whether database collision checking used a provided snapshot or remained pending.

The resolved manifest itself is used for Nextflow input after paths are canonicalized.

### 2.7 Resolved input identity gap

`validate_genomes.py` resolves the six scientific input paths per genome to absolute files and validates metadata/ID consistency, but the current launcher does not persist a digest of `genomes.resolved.tsv` or all individual source-file contents in `invocation.json`.

Nextflow deep caching uses file content for execution/cache behavior, but BioHarness provenance should not rely on an internal cache key as its only historical input identity.

### 2.8 Provider validation

The Nextflow workflow ends with `BUNDLE`, which assembles and verifies a whole-batch candidate. The launcher additionally requires the candidate manifest to exist.

This is valuable provider-level validation evidence, but it should be registered with an explicit validation kind rather than described as universal scientific or publication validation.

## 3. WorkflowExecutorCapabilitySnapshot

BioHarness must let an execution/provider adapter declare what it can actually do.

Conceptual contract:

```yaml
workflow_executor_capabilities:
  provider: genome-web-tf-nextflow-pilot
  provider_revision: ...

  submission:
    mode: synchronous_process
    native_idempotency_key: false
    durable_external_execution_id: limited

  observation:
    poll: limited
    reconcile_after_disconnect: limited
    logs: true
    trace: true

  retry_resume:
    engine_resume: true
    explicit_resume_identity: supported_if_session_captured
    internal_task_retry: nextflow_defined

  cancellation:
    supported: provider_specific

  compute:
    backend: local
    remote_scheduler: false

  provenance:
    invocation_record: true
    source_hashes: true
    tool_fingerprints: true
    resolved_manifest_digest: not_currently_emitted
```

The snapshot is tied to a provider revision; it is not a timeless claim about Nextflow itself.

## 4. Capability-Driven Execution Rule

BioHarness Core must not assume all WorkflowExecutors provide the same recovery guarantees.

Required rule:

> A provider adapter may advertise only capabilities demonstrated by its concrete integration. Missing capability is explicit state, not permission to invent an approximation silently.

Examples:

- if a provider has durable external IDs and lookup, BioHarness may automatically reconcile `UNKNOWN`;
- if it lacks reliable lookup, `UNKNOWN` may require filesystem/process evidence or operator resolution;
- if absence cannot be established safely, BioHarness must not auto-resubmit simply to make progress;
- no provider may be described as exactly-once merely because BioHarness stores a submission key.

## 5. Refined P0 Failure-Recovery Semantics

The previous architecture correctly requires that lost acknowledgement must not cause blind duplicate execution.

For this concrete P0, however, the implementation path is capability constrained.

### Supported target behavior

Before launch:

```text
RunAttempt exists
submission intent recorded
attempt/run-root identity fixed
```

During/after uncertain communication:

```text
SUBMITTING/RUNNING -> UNKNOWN
```

Reconciliation may inspect provider-supported evidence such as:

- attempt directory existence;
- `invocation.json`;
- Nextflow log/trace/session metadata;
- candidate manifest;
- launcher/run-root lock/process state when observable.

If the evidence cannot prove an outcome safely:

```text
UNKNOWN -> NEEDS_OPERATOR_RECONCILIATION
```

not:

```text
UNKNOWN -> blind automatic resubmit
```

P0 therefore tests **safe uncertainty handling**, not a false exactly-once guarantee.

## 6. Explicit Resume Identity

Automated recovery should prefer an explicit Nextflow session identifier over `-resume`/`last` where the previous session identity is available.

Rationale:

- `last` is contextual to the launch workspace;
- a later unrelated/changed invocation could become the most recent session;
- content caching may prevent incorrect recomputation, but cache safety is not the same as correct attempt/session lineage.

P0 implementation planning should therefore include capture of the Nextflow session/run identifier in the provider execution record when feasible.

If the provider cannot expose it reliably, that limitation must be recorded and automatic resume behavior narrowed accordingly.

## 7. Resolved Manifest and Member Identity

BioHarness should register the actual resolved input manifest used by the workflow, not only the user's original manifest file.

P0 target provenance:

```text
original manifest identity
    -> resolved manifest Artifact/digest
        -> per-row ResolvedDataRefs
            -> input file identities/digests or immutable provider revisions
```

At minimum, the RunSpec must be able to demonstrate that the biological data actually presented to Nextflow correspond to the recorded provider/input identity.

The current Genome-web launcher does not need to be rewritten to own BioHarness semantics; the adapter can calculate/register additional identity information outside the provider.

## 8. Validation Mapping

Provider BUNDLE/launcher evidence maps to typed validation rather than one universal PASS.

Illustrative mapping:

```text
provider_preflight          -> ValidationReport(kind=provider_contract)
BUNDLE candidate verifier  -> ValidationReport(kind=artifact_integrity/provider_contract)
BioHarness provenance check -> ValidationReport(kind=provenance_completeness)
future scientific review   -> separate method/scientific validation kind
future production release  -> separate publication_readiness profile
```

This prevents the launcher's message:

```text
PASS candidate=...
```

from being interpreted as “scientifically canonical and production-approved.”

## 9. P0 Scope Correction

The first P0 implementation should prove:

- real Genome-web biological input resolution;
- exact RunSpec identity;
- one concrete local Nextflow WorkflowExecutor adapter;
- RunAttempt separation;
- provider capability snapshot;
- candidate Artifact ingestion;
- typed validation;
- safe handling of failed/uncertain attempts;
- explicit Decision/MemoryCandidate feedback;
- no implicit production publication.

It should **not** claim to validate yet:

- Slurm execution;
- SSH remote launch;
- distributed locks;
- Kubernetes;
- generic WES/TES compatibility;
- provider-native exactly-once idempotency;
- all future Nextflow executor modes.

Those can be later adapters/slices.

## 10. P0 Source-Audit Acceptance Scenarios

### P0-CAP-01 Capability honesty

Status: `NOT_RUN`

Expected:

- current pilot advertises `compute.backend=local`;
- no remote-scheduler capability is fabricated;
- reconciliation/idempotency capability is marked according to implemented adapter evidence.

### P0-CAP-02 Unknown state without reliable external lookup

Status: `NOT_RUN`

Expected:

- uncertain launch state remains `UNKNOWN`/`NEEDS_OPERATOR_RECONCILIATION` when available evidence is insufficient;
- no automatic duplicate submission occurs.

### P0-RESUME-01 Explicit resume lineage

Status: `NOT_RUN`

Expected:

- automated resume binds to the intended prior Nextflow session when explicit identity is available;
- `last` is not used as an implicit scientific identity.

### P0-PROV-01 Resolved manifest provenance

Status: `NOT_RUN`

Expected:

- the exact resolved manifest used for execution is registered/digested;
- member input identity is checkable independently of the original user manifest path.

### P0-VAL-01 Provider PASS is typed

Status: `NOT_RUN`

Expected:

- provider candidate verification produces typed validation evidence;
- provider `PASS candidate=...` does not set canonical/publication status.

## 11. New Invariants

1. WorkflowExecutor behavior is capability-declared and revision-scoped.
2. Unsupported recovery capability remains explicit; Core does not invent provider guarantees.
3. P0 validates the current local Nextflow integration, not remote compute backends.
4. Safe uncertainty is preferable to duplicate scientific computation when execution outcome cannot be established.
5. Automated Nextflow resume should bind explicit session lineage when feasible.
6. BioHarness provenance records the resolved inputs actually consumed, not only the pre-resolution user manifest.
7. Provider candidate verification is typed validation evidence, not canonical scientific approval.

## 12. Status

```text
source_audit = COMPLETED
capability_contract = DESIGNED
adapter_implementation = NOT_IMPLEMENTED
p0_source_audit_scenarios = NOT_RUN
```
