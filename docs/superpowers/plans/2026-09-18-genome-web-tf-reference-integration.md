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
- Create: `examples/reference_integrations/genome_web_tf/__init__.py`
- Create: `examples/reference_integrations/genome_web_tf/config.py`
- Create: `examples/reference_integrations/genome_web_tf/README.md`
- Create: `tests/reference/test_genome_web_boundary.py`

**Interfaces:**
- Consumes: external Genome-web checkout path and expected revision.
- Produces: `GenomeWebTFReferenceConfig` and explicit revision verification.

- [ ] **Step 1: Write boundary/revision tests**

```python
from pathlib import Path
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

- [ ] **Step 2: Implement config without provider code copying**

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

- [ ] **Step 3: Document the dependency direction**

README must state exactly:

```text
Genome-web owns all biological data/schema/workflow logic.
This directory contains only a reference translation layer.
Deleting this directory must not break the bioharness package or Core tests.
```

- [ ] **Step 4: Run reference boundary test**

Run: `python -m pytest tests/reference/test_genome_web_boundary.py -q`

Expected: PASS without running Genome-web scientific code.

- [ ] **Step 5: Commit**

```bash
git add examples/reference_integrations/genome_web_tf tests/reference/test_genome_web_boundary.py
git commit -m "test: define Genome-web reference integration boundary"
```

---

### Task 2: External Data Resolution Adapter

**Files:**
- Create: `examples/reference_integrations/genome_web_tf/data_adapter.py`
- Create: `tests/reference/test_genome_web_data_adapter.py`

**Interfaces:**
- Consumes: BioHarness `DataProvider` port, external `validate_genomes.py`, input manifest path.
- Produces: `ProviderResolution` with reference-case resource identities/evidence.

- [ ] **Step 1: Write command construction test**

Inject a subprocess runner fake. Assert the adapter invokes:

```text
<python> <external_repo>/pipeline/nextflow/scripts/validate_genomes.py
  --genomes <input_manifest>
  --output <planning_workspace>/genomes.resolved.tsv
```

When `existing_identities` is provided, assert `--existing-identities <path>` is appended. The adapter must never reproduce Genome-web UID/table validation rules itself.

- [ ] **Step 2: Implement `GenomeWebTFDataAdapter.resolve`**

Use `subprocess.run(argv, check=True, text=True, capture_output=True)` with `shell=False`. Parse only the external resolver's output TSV columns required by the audited case:

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

Return `ProviderResolution(provider="genome-web", provider_revision=config.provider_revision, resources=..., evidence=...)`.

- [ ] **Step 3: Preserve provider strings verbatim**

The adapter must not coerce `uid` to int. Add test that TSV value `00902` returns exactly `"00902"` in provider resource metadata.

- [ ] **Step 4: Propagate provider failures rather than repairing them**

Use a fake external resolver that exits non-zero. Assert the adapter raises a typed `ProviderResolutionError` containing exit code and captured stderr; it must not rename IDs, patch tables, or retry with relaxed rules.

- [ ] **Step 5: Run tests**

Run: `python -m pytest tests/reference/test_genome_web_data_adapter.py -q`

Expected: PASS using fake external commands only.

- [ ] **Step 6: Commit**

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
- Consumes: BioHarness `WorkflowExecutor` port and external Genome-web `run.sh`.
- Produces: audited capability snapshot, provider-specific `InvocationSpec`, evidence/artifact discovery mapping.

- [ ] **Step 1: Write audited capability test**

Assert at the pinned revision:

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

A different provider revision must fail `require_audited_revision()` rather than inheriting this snapshot.

- [ ] **Step 2: Write invocation composition test**

Given adapter payload containing `run_root`, `manifest`, `provider_attempt_name`, and resolved configuration, assert `prepare()` returns an `InvocationSpec` whose argv begins:

```text
<external_repo>/pipeline/nextflow/run.sh
<isolated_run_root>
<manifest>
<provider_attempt_name>
```

and appends explicit provider parameters (`--min-seqs`, `--model`, `--bootstrap`, `--alrt`, `--seed`, `--mafft-threads`, `--iqtree-threads`) from ResolvedConfiguration.

Do not construct `nextflow run` in the adapter.

- [ ] **Step 3: Implement evidence mapping**

`inspect()` may map external evidence paths under the provider attempt directory:

```text
invocation.json
genomes.resolved.tsv
nextflow.log
trace.tsv
output/candidate/manifest.json
```

into generic `ExecutionEvidence.evidence`. Missing files are evidence absence, not automatic success/failure unless the audited contract says otherwise.

- [ ] **Step 4: Implement artifact discovery mapping**

Return candidate dictionaries for existing reference outputs only. Roles may include `resolved_manifest`, `provider_invocation`, `execution_log`, `execution_trace`, `candidate_manifest`, `alignment`, `tree`, and audit tables. Artifact bytes remain external files and are hashed by BioHarness Core.

- [ ] **Step 5: Run adapter tests**

Run: `python -m pytest tests/reference/test_genome_web_executor_adapter.py -q`

Expected: PASS without Nextflow installed.

- [ ] **Step 6: Commit**

```bash
git add examples/reference_integrations/genome_web_tf/executor_adapter.py tests/reference/test_genome_web_executor_adapter.py
git commit -m "feat: add Genome-web TF workflow reference adapter"
```

---

### Task 4: Reference Acceptance Harness Configuration

**Files:**
- Create: `examples/reference_integrations/genome_web_tf/acceptance.py`
- Create: `examples/reference_integrations/genome_web_tf/acceptance.example.toml`
- Create: `tests/reference/test_acceptance_config.py`

**Interfaces:**
- Consumes: remote/test-only paths and database URL.
- Produces: a validated acceptance configuration; no production execution by default.

- [ ] **Step 1: Define required acceptance configuration**

```toml
provider_repo = "/srv/genome-web-backend"
provider_revision = "05072cbbcd533ca59afa13996d8d0edd8f939c6e"
input_manifest = "/srv/bioharness-p0/fixtures/genomes.tsv"
run_root = "/srv/bioharness-p0/runs"
artifact_root = "/srv/bioharness-p0/artifacts"
database_url_env = "BIOHARNESS_DATABASE_URL"
production_roots = ["/srv/genome-web-production"]
```

No real password/credential is committed.

- [ ] **Step 2: Validate isolation before any provider read or launch**

`acceptance.py` must resolve paths and reject when `run_root` or `artifact_root` equals, contains, or is contained by a protected production root. It must reject `/`, home directory, and paths inside the external Genome-web source-data roots configured as read-only.

- [ ] **Step 3: Add dry-run inspection command**

`python -m examples.reference_integrations.genome_web_tf.acceptance --config <file> --dry-run` prints resolved adapter revision, paths, planned provider commands, and policy decisions but does not invoke the provider.

- [ ] **Step 4: Run acceptance config tests**

Run: `python -m pytest tests/reference/test_acceptance_config.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add examples/reference_integrations/genome_web_tf/acceptance.py examples/reference_integrations/genome_web_tf/acceptance.example.toml tests/reference/test_acceptance_config.py
git commit -m "feat: add isolated reference acceptance configuration"
```

---

### Task 5: Live Isolated Genome-web TF Acceptance Run

**Files:**
- Modify after run: `docs/architecture/scenario-validation-plan.md` only to add evidence records/statuses actually supported by the live run; do not mark unrelated scenarios PASS.
- Create per-run evidence outside git under the configured BioHarness run/artifact root.

**Interfaces:**
- Consumes: completed Core plan, completed reference adapter tasks, designated remote/test environment.
- Produces: executable acceptance evidence for the Genome-web TF reference slice.

- [ ] **Step 1: Verify external provider revision on the designated server**

Required evidence:

```text
Genome-web repository revision = 05072cbbcd533ca59afa13996d8d0edd8f939c6e
BioHarness implementation revision = exact commit SHA
acceptance config digest = SHA-256
input manifest digest = SHA-256
```

Do not proceed if provider revision differs; re-audit or pin the audited revision first.

- [ ] **Step 2: Run dry-run isolation check**

Run on the designated remote/test environment, not the local Mac:

```bash
python -m examples.reference_integrations.genome_web_tf.acceptance \
  --config /srv/bioharness-p0/acceptance.toml \
  --dry-run
```

Expected: ALLOW for protected read/resolve and candidate launch; DENY for production publication/canonical mutation; all writable paths isolated from production roots.

- [ ] **Step 3: Execute the governed reference slice**

Use BioHarness application/CLI operations so the flow is:

```text
TaskSpec
-> authorized reference DataProvider resolve
-> exact ResolvedDataRefs
-> assessment/configuration/RunSpec
-> current launch authorization
-> RunAttempt
-> external Genome-web run.sh
-> Nextflow/MAFFT/IQ-TREE externally
-> artifact registration
-> typed validation
-> scoped MemoryCandidate
```

Do not call the Genome-web launcher manually outside the BioHarness RunAttempt when collecting acceptance evidence.

- [ ] **Step 4: Record scenario evidence only for observed cases**

Minimum target reference scenarios:

```text
TF-01 leading-zero UID
TF-02 cross-UID conflict (separate negative fixture/run)
EXEC-01 capability honesty
EXEC-06 implicit Nextflow last is not resume identity
DATA-01 resolved manifest/member provenance
```

Each recorded scenario must include the catalog-required fixture identity, implementation revision, provider revision, input identity, action/failure injection, observable assertions, forbidden behavior, expected-vs-observed, result status, executed_at, logs/artifacts/events.

- [ ] **Step 5: Verify no Core dependency reversal was introduced**

Run CI again without the external Genome-web checkout available:

```bash
python -m pytest tests/unit tests/contract tests/integration -q
```

Expected: PASS. Then run reference tests separately in the environment that has the reference integration dependencies/configuration.

- [ ] **Step 6: Commit only documentation/status changes supported by evidence**

```bash
git add docs/architecture/scenario-validation-plan.md
git commit -m "docs: record Genome-web TF reference acceptance evidence"
```

Do not commit biological input data, credentials, large run artifacts, or production paths containing secrets.

---

## Plan Completion Gate

This reference plan is complete only when:

1. BioHarness Core CI remains green with no Genome-web checkout present.
2. The reference adapter contains no copied Genome-web scientific/validation/launcher source.
3. The pinned provider revision is verified before applying its capability snapshot.
4. Live acceptance runs use isolated BioHarness DB/run roots and read-only Genome-web source data.
5. Only scenarios with fresh executable evidence move from `NOT_RUN`.
6. The reference run does not publish/canonicalize production outputs.

The reference integration remains an example/case after completion; it does not become a BioHarness Core dependency.
