# BioHarness P0 Runtime Kernel Implementation Plan

Execution status: **COMPLETED AND MERGED VIA PR #2**. Subsequent execution/reconciliation/validation hardening is tracked in `2026-09-18-p0-1h-core-hardening.md`. The checklist below is retained as the implementation script/audit trail rather than the live status source.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first provider-agnostic BioHarness Research Control Plane kernel that can plan, authorize, execute, reconcile, register evidence, validate, and recall one governed scientific run without depending on Genome-web or any agent runtime.

**Architecture:** Implement a Python modular monolith under `src/bioharness` with immutable Pydantic domain records, explicit ports, SQLAlchemy/PostgreSQL persistence, and a generic local-process primitive. Core tests use deterministic fake providers/processes. Genome-web TF is explicitly excluded from this plan and is handled by the separate reference-integration plan after Core is working.

**Tech Stack:** Python 3.12+, Pydantic 2, SQLAlchemy 2, Alembic, psycopg 3, PostgreSQL 16, Typer, pytest, rfc8785, Python stdlib.

**Spec:** `docs/superpowers/specs/2026-09-18-p0-runtime-kernel-design.md`

## Global Constraints

- `src/bioharness/**` MUST NOT import Genome-web, Nextflow, Pi, DeepSeek Harness, or code from `examples/reference_integrations/**`.
- Provider-specific scientific scripts and schemas are not BioHarness Core.
- PostgreSQL is authoritative for control-plane identity/state; artifact bytes remain external immutable files referenced by digest/path.
- ScientificTaskSpec contains scientific intent, not ordinary provider defaults.
- ScientificAssessment is pre-execution feasibility, not biological hypothesis support.
- RunSpec is immutable intended-work identity; RunAttempt is one concrete external launch.
- `analysis_hash` and `run_spec_hash` use SHA-256 over RFC 8785 canonical JSON with explicit projection versions.
- A submission intent and current authorization must be durable before an external side effect.
- Unknown external outcome must remain `UNKNOWN`/`NEEDS_OPERATOR_RECONCILIATION`; no blind duplicate launch.
- Provider PASS is typed evidence, never universal scientific/canonical validation.
- P0 has no FastAPI/Web, Celery/Temporal/Redis/Kafka, graph/vector DB, dynamic plugin loader, production publication, or provider-specific scientific code in Core.
- No local Mac build/deploy. Verification is performed through repository CI and the designated remote/test runtime when available.

---

## File Map Locked by This Plan

```text
pyproject.toml
.github/workflows/ci.yml
alembic.ini
migrations/env.py
migrations/versions/0001_p0_kernel.py
src/bioharness/__init__.py
src/bioharness/settings.py
src/bioharness/domain/base.py
src/bioharness/domain/task.py
src/bioharness/domain/data.py
src/bioharness/domain/assessment.py
src/bioharness/domain/policy.py
src/bioharness/domain/run.py
src/bioharness/domain/artifact.py
src/bioharness/domain/validation.py
src/bioharness/domain/memory.py
src/bioharness/identity/canonical.py
src/bioharness/identity/projections.py
src/bioharness/ports/data_provider.py
src/bioharness/ports/workflow_executor.py
src/bioharness/ports/policy.py
src/bioharness/ports/repositories.py
src/bioharness/adapters/postgres/base.py
src/bioharness/adapters/postgres/models.py
src/bioharness/adapters/postgres/session.py
src/bioharness/adapters/postgres/repositories.py
src/bioharness/adapters/filesystem/artifacts.py
src/bioharness/adapters/local_process/runner.py
src/bioharness/adapters/local_process/probe.py
src/bioharness/application/resolve_task.py
src/bioharness/application/plan_analysis.py
src/bioharness/application/execute_run.py
src/bioharness/application/reconcile_run.py
src/bioharness/application/collect_artifacts.py
src/bioharness/application/validate_run.py
src/bioharness/application/memory.py
src/bioharness/cli/main.py
tests/conftest.py
tests/fakes/providers.py
tests/fakes/factories.py
tests/unit/**
tests/contract/**
tests/integration/**
tests/fixtures/**
```

`examples/reference_integrations/**` is intentionally untouched in this plan.

---

### Task 1: Package Skeleton and Remote CI Baseline

**Files:**
- Create: `pyproject.toml`
- Create: `src/bioharness/__init__.py`
- Create: `src/bioharness/settings.py`
- Create: `tests/unit/test_import.py`
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: none.
- Produces: installable `bioharness` package; frozen `Settings`; PostgreSQL-backed GitHub Actions CI.

- [ ] **Step 1: Write the package smoke test**

```python
# tests/unit/test_import.py
from bioharness import __version__
from bioharness.settings import Settings


def test_package_import_and_settings(tmp_path):
    settings = Settings(
        database_url="postgresql+psycopg://bioharness:bioharness@localhost/bioharness_test",
        run_root=tmp_path / "runs",
        artifact_root=tmp_path / "artifacts",
        protected_roots=(tmp_path / "production",),
    )
    assert __version__ == "0.1.0"
    assert settings.run_root.name == "runs"
```

- [ ] **Step 2: Add package metadata**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"

[project]
name = "bioharness"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "pydantic>=2.9,<3",
  "SQLAlchemy>=2.0,<3",
  "alembic>=1.13,<2",
  "psycopg[binary]>=3.2,<4",
  "typer>=0.12,<1",
  "rfc8785>=0.1,<1",
]

[project.optional-dependencies]
dev = ["pytest>=8,<9"]

[project.scripts]
bioharness = "bioharness.cli.main:app"

[tool.setuptools.packages.find]
where = ["src"]
```

```python
# src/bioharness/__init__.py
__version__ = "0.1.0"
```

```python
# src/bioharness/settings.py
from pathlib import Path
from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    database_url: str
    run_root: Path
    artifact_root: Path
    protected_roots: tuple[Path, ...] = ()
```

- [ ] **Step 3: Add GitHub Actions with PostgreSQL 16**

```yaml
# .github/workflows/ci.yml
name: ci
on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: bioharness
          POSTGRES_PASSWORD: bioharness
          POSTGRES_DB: bioharness_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U bioharness -d bioharness_test"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 20
    env:
      BIOHARNESS_TEST_DATABASE_URL: postgresql+psycopg://bioharness:bioharness@localhost:5432/bioharness_test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: python -m pip install -e '.[dev]'
      - run: python -m pytest -q
```

- [ ] **Step 4: Run in CI**

Run: `python -m pytest tests/unit/test_import.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .github/workflows/ci.yml src/bioharness tests/unit/test_import.py
git commit -m "build: bootstrap BioHarness P0 package and CI"
```

---

### Task 2: Immutable Planning Domain

**Files:**
- Create: `src/bioharness/domain/base.py`
- Create: `src/bioharness/domain/task.py`
- Create: `src/bioharness/domain/data.py`
- Create: `src/bioharness/domain/assessment.py`
- Create: `src/bioharness/domain/policy.py`
- Create: `tests/unit/test_domain_planning.py`

**Interfaces:**
- Produces: `FrozenRecord`, `ScientificTaskSpec`, `ResolvedDataRef`, `ScientificAssessment`, `PolicyRequest`, `PolicyDecision`.

- [ ] **Step 1: Write failing immutability/intent tests**

```python
from datetime import datetime, timezone
from uuid import UUID
import pytest
from pydantic import ValidationError
from bioharness.domain.task import OutputIntent, ScientificTaskSpec

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


def test_task_spec_is_frozen_and_excludes_provider_defaults():
    task = ScientificTaskSpec(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        revision=1,
        question="Build a phylogeny for requested proteins",
        requested_inference="protein phylogeny",
        analysis_class="phylogeny",
        biological_scope={"resources": ["provider://proteome/A"]},
        output_intent=OutputIntent.CANDIDATE,
        unresolved_fields=(),
        created_at=NOW,
    )
    assert "min_seqs" not in type(task).model_fields
    with pytest.raises(ValidationError):
        task.revision = 2
```

- [ ] **Step 2: Implement frozen base and TaskSpec**

```python
# src/bioharness/domain/base.py
from pydantic import BaseModel, ConfigDict


class FrozenRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
```

```python
# src/bioharness/domain/task.py
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID
from pydantic import Field
from .base import FrozenRecord


class OutputIntent(StrEnum):
    EXPLORATORY = "exploratory"
    CANDIDATE = "candidate"
    OFFICIAL = "official"


class ScientificTaskSpec(FrozenRecord):
    id: UUID
    revision: int = Field(ge=1)
    question: str = Field(min_length=1)
    requested_inference: str = Field(min_length=1)
    analysis_class: str = Field(min_length=1)
    biological_scope: dict[str, Any]
    output_intent: OutputIntent
    unresolved_fields: tuple[str, ...] = ()
    created_at: datetime
```

- [ ] **Step 3: Implement resolved-data and assessment records**

```python
# src/bioharness/domain/data.py
from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import Field
from .base import FrozenRecord


class ResolvedDataRef(FrozenRecord):
    id: UUID
    provider: str
    provider_revision: str
    resource_type: str
    logical_uri: str
    content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    manifest_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    member_manifest_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    biological_identity: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    resolved_at: datetime
```

```python
# src/bioharness/domain/assessment.py
from datetime import datetime
from enum import StrEnum
from uuid import UUID
from pydantic import Field
from .base import FrozenRecord


class AssessmentStatus(StrEnum):
    ANALYSIS_SUPPORTED = "ANALYSIS_SUPPORTED"
    ANALYSIS_SUPPORTED_WITH_LIMITATIONS = "ANALYSIS_SUPPORTED_WITH_LIMITATIONS"
    UNRESOLVED = "UNRESOLVED"
    NOT_IDENTIFIABLE = "NOT_IDENTIFIABLE"
    INCOMPATIBLE = "INCOMPATIBLE"


class ScientificAssessment(FrozenRecord):
    id: UUID
    task_spec_id: UUID
    task_spec_revision: int = Field(ge=1)
    resolved_data_ref_ids: tuple[UUID, ...]
    scientific_contract_id: str
    scientific_contract_revision: str
    dependency_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    status: AssessmentStatus
    limitations: tuple[str, ...] = ()
    assessed_at: datetime
```

- [ ] **Step 4: Implement action-scoped policy records**

```python
# src/bioharness/domain/policy.py
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID
from pydantic import Field
from .base import FrozenRecord


class PolicyOutcome(StrEnum):
    ALLOW = "ALLOW"
    ALLOW_WITH_WARNING = "ALLOW_WITH_WARNING"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"


class PolicyRequest(FrozenRecord):
    actor: str
    action: str
    resource: str
    context: dict[str, Any] = Field(default_factory=dict)


class PolicyDecision(FrozenRecord):
    id: UUID
    actor: str
    action: str
    resource: str
    policy_revision: str
    outcome: PolicyOutcome
    warnings: tuple[str, ...] = ()
    obligations: tuple[str, ...] = ()
    decided_at: datetime
```

- [ ] **Step 5: Run and commit**

Run: `python -m pytest tests/unit/test_domain_planning.py -q`

Expected: PASS.

```bash
git add src/bioharness/domain tests/unit/test_domain_planning.py
git commit -m "feat: define immutable scientific planning records"
```

---

### Task 3: Canonical Identity Projections

**Files:**
- Create: `src/bioharness/identity/canonical.py`
- Create: `src/bioharness/identity/projections.py`
- Create: `tests/unit/test_identity.py`

**Interfaces:**
- Produces: `canonical_json_bytes`, `sha256_canonical`, `analysis_projection`, `run_spec_projection`.

- [ ] **Step 1: Write hash tests**

```python
from bioharness.identity.canonical import sha256_canonical
from bioharness.identity.projections import analysis_projection, run_spec_projection


def test_mapping_order_does_not_change_hash():
    assert sha256_canonical({"b": 2, "a": 1}) == sha256_canonical({"a": 1, "b": 2})


def test_validation_profile_changes_run_spec_not_analysis_identity():
    analysis = analysis_projection(
        task_semantics={"inference": "phylogeny"},
        input_identities=({"sha256": "a" * 64},),
        workflow_identity={"provider": "fake", "revision": "r1"},
        result_affecting_parameters={"seed": 7},
        environment_contract={"python": "3.12"},
        reproducibility={"class": "SEEDED_STOCHASTIC", "seed": 7},
    )
    run_a = run_spec_projection(analysis, {"id": "candidate", "revision": "1"}, {"project": "p1"})
    run_b = run_spec_projection(analysis, {"id": "candidate", "revision": "2"}, {"project": "p1"})
    assert sha256_canonical(run_a) != sha256_canonical(run_b)
    assert sha256_canonical(analysis) == sha256_canonical(analysis)
```

- [ ] **Step 2: Implement RFC 8785 canonical hashing**

```python
# src/bioharness/identity/canonical.py
import hashlib
import rfc8785


def canonical_json_bytes(value: object) -> bytes:
    return rfc8785.dumps(value)


def sha256_canonical(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
```

- [ ] **Step 3: Implement explicit versioned projections**

```python
# src/bioharness/identity/projections.py
from typing import Any

ANALYSIS_PROJECTION_VERSION = "bioharness.analysis.v1"
RUN_SPEC_PROJECTION_VERSION = "bioharness.runspec.v1"


def analysis_projection(*, task_semantics: dict[str, Any], input_identities: tuple[dict[str, Any], ...], workflow_identity: dict[str, Any], result_affecting_parameters: dict[str, Any], environment_contract: dict[str, Any], reproducibility: dict[str, Any]) -> dict[str, Any]:
    return {
        "projection_version": ANALYSIS_PROJECTION_VERSION,
        "task_semantics": task_semantics,
        "input_identities": list(input_identities),
        "workflow_identity": workflow_identity,
        "result_affecting_parameters": result_affecting_parameters,
        "environment_contract": environment_contract,
        "reproducibility": reproducibility,
    }


def run_spec_projection(analysis: dict[str, Any], validation_profile: dict[str, Any], control_context: dict[str, Any]) -> dict[str, Any]:
    return {
        "projection_version": RUN_SPEC_PROJECTION_VERSION,
        "analysis": analysis,
        "validation_profile": validation_profile,
        "control_context": control_context,
    }
```

- [ ] **Step 4: Run and commit**

Run: `python -m pytest tests/unit/test_identity.py -q`

Expected: PASS.

```bash
git add src/bioharness/identity tests/unit/test_identity.py
git commit -m "feat: add canonical analysis and run spec identity"
```

---

### Task 4: Stable Ports and Shared Test Fakes

**Files:**
- Create: `src/bioharness/ports/data_provider.py`
- Create: `src/bioharness/ports/workflow_executor.py`
- Create: `src/bioharness/ports/policy.py`
- Create: `tests/fakes/providers.py`
- Create: `tests/fakes/factories.py`
- Create: `tests/contract/test_ports.py`

**Interfaces:**
- Produces: `DataProvider`, `WorkflowExecutor`, `ProcessRunner`, `PolicyEvaluator`, `ProviderResource`, `ProviderResolution`, `ExecutorCapabilities`, `InvocationSpec`, `ExecutionBinding`, `ExecutionEvidence`.

- [ ] **Step 1: Define DataProvider records/protocol**

```python
# src/bioharness/ports/data_provider.py
from typing import Any, Protocol
from pydantic import Field
from bioharness.domain.base import FrozenRecord


class ProviderResource(FrozenRecord):
    logical_uri: str
    resource_type: str
    biological_identity: dict[str, Any]
    content_identity: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderResolution(FrozenRecord):
    provider: str
    provider_revision: str
    resources: tuple[ProviderResource, ...]
    evidence: tuple[dict[str, Any], ...] = ()


class DataProvider(Protocol):
    def resolve(self, logical_resources: tuple[str, ...], context: dict[str, Any]) -> ProviderResolution: ...
```

- [ ] **Step 2: Define executor/process contracts**

```python
# src/bioharness/ports/workflow_executor.py
from pathlib import Path
from typing import Any, Protocol
from pydantic import Field
from bioharness.domain.base import FrozenRecord


class ExecutorCapabilities(FrozenRecord):
    mode: str
    native_idempotency_key: bool
    durable_external_execution_id: bool
    poll: bool
    reconcile_after_disconnect: str
    cancellation: str
    logs: bool
    trace: bool


class InvocationSpec(FrozenRecord):
    argv: tuple[str, ...]
    cwd: Path
    env: dict[str, str]
    stdout_path: Path
    stderr_path: Path


class ExecutionBinding(FrozenRecord):
    host: str
    pid: int | None
    process_start_token: str | None
    external_execution_id: str | None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionEvidence(FrozenRecord):
    active: bool | None
    terminal_outcome: str | None
    exit_code: int | None
    evidence: tuple[dict[str, Any], ...] = ()


class WorkflowExecutor(Protocol):
    def capabilities(self) -> ExecutorCapabilities: ...
    def prepare(self, run_spec_payload: dict[str, Any], attempt_payload: dict[str, Any]) -> InvocationSpec: ...
    def inspect(self, binding: ExecutionBinding, attempt_payload: dict[str, Any]) -> ExecutionEvidence: ...
    def discover_artifacts(self, attempt_payload: dict[str, Any]) -> tuple[dict[str, Any], ...]: ...


class ProcessRunner(Protocol):
    def spawn(self, invocation: InvocationSpec) -> ExecutionBinding: ...
```

- [ ] **Step 3: Define policy port**

```python
# src/bioharness/ports/policy.py
from typing import Any, Protocol
from bioharness.domain.policy import PolicyDecision


class PolicyEvaluator(Protocol):
    def evaluate(self, actor: str, action: str, resource: str, context: dict[str, Any]) -> PolicyDecision: ...
```

- [ ] **Step 4: Implement deterministic fakes/factories**

`tests/fakes/providers.py` defines `FakeDataProvider`, `FakeWorkflowExecutor`, `FakeProcessRunner`, `FakePolicyEvaluator`. Each exposes a `.calls` list. `FakeProcessRunner` exposes `.spawn_calls`. `FakeWorkflowExecutor` exposes `.prepare_calls`. No fake imports Genome-web.

`tests/fakes/factories.py` defines `make_task()`, `make_data_ref()`, `make_run_spec()` using fixed timestamps and UUIDs by default so hash/repository tests are repeatable.

- [ ] **Step 5: Test explicit capabilities and action-scoped policy**

```python
from tests.fakes.providers import FakePolicyEvaluator, FakeWorkflowExecutor


def test_fake_executor_declares_no_unearned_guarantees():
    caps = FakeWorkflowExecutor().capabilities()
    assert caps.native_idempotency_key is False
    assert caps.durable_external_execution_id is False
    assert caps.poll is False


def test_policy_is_action_scoped():
    policy = FakePolicyEvaluator(denied_actions={"publish"})
    assert policy.evaluate("alice", "launch", "runspec:1", {}).outcome.value == "ALLOW"
    assert policy.evaluate("alice", "publish", "artifact:1", {}).outcome.value == "DENY"
```

- [ ] **Step 6: Run and commit**

Run: `python -m pytest tests/contract/test_ports.py -q`

Expected: PASS.

```bash
git add src/bioharness/ports tests/fakes tests/contract/test_ports.py
git commit -m "feat: define provider executor process and policy seams"
```

---

### Task 5: Run, Artifact, Validation, and Memory Domain

**Files:**
- Create: `src/bioharness/domain/run.py`
- Create: `src/bioharness/domain/artifact.py`
- Create: `src/bioharness/domain/validation.py`
- Create: `src/bioharness/domain/memory.py`
- Create: `tests/unit/test_run_domain.py`

**Interfaces:**
- Produces: immutable run/config/context/evidence records and transition rules.

- [ ] **Step 1: Define attempt state transition tests**

```python
from bioharness.domain.run import RunAttemptState, allowed_transition


def test_finished_is_execution_not_validation_state():
    assert allowed_transition(RunAttemptState.COLLECTING, RunAttemptState.FINISHED)


def test_unknown_cannot_be_resubmitted_in_place():
    assert not allowed_transition(RunAttemptState.UNKNOWN, RunAttemptState.SUBMITTING)
```

- [ ] **Step 2: Implement states and transition map**

```python
class RunAttemptState(StrEnum):
    SUBMITTING = "SUBMITTING"
    RUNNING = "RUNNING"
    COLLECTING = "COLLECTING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    NEEDS_OPERATOR_RECONCILIATION = "NEEDS_OPERATOR_RECONCILIATION"
```

Allowed transitions are exactly:

```text
SUBMITTING -> RUNNING | FAILED | UNKNOWN
RUNNING -> COLLECTING | FAILED | UNKNOWN
COLLECTING -> FINISHED | FAILED | UNKNOWN
UNKNOWN -> RUNNING | COLLECTING | FINISHED | FAILED | NEEDS_OPERATOR_RECONCILIATION
NEEDS_OPERATOR_RECONCILIATION -> RUNNING | COLLECTING | FINISHED | FAILED
FINISHED -> none
FAILED -> none
```

- [ ] **Step 3: Implement stable run records**

`ResolvedConfiguration`, `ContextSnapshot`, `RunSpec`, `RunAttempt`, and `RunEvent` fields are exactly those in the design spec. `RunAttempt.binding` is `ExecutionBinding | None`. `RunEvent.event_type` is a StrEnum containing the durable event names from the spec.

- [ ] **Step 4: Implement Artifact, Validation, Memory models**

Add:

```text
Artifact(id, run_spec_id, run_attempt_id, role, content_sha256, size_bytes, uri, metadata, registered_at)
ValidationReport(id, kind, subject_type, subject_id, validator, validator_revision, outcome, limitations, evidence_refs, created_at)
ValidationRequirement(kind, allowed_outcomes)
ValidationProfile(profile_id, revision, requirements)
ValidationEvaluation(id, profile_id, profile_revision, report_ids, outcome, evaluated_at)
MemoryCandidate(id, scope, kind, statement, tags, applicability, evidence_refs, status, created_at)
```

`MemoryCandidate.evidence_refs` must have `min_length=1`.

- [ ] **Step 5: Run and commit**

Run: `python -m pytest tests/unit/test_run_domain.py -q`

Expected: PASS.

```bash
git add src/bioharness/domain tests/unit/test_run_domain.py
git commit -m "feat: define run evidence validation and memory records"
```

---

### Task 6: PostgreSQL Schema, Migration, UoW, and Shared DB Fixtures

**Files:**
- Create: `src/bioharness/adapters/postgres/base.py`
- Create: `src/bioharness/adapters/postgres/session.py`
- Create: `src/bioharness/adapters/postgres/models.py`
- Create: `src/bioharness/adapters/postgres/repositories.py`
- Create: `src/bioharness/ports/repositories.py`
- Create: `alembic.ini`
- Create: `migrations/env.py`
- Create: `migrations/versions/0001_p0_kernel.py`
- Create: `tests/conftest.py`
- Create: `tests/integration/test_postgres_schema.py`

**Interfaces:**
- Produces: `PostgresUnitOfWork(database_url)`, planning/run/artifact/validation/memory repositories, migrated DB fixture.

- [ ] **Step 1: Define `tests/conftest.py` DB fixture**

```python
import os
import subprocess
import pytest


@pytest.fixture(scope="session")
def database_url() -> str:
    return os.environ["BIOHARNESS_TEST_DATABASE_URL"]


@pytest.fixture
def migrated_database(database_url: str):
    subprocess.run(["alembic", "downgrade", "base"], check=True)
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    yield database_url
```

No test uses SQLite as a substitute for concurrency/locking semantics.

- [ ] **Step 2: Create SQLAlchemy base/session factory and all P0 tables**

Use PostgreSQL UUID, JSONB, timezone-aware timestamps. Immutable records store validated snapshot JSONB plus query-critical columns. `run_attempts` owns mutable current state; `run_events` is append-only.

- [ ] **Step 3: Enforce minimum DB constraints**

```text
run_specs.run_spec_hash UNIQUE
run_attempts(run_spec_id, attempt_number) UNIQUE
run_attempts.submission_key UNIQUE
run_attempts(executor_namespace, provider_attempt_name) UNIQUE
run_events(run_attempt_id, sequence_no) UNIQUE
validation_profiles(profile_id, revision) UNIQUE
analysis_hash INDEX, not UNIQUE
```

- [ ] **Step 4: Implement repository/UoW interfaces**

```python
# src/bioharness/ports/repositories.py
from typing import Protocol


class UnitOfWork(Protocol):
    planning: object
    runs: object
    artifacts: object
    validation: object
    memory: object
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
```

`PostgresUnitOfWork` owns one Session and exposes only `add/get/list` for immutable records. RunAttempt state updates occur only through run-specific transition methods that append a RunEvent in the same transaction.

- [ ] **Step 5: Test unique constraints directly**

Create one RunSpec using `tests.fakes.factories.make_run_spec()`, persist it, then attempt duplicate `run_spec_hash`; expect `IntegrityError`. Create one attempt, then duplicate `submission_key`; expect `IntegrityError`.

- [ ] **Step 6: Run and commit**

Run:

```bash
alembic upgrade head
python -m pytest tests/integration/test_postgres_schema.py -q
```

Expected: PASS.

```bash
git add alembic.ini migrations src/bioharness/adapters/postgres src/bioharness/ports/repositories.py tests/conftest.py tests/integration/test_postgres_schema.py
git commit -m "feat: add authoritative PostgreSQL persistence"
```

---

### Task 7: Authorized Resolution and Deterministic Planning

**Files:**
- Create: `src/bioharness/application/resolve_task.py`
- Create: `src/bioharness/application/plan_analysis.py`
- Create: `tests/contract/test_planning_service.py`

**Interfaces:**
- Produces:
  - `ResolutionService.resolve(task_id: UUID, actor: str) -> tuple[ResolvedDataRef, ...]`
  - `PlanningService.publish_run_spec(...) -> RunSpec`

- [ ] **Step 1: Write AUTH-02 order test without undefined fixtures**

Construct `FakePolicyEvaluator`, `FakeDataProvider`, and an in-memory spy repository in the test. The fake policy and provider each append `("policy", action)` / `("provider", "resolve")` into the same `order` list. Assert policy `read_resolve` appears before provider `resolve`.

- [ ] **Step 2: Implement `ResolutionService.resolve`**

Algorithm:

```text
load TaskSpec
-> current PolicyEvaluator.evaluate(actor, "read_resolve", task resource, context)
-> if DENY/REQUIRE_APPROVAL: stop before DataProvider.resolve
-> DataProvider.resolve
-> convert ProviderResource records to ResolvedDataRef records
-> persist current PolicyDecision and ResolvedDataRefs
```

The conversion copies provider/resource identity; BioHarness never invents missing biological identifiers.

- [ ] **Step 3: Implement assessment dependency fingerprint**

```python
sha256_canonical({
    "projection_version": "bioharness.assessment-deps.v1",
    "task_spec": {"id": str(task.id), "revision": task.revision},
    "resolved_data_refs": [str(ref.id) for ref in sorted(refs, key=lambda x: str(x.id))],
    "scientific_contract": {"id": contract_id, "revision": contract_revision},
    "assumption_constraints": assumption_constraints,
})
```

- [ ] **Step 4: Implement `PlanningService.publish_run_spec`**

Inputs include explicit provider/workflow identity, result-affecting parameters, environment contract, reproducibility contract, validation profile ref, expected outputs, and current assessment. Refuse publication for `UNRESOLVED`, `NOT_IDENTIFIABLE`, or `INCOMPATIBLE`. Compute `analysis_hash` and `run_spec_hash` from Task 3 functions, then persist ResolvedConfiguration, ContextSnapshot, and RunSpec.

- [ ] **Step 5: Test assumption-relevant change invalidation**

Create assessment dependency fingerprint for constraint `{"model": "A"}`. Attempt to publish configuration with `{"model": "B"}` marked assumption-relevant. Assert `AssessmentDependencyMismatch` and no RunSpec row.

- [ ] **Step 6: Run and commit**

Run: `python -m pytest tests/contract/test_planning_service.py -q`

Expected: PASS.

```bash
git add src/bioharness/application/resolve_task.py src/bioharness/application/plan_analysis.py tests/contract/test_planning_service.py
git commit -m "feat: add authorized deterministic planning flow"
```

---

### Task 8: RunAttempt Allocation and Intent-Before-Side-Effect

**Files:**
- Modify: `src/bioharness/adapters/postgres/repositories.py`
- Create: `src/bioharness/application/execute_run.py`
- Create: `tests/integration/test_attempt_allocation.py`
- Create: `tests/contract/test_execution_intent.py`

**Interfaces:**
- `ExecutionService(policy, executor, process_runner, uow_factory)`
- `ExecutionService.start(run_spec_id: UUID, actor: str) -> RunAttempt`

- [ ] **Step 1: Write concurrent allocation test**

Use `ThreadPoolExecutor(max_workers=2)` with two independent PostgreSQL UoWs targeting the same RunSpec. Both call `runs.allocate_attempt_intent(...)`. Assert attempt numbers are exactly `{1, 2}`.

- [ ] **Step 2: Implement allocation under `SELECT ... FOR UPDATE`**

Within one transaction:

```text
lock RunSpec row
allocate next attempt_number
persist current launch PolicyDecision
insert RunAttempt state=SUBMITTING
append AttemptCreated seq=1
append AuthorizationChecked seq=2
append SubmissionIntentRecorded seq=3
commit
```

No file hash or process call occurs inside this transaction.

- [ ] **Step 3: Write AUTH-01 launch test with explicit fakes**

```python
policy = FakePolicyEvaluator(denied_actions={"launch"})
executor = FakeWorkflowExecutor()
runner = FakeProcessRunner()
service = ExecutionService(policy=policy, executor=executor, process_runner=runner, uow_factory=uow_factory)
with pytest.raises(LaunchDenied):
    service.start(run_spec.id, actor="alice")
assert executor.prepare_calls == 0
assert runner.spawn_calls == 0
```

- [ ] **Step 4: Implement phase-0 preflight and fresh launch authorization**

Before the allocation transaction, recheck frozen input identities/environment identity and protected roots. Then evaluate fresh current launch policy; never reuse ContextSnapshot authorization.

- [ ] **Step 5: Run and commit**

Run:

```bash
python -m pytest tests/integration/test_attempt_allocation.py tests/contract/test_execution_intent.py -q
```

Expected: PASS.

```bash
git add src/bioharness/application/execute_run.py src/bioharness/adapters/postgres/repositories.py tests/integration/test_attempt_allocation.py tests/contract/test_execution_intent.py
git commit -m "feat: persist launch intent before external execution"
```

---

### Task 9: Generic Local Process Runner and Ambiguous-Bind Handling

**Files:**
- Create: `src/bioharness/adapters/local_process/runner.py`
- Create: `src/bioharness/adapters/local_process/probe.py`
- Modify: `src/bioharness/application/execute_run.py`
- Create: `tests/unit/test_local_process.py`
- Create: `tests/contract/test_unknown_submission.py`

**Interfaces:**
- `LocalProcessRunner.spawn(InvocationSpec) -> ExecutionBinding`
- `LocalProcessProbe.probe(ExecutionBinding) -> bool | None`

- [ ] **Step 1: Write local-process binding test**

Use `sys.executable -c 'import time; time.sleep(2)'`. Assert returned binding has hostname/PID and a `/proc/<pid>/stat` start token on Linux.

- [ ] **Step 2: Implement runner**

```python
subprocess.Popen(
    invocation.argv,
    cwd=invocation.cwd,
    env=invocation.env,
    stdout=stdout_handle,
    stderr=stderr_handle,
    start_new_session=True,
)
```

Never use `shell=True`. Create output parents before spawn. Read Linux `/proc/<pid>/stat` field 22 for the start token; if `/proc` is unavailable, set it to `None` and reconciliation becomes weaker rather than inventing identity.

- [ ] **Step 3: Complete `ExecutionService.start` phase B**

After committed submission intent:

```text
executor.prepare(...)
-> process_runner.spawn(invocation)
-> atomically persist binding + RUNNING
-> append ExternalProcessBound + ExecutionStarted
```

Known failure before process creation -> FAILED. Ambiguity after possible process creation/bind -> UNKNOWN + `ExecutionOutcomeUnknown`. Never auto-create a second attempt.

- [ ] **Step 4: Write ambiguous bind test**

Use `FakeProcessRunner(raise_after_possible_spawn=True)`. Assert one RunAttempt remains UNKNOWN, one runner call occurred, and executor.prepare was called once.

- [ ] **Step 5: Run and commit**

Run:

```bash
python -m pytest tests/unit/test_local_process.py tests/contract/test_unknown_submission.py -q
```

Expected: PASS.

```bash
git add src/bioharness/adapters/local_process src/bioharness/application/execute_run.py tests/unit/test_local_process.py tests/contract/test_unknown_submission.py
git commit -m "feat: add crash-aware local process execution"
```

---

### Task 10: Conservative Reconciliation

**Files:**
- Create: `src/bioharness/application/reconcile_run.py`
- Modify: `src/bioharness/application/execute_run.py`
- Modify: `src/bioharness/adapters/local_process/probe.py`
- Create: `tests/contract/test_reconciliation.py`

**Interfaces:**
- `ReconciliationService.reconcile(attempt_id: UUID, actor: str) -> RunAttempt`

- [ ] **Step 1: Test reconciliation matrix**

```text
active=True with matching identity -> RUNNING
terminal_outcome=succeeded exit=0 -> COLLECTING
terminal_outcome=failed exit!=0 -> FAILED
no conclusive evidence -> NEEDS_OPERATOR_RECONCILIATION
PID exists but start token mismatches -> NEEDS_OPERATOR_RECONCILIATION
```

- [ ] **Step 2: Implement process identity probe**

PID existence without a matching recorded start token is not proof of the same process. Return indeterminate (`None`) on mismatch/unverifiable identity.

- [ ] **Step 3: Implement reconciliation service**

Combine RunAttempt history, process probe, and `WorkflowExecutor.inspect`. Transition state and append `ReconciliationResolved` or `ReconciliationRequired` in the same DB transaction.

- [ ] **Step 4: Block start while unresolved attempt exists**

`ExecutionService.start` must raise `PriorAttemptUnresolved` when any attempt for the RunSpec is `UNKNOWN` or `NEEDS_OPERATOR_RECONCILIATION`.

- [ ] **Step 5: Run and commit**

Run: `python -m pytest tests/contract/test_reconciliation.py -q`

Expected: PASS.

```bash
git add src/bioharness/application/reconcile_run.py src/bioharness/application/execute_run.py src/bioharness/adapters/local_process/probe.py tests/contract/test_reconciliation.py
git commit -m "feat: add conservative run reconciliation"
```

---

### Task 11: Immutable Artifact Collection

**Files:**
- Create: `src/bioharness/adapters/filesystem/artifacts.py`
- Create: `src/bioharness/application/collect_artifacts.py`
- Create: `tests/unit/test_artifact_store.py`
- Create: `tests/contract/test_artifact_collection.py`

**Interfaces:**
- `inspect_artifact(path: Path, role: str) -> ArtifactInspection`
- `ArtifactCollectionService.collect(attempt_id: UUID) -> tuple[Artifact, ...]`

- [ ] **Step 1: Write SHA-256 test**

```python
def test_inspect_artifact_hashes_bytes(tmp_path):
    p = tmp_path / "result.txt"
    p.write_text("abc", encoding="utf-8")
    record = inspect_artifact(p, role="result")
    assert record.content_sha256 == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert record.size_bytes == 3
```

- [ ] **Step 2: Implement 1 MiB streaming digest**

Reject artifact candidates outside configured allowed run/artifact roots. Do not load large scientific files fully into memory.

- [ ] **Step 3: Implement collection service**

Ask `WorkflowExecutor.discover_artifacts`, register each immutable artifact with digest, append `ArtifactDiscovered` and `ArtifactRegistered`, then transition COLLECTING -> FINISHED. Execution FINISHED remains independent from validation.

- [ ] **Step 4: Run and commit**

Run:

```bash
python -m pytest tests/unit/test_artifact_store.py tests/contract/test_artifact_collection.py -q
```

Expected: PASS.

```bash
git add src/bioharness/adapters/filesystem src/bioharness/application/collect_artifacts.py tests/unit/test_artifact_store.py tests/contract/test_artifact_collection.py
git commit -m "feat: register immutable artifact evidence"
```

---

### Task 12: Typed, Versioned Validation

**Files:**
- Create: `src/bioharness/application/validate_run.py`
- Modify: `src/bioharness/adapters/postgres/repositories.py`
- Create: `tests/contract/test_validation.py`

**Interfaces:**
- `ValidationService.report(...) -> ValidationReport`
- `ValidationService.evaluate(profile_id: str, revision: str, report_ids: tuple[UUID, ...]) -> ValidationEvaluation`

- [ ] **Step 1: Define generic `candidate@1` profile in test setup**

Requirements:

```text
provider_contract: PASS | PASS_WITH_LIMITATIONS
artifact_integrity: PASS
provenance_completeness: PASS
```

- [ ] **Step 2: Write VAL-01/VAL-02 tests using an explicit service/repository**

Create only a `provider_contract=PASS` report and evaluate `candidate@1`; assert evaluation FAIL because required artifact/provenance reports are absent. Then add all required PASS reports; assert evaluation PASS.

- [ ] **Step 3: Implement validation evaluation**

Each report has one kind. Evaluation stores exact profile revision and report IDs. `PASS_WITH_LIMITATIONS` remains attached to the report and is only accepted when that profile requirement allows it.

- [ ] **Step 4: Test historical revision immutability and no publication**

Create `candidate@2` with an extra requirement. Assert prior `candidate@1` row/evaluation is unchanged. ValidationService has no method that writes CanonicalPointer or production publication in P0.

- [ ] **Step 5: Run and commit**

Run: `python -m pytest tests/contract/test_validation.py -q`

Expected: PASS.

```bash
git add src/bioharness/application/validate_run.py src/bioharness/adapters/postgres/repositories.py tests/contract/test_validation.py
git commit -m "feat: add typed versioned validation gates"
```

---

### Task 13: Evidence-Backed MemoryCandidate

**Files:**
- Create: `src/bioharness/application/memory.py`
- Create: `tests/contract/test_memory.py`

**Interfaces:**
- `MemoryService.record(...) -> MemoryCandidate`
- `MemoryService.search(scope: str, tags: tuple[str, ...], text: str | None = None) -> tuple[MemoryCandidate, ...]`

- [ ] **Step 1: Test required evidence and non-authority**

Attempt record with empty evidence refs; expect validation failure. Record a candidate with evidence refs, retrieve by exact scope/tag, and assert no PolicyDecision/Finding/Canonical record is created.

- [ ] **Step 2: Implement deterministic retrieval**

Filter by scope, all requested exact tags, provider/workflow applicability keys when present, and optional case-insensitive text containment. No vector/graph storage.

- [ ] **Step 3: Run and commit**

Run: `python -m pytest tests/contract/test_memory.py -q`

Expected: PASS.

```bash
git add src/bioharness/application/memory.py tests/contract/test_memory.py
git commit -m "feat: add evidence-backed memory candidates"
```

---

### Task 14: Headless CLI and Core Dependency Guard

**Files:**
- Create: `src/bioharness/cli/__init__.py`
- Create: `src/bioharness/cli/main.py`
- Create: `tests/contract/test_cli.py`
- Create: `tests/contract/test_core_dependency_boundary.py`

**Interfaces:**
- CLI commands: `task create`, `task show`, `plan`, `run start`, `run show`, `run reconcile`, `artifact list`, `validate`, `memory list`.

- [ ] **Step 1: Write Typer command-surface test**

Use `typer.testing.CliRunner`, invoke `--help` for root and command groups, and assert exit code 0 plus the expected commands.

- [ ] **Step 2: Implement thin CLI**

CLI defines the stable command surface and delegates to an injected runtime composition object. Core owns the command/use-case boundary; concrete composition of Settings/UoW with PolicyEvaluator, DataProvider, and WorkflowExecutor adapters is supplied by deployment/reference integration code. It prints JSON containing stable IDs/status. It never imports provider-specific examples or invokes subprocesses directly.

- [ ] **Step 3: Add architecture dependency guard**

Scan `src/bioharness/**/*.py`; fail when executable source contains imports/references to `examples.reference_integrations`, `genome_web`, `deepseek_harness`, or Pi package names. This is a dependency-direction guard, not a ban on architecture documentation outside `src`.

- [ ] **Step 4: Run and commit**

Run:

```bash
python -m pytest tests/contract/test_cli.py tests/contract/test_core_dependency_boundary.py -q
```

Expected: PASS.

```bash
git add src/bioharness/cli tests/contract/test_cli.py tests/contract/test_core_dependency_boundary.py
git commit -m "feat: expose headless BioHarness P0 CLI"
```

---

### Task 15: Provider-Agnostic End-to-End Vertical Slice

**Files:**
- Create: `tests/fixtures/fake_science_provider.py`
- Create: `tests/integration/test_p0_vertical_slice.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Produces: executable Core acceptance evidence using only a fake external provider.

- [ ] **Step 1: Implement deterministic fake process**

`fake_science_provider.py` accepts `--input`, `--outdir`, `--mode success|fail`. Success writes `result.txt` and `provider_evidence.json`, exits 0. Failure writes stderr and exits 9. It contains no Genome-web/TF logic.

- [ ] **Step 2: Write complete success flow**

Test:

```text
ScientificTaskSpec
-> current read authorization
-> FakeDataProvider.resolve
-> ResolvedDataRefs
-> ScientificAssessment
-> ResolvedConfiguration
-> RunSpec hashes
-> current launch authorization
-> RunAttempt intent transaction
-> fake external process
-> Artifact registration
-> provider_contract + artifact_integrity + provenance_completeness reports
-> candidate@1 ValidationEvaluation PASS
-> MemoryCandidate record/retrieval
```

Assert one RunSpec, one RunAttempt, ordered RunEvents, correct artifact digest, no canonical/publication record, no authority escalation from MemoryCandidate.

- [ ] **Step 3: Write unknown-outcome flow**

Use `FakeProcessRunner(raise_after_possible_spawn=True)`. Assert UNKNOWN, no second spawn, and new start blocked until reconciliation.

- [ ] **Step 4: Run complete Core suite in CI**

```bash
alembic upgrade head
python -m pytest tests/unit tests/contract tests/integration -q
```

Expected: PASS without Genome-web, Nextflow, MAFFT, IQ-TREE, Pi, or DeepSeek Harness installed.

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/fake_science_provider.py tests/integration/test_p0_vertical_slice.py .github/workflows/ci.yml
git commit -m "test: prove provider-agnostic P0 vertical slice"
```

---

## Plan Completion Gate

Before declaring this plan implemented:

1. Fresh CI on the implementation head must pass `tests/unit`, `tests/contract`, and `tests/integration` against PostgreSQL 16.
2. Core dependency-boundary test must prove Genome-web reference code is not imported by `src/bioharness`.
3. Fake-provider vertical slice must prove current authorization, durable submission intent, unknown handling, immutable artifacts, typed validation, and non-authoritative memory.
4. Do not mark Genome-web TF scenarios PASS from this plan; they remain `NOT_RUN` until the separate reference plan executes.
5. Do not claim production readiness, publication support, remote schedulers, durable cancellation, or provider exactly-once guarantees.

## Follow-On Plan Boundary

After Core passes this plan, execute `docs/superpowers/plans/2026-09-18-genome-web-tf-reference-integration.md`. That plan may depend on BioHarness public contracts and the external Genome-web repository; BioHarness Core must never depend on it.
