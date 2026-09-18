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
    run_root: Path

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

### Task 2: External Data Resolution Adapter

**Files:**
- Create: `examples/reference_integrations/genome_web_tf/data_adapter.py`
- Create: `tests/reference/test_genome_web_data_adapter.py`

**Interfaces:**
- `GenomeWebTFDataAdapter(config, run_command=subprocess.run)` implements Core `DataProvider`.
- `resolve(logical_resources, context)` requires `context["input_manifest"]` and `context["planning_workspace"]`; optional `context["existing_identities"]`.
- Produces: Core `ProviderResolution`.

- [ ] **Step 1: Define typed provider error and injected command runner**

```python
class ProviderResolutionError(RuntimeError):
    def __init__(self, exit_code: int, stderr: str):
        self.exit_code = exit_code
        self.stderr = stderr
        super().__init__(f"Genome-web resolver failed with exit code {exit_code}: {stderr}")
```

The adapter constructor stores `run_command`; tests inject a fake callable rather than invoking the real external resolver.

- [ ] **Step 2: Test exact command construction**

Assert argv is:

```text
<sys.executable>
<external_repo>/pipeline/nextflow/scripts/validate_genomes.py
--genomes <context.input_manifest>
--output <context.planning_workspace>/genomes.resolved.tsv
```

Append `--existing-identities <path>` only when context contains that key. Never reproduce provider UID/table validation logic.

- [ ] **Step 3: Implement `resolve`**

Call the injected runner with `check=True`, `text=True`, `capture_output=True`, `shell=False` semantics. Parse only the external resolver output TSV columns required by the audited case:

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

Map each row to a Core `ProviderResource`. Keep `uid` as a string. Put provider-specific fields in `biological_identity`/`metadata`; do not change Core schemas to make them mandatory.

- [ ] **Step 4: Test leading-zero and failure propagation**

A fake TSV with `uid=00902` must return exactly `"00902"`. A fake command failure with exit code 7 and stderr `cross-uid ID collision` must become `ProviderResolutionError(7, ...)`; the adapter must not repair/rename/retry.

- [ ] **Step 5: Run and commit**

Run: `python -m pytest tests/reference/test_genome_web_data_adapter.py -q`

Expected: PASS using fake external commands only.

```bash
git add examples/reference_integrations/genome_web_tf/data_adapter.py tests/reference/test_genome_web_data_adapter.py
git commit -m "feat: add external Genome-web data reference adapter"
```

---

### Task 3: TF Workflow Executor Adapter Without Nextflow Reimplementation

**Files:**
- Create: `examples/reference_integrations/genome_web_tf/executor_adapter.py`
- Create: `tests/reference/test_genome_web_executor_adapter.py`

**Interfaces:**
- `GenomeWebTFExecutorAdapter(config)` implements Core `WorkflowExecutor`.
- Produces: `ExecutorCapabilities`, `InvocationSpec`, `ExecutionEvidence`, artifact candidate dictionaries.

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

- [ ] **Step 2: Test invocation composition**

Given run payload containing `run_root`, `manifest`, `provider_attempt_name`, and explicit resolved parameters, `prepare()` returns an `InvocationSpec` whose argv begins:

```text
<external_repo>/pipeline/nextflow/run.sh
<isolated_run_root>
<manifest>
<provider_attempt_name>
```

and appends `--min-seqs`, `--model`, `--bootstrap`, `--alrt`, `--seed`, `--mafft-threads`, `--iqtree-threads`. It MUST NOT construct `nextflow run` itself.

- [ ] **Step 3: Implement evidence mapping**

Map existing provider paths such as `invocation.json`, `genomes.resolved.tsv`, `nextflow.log`, `trace.tsv`, and `output/candidate/manifest.json` into generic `ExecutionEvidence.evidence`. File absence is evidence absence, not success.

- [ ] **Step 4: Implement artifact discovery mapping**

Return artifact candidates for provider outputs that actually exist. Roles may include `resolved_manifest`, `provider_invocation`, `execution_log`, `execution_trace`, `candidate_manifest`, `alignment`, `tree`, and audit tables. Core performs hashing/registration.

- [ ] **Step 5: Run and commit**

Run: `python -m pytest tests/reference/test_genome_web_executor_adapter.py -q`

Expected: PASS without Nextflow installed.

```bash
git add examples/reference_integrations/genome_web_tf/executor_adapter.py tests/reference/test_genome_web_executor_adapter.py
git commit -m "feat: add Genome-web TF workflow reference adapter"
```

---

### Task 4: Isolated Acceptance Configuration and Dry Run

**Files:**
- Create: `examples/reference_integrations/genome_web_tf/acceptance.py`
- Create: `examples/reference_integrations/genome_web_tf/acceptance.example.toml`
- Create: `tests/reference/test_acceptance_config.py`

**Interfaces:**
- Produces: validated remote/test acceptance configuration; `--dry-run` performs no provider side effect.

- [ ] **Step 1: Add example config**

```toml
provider_repo = "/srv/genome-web-backend"
provider_revision = "05072cbbcd533ca59afa13996d8d0edd8f939c6e"
input_manifest = "/srv/bioharness-p0/fixtures/genomes.tsv"
run_root = "/srv/bioharness-p0/runs"
artifact_root = "/srv/bioharness-p0/artifacts"
database_url_env = "BIOHARNESS_DATABASE_URL"
production_roots = ["/srv/genome-web-production"]
read_only_source_roots = ["/srv/genome-web-data"]
```

No credential is committed.

- [ ] **Step 2: Validate path isolation**

Reject writable run/artifact paths that equal, contain, or are contained by protected production/source roots; reject `/` and the current user's home directory. Resolve symlinks before comparison.

- [ ] **Step 3: Add dry-run command**

```bash
python -m examples.reference_integrations.genome_web_tf.acceptance \
  --config /path/to/acceptance.toml \
  --dry-run
```

Dry run prints revision, resolved paths, planned adapter commands, and policy outcomes; it does not execute resolver/launcher.

- [ ] **Step 4: Run and commit**

Run: `python -m pytest tests/reference/test_acceptance_config.py -q`

Expected: PASS.

```bash
git add examples/reference_integrations/genome_web_tf/acceptance.py examples/reference_integrations/genome_web_tf/acceptance.example.toml tests/reference/test_acceptance_config.py
git commit -m "feat: add isolated reference acceptance configuration"
```

---

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
-> authorized reference DataProvider resolve
-> ResolvedDataRefs
-> ScientificAssessment/ResolvedConfiguration/RunSpec
-> current launch authorization
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

The reference integration remains an example/case after completion; it does not become a BioHarness Core dependency.
