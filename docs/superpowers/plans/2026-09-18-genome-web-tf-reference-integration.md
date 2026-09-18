# Genome-web TF Reference Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that the provider-agnostic BioHarness P0 kernel can govern the existing Genome-web TF workflow as an external reference case without absorbing Genome-web scripts, schemas, or workflow logic into BioHarness Core.

**Architecture:** Implement only a reference adapter under `examples/reference_integrations/genome_web_tf/`. The adapter depends on BioHarness public ports/contracts and on an externally checked-out, revision-pinned Genome-web repository. It translates provider-specific resolution, invocation, evidence, and artifact conventions into BioHarness records. Core remains independently installable/testable when this example directory is removed.

**Tech Stack:** Python 3.12+, existing BioHarness package, Python stdlib subprocess/csv/json/hashlib/pathlib, external Genome-web TF pilot at audited revision `05072cbbcd533ca59afa13996d8d0edd8f939c6e`, external Nextflow/MAFFT/IQ-TREE environment for live acceptance only.

**Spec:** `docs/superpowers/specs/2026-09-18-p0-runtime-kernel-design.md`

## Global Constraints

- This plan starts only after `docs/superpowers/plans/2026-09-18-p0-runtime-kernel.md` passes its Core completion gate.
- `validate_genomes.py`, `run.sh`, `run.py`, Nextflow sources, MAFFT, IQ-TREE, and Genome-web schemas remain external and MUST NOT be copied into `src/bioharness` or this example directory.
- The reference adapter may import BioHarness public ports/domain types; BioHarness Core MUST NOT import this adapter.
- Audited provider capability claims apply only to Genome-web revision `05072cbbcd533ca59afa13996d8d0edd8f939c6e`.
- The live acceptance environment uses read-only Genome-web source data, an isolated BioHarness PostgreSQL database/schema, and an isolated writable BioHarness run root.
- No production loader/publication/canonical mutation is allowed.
- No local Mac execution/build/deploy.
- Core `ResolutionService` supplies only generic logical resources plus generic task context (`task_id`, `task_revision`); provider-specific manifest/workspace paths come from reference configuration, never invented Core context keys.
- Core `WorkflowExecutor.prepare` consumes an immutable `ExecutionDescriptor`; the reference executor MUST NOT query BioHarness repositories to reconstruct configuration.
- The reference launch preflight rechecks frozen resolved-manifest/member identities and provider/environment constraints immediately before launch.
- BioHarness local-process stdout/stderr/`process.json` use a separate reference `control_root`; they MUST NOT pre-create Genome-web's provider-owned `run_root/attempts/<attempt>` directory, because the audited launcher requires that provider attempt directory not already exist.

---

### Task 1: Reference Adapter Package Boundary and Revision Guard

**Files:**
- Create: `examples/__init__.py`
- Create: `examples/reference_integrations/__init__.py`
- Create: `examples/reference_integrations/genome_web_tf/__init__.py`
- Create: `examples/reference_integrations/genome_web_tf/config.py`
- Create: `examples/reference_integrations/genome_web_tf/README.md`
- Create: `tests/reference/test_genome_web_boundary.py`

**Interfaces:**
- Produces: importable example module, `GenomeWebTFReferenceConfig`, and explicit audited-revision guard.

- [ ] **Step 1: Write boundary/revision tests**

```python
import pytest
from examples.reference_integrations.genome_web_tf.config import (
    AUDITED_REVISION,
    GenomeWebTFReferenceConfig,
    RevisionMismatch,
)


def test_audited_revision_is_fixed():
    assert AUDITED_REVISION == "05072cbbcd533ca59afa13996d8d0edd8f939c6e"


def test_revision_mismatch_refuses_audited_capabilities(tmp_path):
    cfg = GenomeWebTFReferenceConfig(
        repo_root=tmp_path,
        provider_revision="different",
        input_manifest=tmp_path / "genomes.tsv",
        planning_root=tmp_path / "planning",
        control_root=tmp_path / "control",
        run_root=tmp_path / "runs",
    )
    with pytest.raises(RevisionMismatch):
        cfg.require_audited_revision()
```

- [ ] **Step 2: Implement revision/path config**

```python
# examples/reference_integrations/genome_web_tf/config.py
from pathlib import Path
from pydantic import BaseModel, ConfigDict

AUDITED_REVISION = "05072cbbcd533ca59afa13996d8d0edd8f939c6e"


class RevisionMismatch(RuntimeError):
    pass


class GenomeWebTFReferenceConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    repo_root: Path
    provider_revision: str
    input_manifest: Path
    planning_root: Path
    control_root: Path
    run_root: Path
    existing_identities: Path | None = None

    def require_audited_revision(self) -> None:
        if self.provider_revision != AUDITED_REVISION:
            raise RevisionMismatch(
                f"audited capability snapshot requires {AUDITED_REVISION}; got {self.provider_revision}"
            )

    @property
    def validate_script(self) -> Path:
        return self.repo_root / "pipeline/nextflow/scripts/validate_genomes.py"

    @property
    def launcher(self) -> Path:
        return self.repo_root / "pipeline/nextflow/run.sh"
```

- [ ] **Step 3: Document dependency direction**

README states:

```text
Genome-web owns all biological data/schema/workflow logic.
This directory contains only a reference translation layer.
The reference layer may depend on BioHarness public contracts.
BioHarness Core never depends on this directory.
Deleting this directory must not break the bioharness package or Core tests.
```

- [ ] **Step 4: Run and commit**

Run: `python -m pytest tests/reference/test_genome_web_boundary.py -q`

Expected: PASS without running Genome-web scientific code.

```bash
git add examples tests/reference/test_genome_web_boundary.py
git commit -m "test: define Genome-web reference integration boundary"
```

---

### Task 2: External Data Resolution Adapter and Exact Member Identity

**Files:**
- Create: `examples/reference_integrations/genome_web_tf/data_adapter.py`
- Create: `tests/reference/test_genome_web_data_adapter.py`

**Interfaces:**
- `GenomeWebTFDataAdapter(config, run_command=subprocess.run)` implements Core `DataProvider`.
- `resolve(logical_resources, context)` consumes only Core's generic `logical_resources` plus `context["task_id"]` / `context["task_revision"]`.
- Provider-specific `input_manifest`, `planning_root`, and optional `existing_identities` are owned by `GenomeWebTFReferenceConfig`.
- Produces: Core `ProviderResolution` with one `ProviderResource` per requested genome and exact resolved/member identity evidence.

- [ ] **Step 1: Define typed provider error and stable logical identity**

Define `ProviderResolutionError` that preserves provider exit code/stderr. Define one adapter-local logical URI scheme, for example:

```text
genomeweb:registered-genome:<species_id>:<five-digit-uid>
```

The scheme belongs to the reference adapter, not BioHarness Core. The requested `logical_resources` set must exactly match the genomes present in the configured acceptance manifest for P0; unexpected extra or missing rows fail rather than being silently included/repaired.

- [ ] **Step 2: Test exact external resolver command construction**

For task `<task_id>`, create a task-scoped planning directory under `config.planning_root` and invoke:

```text
<sys.executable>
<external_repo>/pipeline/nextflow/scripts/validate_genomes.py
--genomes <config.input_manifest>
--output <config.planning_root>/<task_id>/genomes.resolved.tsv
```

Append `--existing-identities <config.existing_identities>` only when configured. Tests inject a fake command runner; the adapter never reproduces provider UID/table validation logic.

- [ ] **Step 3: Freeze exact consumed member identity**

Parse only the audited resolver columns:

```text
species_id
uid
genome_build
annotation_release
release_id
gene_tsv
transcript_tsv
protein_tsv
protein_fasta
tf_tsv
tf_gene_tsv
```

For every resolved genome, hash the six resolved member files and record role/path/SHA-256 evidence. Hash the deterministic resolved TSV itself. Build a deterministic per-genome member-manifest digest from the role + member digest set.

Map each row to Core `ProviderResource`:
- `biological_identity`: species/UID/build/annotation/release;
- `content_identity.manifest_sha256`: resolved TSV SHA-256;
- `content_identity.member_manifest_sha256`: per-genome member digest manifest;
- `metadata.resolved_manifest_path`: task-scoped resolved TSV path;
- `metadata.members`: auditable role/path/digest records.

Do not treat a path string alone as immutable data identity.

- [ ] **Step 4: Test leading-zero identity, exact scope, and failure propagation**

Tests must prove:
- `uid=00902` remains exactly `"00902"`;
- missing/extra logical resource rows are rejected;
- a changed member file changes its member-manifest digest;
- provider exit code 7 with stderr `cross-uid ID collision` becomes `ProviderResolutionError(7, ...)`;
- the adapter does not repair/rename/retry provider failures.

- [ ] **Step 5: Run and commit**

Run: `python -m pytest tests/reference/test_genome_web_data_adapter.py -q`

Expected: PASS using fake external commands only.

```bash
git add examples/reference_integrations/genome_web_tf/data_adapter.py tests/reference/test_genome_web_data_adapter.py
git commit -m "feat: add external Genome-web data reference adapter"
```

### Task 3: TF Workflow Executor Adapter over the Core ExecutionDescriptor

**Files:**
- Create: `examples/reference_integrations/genome_web_tf/executor_adapter.py`
- Create: `tests/reference/test_genome_web_executor_adapter.py`

**Interfaces:**
- `GenomeWebTFExecutorAdapter(config)` implements Core `WorkflowExecutor`.
- `prepare(execution: ExecutionDescriptor)` consumes the frozen materialized execution descriptor; it does not query BioHarness repositories.
- `inspect(binding | None, attempt_payload)` supports binding-optional reconciliation using attempt-scoped provider evidence.
- Produces: `ExecutorCapabilities`, `InvocationSpec`, `ExecutionEvidence`, and artifact candidate dictionaries.

- [ ] **Step 1: Test audited capability snapshot**

At the pinned revision assert:

```text
mode = synchronous_process
native_idempotency_key = false
durable_external_execution_id = false
poll = false
reconcile_after_disconnect = limited
cancellation = unsupported
logs = true
trace = true
```

A different provider revision must fail the audited-revision guard instead of inheriting the snapshot.

- [ ] **Step 2: Test invocation composition from ExecutionDescriptor**

The adapter obtains:
- isolated provider `run_root` and separate BioHarness `control_root` from reference config;
- exactly one consistent `resolved_manifest_path` from `execution.resolved_inputs`;
- `provider_attempt_name` from the descriptor;
- `min_seqs`, model/bootstrap/aLRT/seed from `execution.result_affecting_parameters`;
- MAFFT/IQ-TREE thread controls from `execution.planned_resource_controls`.

The returned `InvocationSpec` writes wrapper stdout/stderr under `config.control_root / execution.provider_attempt_name`. This lets `LocalProcessRunner` persist `process.json` there without creating the provider-owned `config.run_root / "attempts" / execution.provider_attempt_name` directory before `run.sh` starts.

`prepare()` returns an `InvocationSpec` whose argv begins:

```text
<external_repo>/pipeline/nextflow/run.sh
<config.run_root>
<resolved_manifest_path>
<execution.provider_attempt_name>
```

and appends only audited launcher flags such as `--min-seqs`, `--model`, `--bootstrap`, `--alrt`, `--seed`, `--mafft-threads`, and `--iqtree-threads`. Pass `--existing-identities` only when configured. P0 does not use implicit `--resume last`. The adapter MUST NOT construct `nextflow run` itself.

- [ ] **Step 3: Implement binding-optional evidence mapping**

Derive two evidence locations:
- BioHarness control evidence: `config.control_root / attempt_payload["provider_attempt_name"]` for `process.json` and wrapper stdout/stderr;
- provider attempt evidence: `config.run_root / "attempts" / attempt_payload["provider_attempt_name"]` for provider `invocation.json`, `genomes.resolved.tsv`, `nextflow.log`, `trace.tsv`, and `output/candidate/manifest.json`.

Map only observed files from those locations into `ExecutionEvidence.evidence`.

Rules:
- file absence is evidence absence, never success;
- a validated candidate manifest may provide strong success evidence for this audited synchronous launcher;
- without enough evidence to establish a terminal result, return inconclusive evidence and let Core stop at `NEEDS_OPERATOR_RECONCILIATION`;
- do not fabricate a durable external execution ID, poll API, cancellation, or exactly-once guarantee.

- [ ] **Step 4: Implement artifact discovery mapping**

Return artifact candidates only for provider outputs that actually exist. Roles may include `resolved_manifest`, `provider_invocation`, `execution_log`, `execution_trace`, `candidate_manifest`, `alignment`, `tree`, and audit tables. Core performs hashing/registration.

- [ ] **Step 5: Run and commit**

Run: `python -m pytest tests/reference/test_genome_web_executor_adapter.py -q`

Expected: PASS without Nextflow installed.

```bash
git add examples/reference_integrations/genome_web_tf/executor_adapter.py tests/reference/test_genome_web_executor_adapter.py
git commit -m "feat: add Genome-web TF workflow reference adapter"
```

### Task 4: Launch Preflight, Isolated Acceptance Configuration, and Dry Run

**Files:**
- Create: `examples/reference_integrations/genome_web_tf/preflight.py`
- Create: `examples/reference_integrations/genome_web_tf/acceptance.py`
- Create: `examples/reference_integrations/genome_web_tf/acceptance.example.toml`
- Create: `tests/reference/test_genome_web_preflight.py`
- Create: `tests/reference/test_acceptance_config.py`

**Interfaces:**
- `GenomeWebTFPreflight(config, uow_factory, command_runner=...)` implements the injected Core launch-preflight callable.
- Acceptance configuration supplies provider-specific source/planning/run/artifact paths; Core contracts remain provider-agnostic.
- `--dry-run` performs no resolver, launcher, or workflow side effect.

- [ ] **Step 1: Add example config**

```toml
provider_repo = "/srv/genome-web-backend"
provider_revision = "05072cbbcd533ca59afa13996d8d0edd8f939c6e"
input_manifest = "/srv/bioharness-p0/fixtures/genomes.tsv"
planning_root = "/srv/bioharness-p0/planning"
control_root = "/srv/bioharness-p0/control"
run_root = "/srv/bioharness-p0/runs"
artifact_root = "/srv/bioharness-p0/artifacts"
database_url_env = "BIOHARNESS_DATABASE_URL"
production_roots = ["/srv/genome-web-production"]
read_only_source_roots = ["/srv/genome-web-data"]
```

Optional `existing_identities` is configured only when the acceptance fixture has the audited snapshot. No credential is committed.

- [ ] **Step 2: Validate path isolation**

Reject writable planning/control/run/artifact paths that equal, contain, or are contained by protected production/source roots; reject `/` and the current user's home directory. Resolve symlinks before comparison. Also reject `control_root` paths that would overlap the provider-owned `run_root/attempts` namespace.

- [ ] **Step 3: Test launch preflight against frozen RunSpec dependencies**

Immediately before launch, preflight loads the RunSpec's ResolvedDataRefs/ResolvedConfiguration through the injected UoW and verifies at least:
- `run_spec_hash` is the identity being checked;
- provider/workflow revision still equals the audited revision;
- every recorded resolved manifest/member SHA-256 still matches current bytes;
- writable roots remain isolated;
- required external launcher/tool/runtime checks are observed without modifying provider state.

Return a short evidence dictionary suitable for `SubmissionIntentRecorded.preflight_evidence`. Any identity/revision/environment mismatch raises `PreflightFailed` before a RunAttempt/external side effect is created.

- [ ] **Step 4: Add dry-run command**

```bash
python -m examples.reference_integrations.genome_web_tf.acceptance \
  --config /path/to/acceptance.toml \
  --dry-run
```

Dry run prints pinned revision, resolved paths, requested logical resources, planned `ExecutionDescriptor`-driven adapter command, preflight checks, and policy outcomes. It does not execute the resolver/launcher.

- [ ] **Step 5: Run and commit**

Run:

```bash
python -m pytest   tests/reference/test_genome_web_preflight.py   tests/reference/test_acceptance_config.py -q
```

Expected: PASS.

```bash
git add examples/reference_integrations/genome_web_tf/preflight.py   examples/reference_integrations/genome_web_tf/acceptance.py   examples/reference_integrations/genome_web_tf/acceptance.example.toml   tests/reference/test_genome_web_preflight.py   tests/reference/test_acceptance_config.py
git commit -m "feat: add Genome-web launch preflight and acceptance config"
```

### Task 5: Live Isolated Genome-web TF Acceptance Run

**Files:**
- Create after run: `docs/validation/records/<YYYY-MM-DD>-genome-web-tf-p0.md`
- Modify after run: `docs/architecture/scenario-validation-plan.md` only to update scenario status/link where supported by the new evidence record.
- Runtime evidence remains outside git under the configured BioHarness run/artifact root.

**Interfaces:**
- Consumes: completed Core plan, completed reference adapters, designated remote/test environment.
- Produces: fresh acceptance record for the reference slice.

- [ ] **Step 1: Verify provider and implementation identity on the designated server**

Record:

```text
Genome-web revision = 05072cbbcd533ca59afa13996d8d0edd8f939c6e
BioHarness implementation revision = exact commit SHA
acceptance config SHA-256
input manifest SHA-256
```

If the provider revision differs, stop; re-audit or pin the audited revision before using the capability snapshot.

- [ ] **Step 2: Run dry-run isolation check remotely**

```bash
python -m examples.reference_integrations.genome_web_tf.acceptance \
  --config /srv/bioharness-p0/acceptance.toml \
  --dry-run
```

Expected: allowed protected read/resolve and candidate launch; denied production publication/canonical mutation; writable paths isolated.

- [ ] **Step 3: Execute only through BioHarness governed flow**

```text
TaskSpec
-> durable current authorization before reference DataProvider access
-> exact ResolvedDataRefs/member digests
-> ScientificAssessment/ResolvedConfiguration/RunSpec
-> fresh GenomeWebTFPreflight
-> current launch authorization + durable SubmissionIntent
-> materialized ExecutionDescriptor
-> RunAttempt
-> external Genome-web run.sh
-> external Nextflow/MAFFT/IQ-TREE
-> artifact registration
-> typed validation
-> scoped MemoryCandidate
```

Do not manually call the Genome-web launcher outside the RunAttempt when producing acceptance evidence.

- [ ] **Step 4: Run negative fixture separately for cross-UID conflict**

Use a deliberately conflicting reference fixture and verify the external provider rejects it before scientific execution. Record the provider stderr/exit evidence; do not modify IDs to force progress.

- [ ] **Step 5: Write one evidence record with catalog-required fields**

For each observed scenario include:

```text
scenario_id
fixture identity
BioHarness implementation revision
provider/workflow revision
input/data identity
action/failure injection
observable assertions
forbidden behavior
expected-vs-observed
PASS | FAIL | INCONCLUSIVE
executed_at
supporting logs/artifacts/events
```

Target reference scenarios: TF-01, TF-02, EXEC-01, EXEC-06, DATA-01. Only mark those actually executed.

- [ ] **Step 6: Re-run Core CI without Genome-web checkout**

Run:

```bash
python -m pytest tests/unit tests/contract tests/integration -q
```

Expected: PASS. This demonstrates reference integration did not become a Core dependency.

- [ ] **Step 7: Commit only evidence metadata/docs supported by the run**

```bash
git add docs/validation/records docs/architecture/scenario-validation-plan.md
git commit -m "docs: record Genome-web TF reference acceptance evidence"
```

Do not commit biological input data, credentials, large runtime artifacts, or secret production paths.

---

## Plan Completion Gate

This reference plan is complete only when:

1. BioHarness Core CI remains green with no Genome-web checkout present.
2. The reference adapter contains no copied Genome-web scientific/validation/launcher source.
3. The pinned provider revision is verified before applying its capability snapshot.
4. Live acceptance uses isolated BioHarness DB/run roots and read-only Genome-web source data.
5. Only scenarios with fresh executable evidence move from `NOT_RUN`.
6. The reference run does not publish/canonicalize production outputs.
7. The DataProvider uses only generic Core resolution arguments; provider-specific manifest/planning paths remain reference configuration.
8. The WorkflowExecutor consumes Core `ExecutionDescriptor` and does not reach back into BioHarness repositories.
9. Fresh launch preflight rechecks resolved manifest/member identity before any external launch side effect.
10. Binding loss is reconciled from attempt-scoped evidence when possible and otherwise stops safely at operator reconciliation.
11. BioHarness wrapper evidence uses `control_root` and never pre-creates the Genome-web provider attempt directory before the audited launcher does.

The reference integration remains an example/case after completion; it does not become a BioHarness Core dependency.
