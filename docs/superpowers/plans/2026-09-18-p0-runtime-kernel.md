# BioHarness P0 Runtime Kernel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first provider-agnostic BioHarness Research Control Plane kernel that can plan, authorize, execute, reconcile, register evidence, validate, and recall one governed scientific run without depending on Genome-web or any agent runtime.

**Architecture:** Implement a Python modular monolith under `src/bioharness` with immutable Pydantic domain records, explicit ports, SQLAlchemy/PostgreSQL persistence, and a generic local-process primitive. Core tests use deterministic fake providers/processes. Genome-web TF is explicitly excluded from this plan and is handled by the separate reference-integration plan after Core is working.

**Tech Stack:** Python 3.12+, Pydantic 2, SQLAlchemy 2, Alembic, psycopg 3, PostgreSQL, Typer, pytest, rfc8785, Python stdlib.

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

Core files created by this plan:

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
```

Core tests:

```text
tests/unit/
tests/contract/
tests/integration/
tests/fixtures/
tests/fakes/
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
- Produces: installable package `bioharness`; `Settings(database_url, run_root, artifact_root, protected_roots)`; remote pytest/PostgreSQL CI used by all later tasks.

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

- [ ] **Step 2: Add the package metadata and dependencies**

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
        ports:
          - 5432:5432
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

- [ ] **Step 4: Run the smoke test remotely**

Run in CI: `python -m pytest tests/unit/test_import.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .github/workflows/ci.yml src/bioharness tests/unit/test_import.py
git commit -m "build: bootstrap BioHarness P0 package and CI"
```

---

### Task 2: Immutable Scientific Planning Domain

**Files:**
- Create: `src/bioharness/domain/base.py`
- Create: `src/bioharness/domain/task.py`
- Create: `src/bioharness/domain/data.py`
- Create: `src/bioharness/domain/assessment.py`
- Create: `src/bioharness/domain/policy.py`
- Create: `tests/unit/test_domain_planning.py`

**Interfaces:**
- Consumes: Pydantic 2.
- Produces: `FrozenRecord`, `ScientificTaskSpec`, `ResolvedDataRef`, `ScientificAssessment`, `PolicyRequest`, `PolicyDecision`.

- [ ] **Step 1: Write failing tests for immutability and intent/config separation**

```python
# tests/unit/test_domain_planning.py
from datetime import datetime, timezone
from uuid import UUID
import pytest
from pydantic import ValidationError

from bioharness.domain.task import OutputIntent, ScientificTaskSpec

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


def test_task_spec_is_frozen_and_has_no_provider_defaults():
    task = ScientificTaskSpec(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        revision=1,
        question="Build a phylogeny for the requested proteins",
        requested_inference="protein phylogeny",
        analysis_class="phylogeny",
        biological_scope={"resources": ["provider://proteome/A"]},
        output_intent=OutputIntent.CANDIDATE,
        unresolved_fields=(),
        created_at=NOW,
    )
    assert "min_seqs" not in task.model_fields
    with pytest.raises(ValidationError):
        task.revision = 2
```

- [ ] **Step 2: Implement the immutable base and TaskSpec**

```python
# src/bioharness/domain/base.py
from pydantic import BaseModel, ConfigDict


class FrozenRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", use_enum_values=False)
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

- [ ] **Step 3: Add resolved-data and assessment records**

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
    metadata: dict[str, Any] = {}
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

- [ ] **Step 4: Add action-scoped policy records**

```python
# src/bioharness/domain/policy.py
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID
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
    context: dict[str, Any] = {}


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

- [ ] **Step 5: Run domain tests**

Run: `python -m pytest tests/unit/test_domain_planning.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/bioharness/domain tests/unit/test_domain_planning.py
git commit -m "feat: define immutable scientific planning records"
```

---

### Task 3: Canonical Identity and Hash Projections

**Files:**
- Create: `src/bioharness/identity/canonical.py`
- Create: `src/bioharness/identity/projections.py`
- Create: `tests/unit/test_identity.py`

**Interfaces:**
- Consumes: JSON-compatible dictionaries.
- Produces: `canonical_json_bytes(value)`, `sha256_canonical(value)`, `analysis_projection(...)`, `run_spec_projection(...)`.

- [ ] **Step 1: Write deterministic hash tests**

```python
# tests/unit/test_identity.py
from bioharness.identity.canonical import sha256_canonical
from bioharness.identity.projections import analysis_projection, run_spec_projection


def test_canonical_hash_ignores_mapping_order():
    assert sha256_canonical({"b": 2, "a": 1}) == sha256_canonical({"a": 1, "b": 2})


def test_validation_profile_changes_run_spec_not_analysis_identity():
    base = analysis_projection(
        task_semantics={"inference": "phylogeny"},
        input_identities=({"sha256": "a" * 64},),
        workflow_identity={"provider": "fake", "revision": "r1"},
        result_affecting_parameters={"seed": 7},
        environment_contract={"python": "3.12"},
        reproducibility={"class": "SEEDED_STOCHASTIC", "seed": 7},
    )
    a = run_spec_projection(base, {"profile_id": "candidate", "revision": "1"}, {"project": "p1"})
    b = run_spec_projection(base, {"profile_id": "candidate", "revision": "2"}, {"project": "p1"})
    assert sha256_canonical(base) == sha256_canonical(base)
    assert sha256_canonical(a) != sha256_canonical(b)
```

- [ ] **Step 2: Implement RFC 8785 hashing**

```python
# src/bioharness/identity/canonical.py
import hashlib
import rfc8785


def canonical_json_bytes(value: object) -> bytes:
    return rfc8785.dumps(value)


def sha256_canonical(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
```

- [ ] **Step 3: Implement versioned projections**

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

- [ ] **Step 4: Run identity tests**

Run: `python -m pytest tests/unit/test_identity.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/bioharness/identity tests/unit/test_identity.py
git commit -m "feat: add canonical analysis and run spec identity"
```

---

### Task 4: Provider, Executor, and Policy Ports with Deterministic Fakes

**Files:**
- Create: `src/bioharness/ports/data_provider.py`
- Create: `src/bioharness/ports/workflow_executor.py`
- Create: `src/bioharness/ports/policy.py`
- Create: `tests/fakes/providers.py`
- Create: `tests/contract/test_ports.py`

**Interfaces:**
- Consumes: domain records from Tasks 2-3.
- Produces: stable public seams `DataProvider`, `WorkflowExecutor`, `PolicyEvaluator`, `ProviderResolution`, `ExecutorCapabilities`, `InvocationSpec`, `ExecutionEvidence`.

- [ ] **Step 1: Write port contract tests using fakes**

```python
# tests/contract/test_ports.py
from tests.fakes.providers import FakeDataProvider, FakePolicyEvaluator, FakeWorkflowExecutor


def test_fake_executor_declares_capabilities_explicitly():
    executor = FakeWorkflowExecutor()
    caps = executor.capabilities()
    assert caps.native_idempotency_key is False
    assert caps.durable_external_execution_id is False
    assert caps.poll is False


def test_policy_is_action_scoped():
    policy = FakePolicyEvaluator(denied_actions={"publish"})
    assert policy.evaluate("alice", "launch", "runspec:1", {}).outcome.value == "ALLOW"
    assert policy.evaluate("alice", "publish", "artifact:1", {}).outcome.value == "DENY"
```

- [ ] **Step 2: Define the DataProvider contract**

```python
# src/bioharness/ports/data_provider.py
from typing import Any, Protocol
from pydantic import Field
from bioharness.domain.base import FrozenRecord


class ProviderResolution(FrozenRecord):
    provider: str
    provider_revision: str
    resources: tuple[dict[str, Any], ...]
    evidence: tuple[dict[str, Any], ...] = ()


class DataProvider(Protocol):
    def resolve(self, logical_resources: tuple[str, ...], context: dict[str, Any]) -> ProviderResolution: ...
```

- [ ] **Step 3: Define executor capability/evidence contracts**

```python
# src/bioharness/ports/workflow_executor.py
from pathlib import Path
from typing import Any, Protocol
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
    metadata: dict[str, Any] = {}


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
```

- [ ] **Step 4: Define policy port and deterministic fakes**

```python
# src/bioharness/ports/policy.py
from typing import Any, Protocol
from bioharness.domain.policy import PolicyDecision


class PolicyEvaluator(Protocol):
    def evaluate(self, actor: str, action: str, resource: str, context: dict[str, Any]) -> PolicyDecision: ...
```

`tests/fakes/providers.py` must implement all three ports without importing provider-specific production code. Use fixed revisions (`fake-data@1`, `fake-executor@1`, `test-policy@1`) and UUID4 decisions.

- [ ] **Step 5: Run port tests**

Run: `python -m pytest tests/contract/test_ports.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/bioharness/ports tests/fakes tests/contract/test_ports.py
git commit -m "feat: define provider executor and policy seams"
```

---

### Task 5: Run/Validation/Memory Domain Records

**Files:**
- Create: `src/bioharness/domain/run.py`
- Create: `src/bioharness/domain/artifact.py`
- Create: `src/bioharness/domain/validation.py`
- Create: `src/bioharness/domain/memory.py`
- Create: `tests/unit/test_run_domain.py`

**Interfaces:**
- Consumes: `FrozenRecord` and identity hashes.
- Produces: `ResolvedConfiguration`, `ContextSnapshot`, `RunSpec`, `RunAttempt`, `RunEvent`, `Artifact`, `ValidationReport/Profile/Evaluation`, `MemoryCandidate`.

- [ ] **Step 1: Write run identity/state tests**

```python
# tests/unit/test_run_domain.py
from bioharness.domain.run import RunAttemptState, allowed_transition


def test_finished_is_not_validation_state():
    assert allowed_transition(RunAttemptState.COLLECTING, RunAttemptState.FINISHED)


def test_unknown_does_not_transition_directly_to_submitting():
    assert not allowed_transition(RunAttemptState.UNKNOWN, RunAttemptState.SUBMITTING)
```

- [ ] **Step 2: Implement run records and explicit transition table**

`src/bioharness/domain/run.py` must define:

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

The allowed transition map is exactly:

```python
_ALLOWED = {
    RunAttemptState.SUBMITTING: {RunAttemptState.RUNNING, RunAttemptState.FAILED, RunAttemptState.UNKNOWN},
    RunAttemptState.RUNNING: {RunAttemptState.COLLECTING, RunAttemptState.FAILED, RunAttemptState.UNKNOWN},
    RunAttemptState.COLLECTING: {RunAttemptState.FINISHED, RunAttemptState.FAILED, RunAttemptState.UNKNOWN},
    RunAttemptState.UNKNOWN: {RunAttemptState.RUNNING, RunAttemptState.COLLECTING, RunAttemptState.FINISHED, RunAttemptState.FAILED, RunAttemptState.NEEDS_OPERATOR_RECONCILIATION},
    RunAttemptState.NEEDS_OPERATOR_RECONCILIATION: {RunAttemptState.RUNNING, RunAttemptState.COLLECTING, RunAttemptState.FINISHED, RunAttemptState.FAILED},
    RunAttemptState.FINISHED: set(),
    RunAttemptState.FAILED: set(),
}
```

Also define immutable records with the following stable fields:

```text
ResolvedConfiguration: id, provider, provider_revision, workflow_revision, parameters, environment_contract, validation_profile_id, validation_profile_revision, reproducibility, created_at
ContextSnapshot: id, task_spec_id, resolved_data_ref_ids, policy_decision_ids, memory_candidate_ids, limitations, created_at
RunSpec: id, task_spec_id, assessment_id, configuration_id, context_snapshot_id, input_ref_ids, analysis_hash, run_spec_hash, expected_outputs, created_at
RunAttempt: id, run_spec_id, attempt_number, executor, submission_key, provider_attempt_name, state, binding, submitted_at, last_reconciled_at
RunEvent: id, run_attempt_id, sequence_no, event_type, payload, recorded_at
```

- [ ] **Step 3: Implement Artifact, Validation, and MemoryCandidate records**

Required stable fields:

```text
Artifact: id, run_spec_id, run_attempt_id, role, content_sha256, size_bytes, uri, metadata, registered_at
ValidationReport: id, kind, subject_type, subject_id, validator, validator_revision, outcome, limitations, evidence_refs, created_at
ValidationProfile: profile_id, revision, requirements
ValidationEvaluation: id, profile_id, profile_revision, report_ids, outcome, evaluated_at
MemoryCandidate: id, scope, kind, statement, tags, applicability, evidence_refs, status, created_at
```

`ValidationKind` must include `provider_contract`, `artifact_integrity`, `provenance_completeness`, `method_qc`, `scientific_assumptions`, `reproducibility`, `publication_readiness`.

- [ ] **Step 4: Run domain tests**

Run: `python -m pytest tests/unit/test_run_domain.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/bioharness/domain tests/unit/test_run_domain.py
git commit -m "feat: define run evidence validation and memory records"
```

---

### Task 6: PostgreSQL Schema, Migration, and Repository Boundaries

**Files:**
- Create: `src/bioharness/adapters/postgres/base.py`
- Create: `src/bioharness/adapters/postgres/session.py`
- Create: `src/bioharness/adapters/postgres/models.py`
- Create: `src/bioharness/adapters/postgres/repositories.py`
- Create: `src/bioharness/ports/repositories.py`
- Create: `alembic.ini`
- Create: `migrations/env.py`
- Create: `migrations/versions/0001_p0_kernel.py`
- Create: `tests/integration/test_postgres_schema.py`

**Interfaces:**
- Consumes: all immutable domain records.
- Produces: transactional `PostgresUnitOfWork`, repositories for planning, run state/events, artifacts, validation, memory.

- [ ] **Step 1: Write schema constraint tests**

```python
# tests/integration/test_postgres_schema.py
import os
import pytest
from sqlalchemy.exc import IntegrityError
from bioharness.adapters.postgres.session import create_engine_from_url
from bioharness.adapters.postgres.repositories import PostgresUnitOfWork

DB_URL = os.environ["BIOHARNESS_TEST_DATABASE_URL"]


def test_submission_key_is_unique(migrated_database, sample_run_spec):
    with PostgresUnitOfWork(DB_URL) as uow:
        first = uow.runs.create_attempt_intent(sample_run_spec.id, "alice", "sub-1", "attempt-1")
        uow.commit()
    with pytest.raises(IntegrityError):
        with PostgresUnitOfWork(DB_URL) as uow:
            uow.runs.create_attempt_intent(sample_run_spec.id, "alice", "sub-1", "attempt-2")
            uow.commit()
```

- [ ] **Step 2: Define SQLAlchemy base and session factory**

Use SQLAlchemy 2 declarative mappings, PostgreSQL UUID, JSONB, timezone-aware `DateTime`, and explicit named unique constraints.

- [ ] **Step 3: Implement exactly these minimum relational constraints**

```text
run_specs.run_spec_hash                         UNIQUE
run_attempts(run_spec_id, attempt_number)      UNIQUE
run_attempts.submission_key                    UNIQUE
run_attempts(executor_namespace, provider_attempt_name) UNIQUE
run_events(run_attempt_id, sequence_no)        UNIQUE
validation_profiles(profile_id, revision)      UNIQUE
```

`analysis_hash` receives a normal index, not a unique constraint.

- [ ] **Step 4: Create the first migration**

`migrations/versions/0001_p0_kernel.py` must create all P0 tables named in the spec: projects, scientific_task_specs, policy_decisions, resolved_data_refs, scientific_assessments, resolved_configurations, context_snapshots, run_specs, run_attempts, run_events, artifacts, validation_profiles, validation_reports, validation_evaluations, memory_candidates.

Immutable records store a validated JSONB snapshot plus query-critical columns. `run_attempts` stores mutable current state; `run_events` stores immutable transition history.

- [ ] **Step 5: Implement `PostgresUnitOfWork`**

```python
# src/bioharness/ports/repositories.py
from typing import Protocol


class UnitOfWork(Protocol):
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
```

`PostgresUnitOfWork` must expose `.planning`, `.runs`, `.artifacts`, `.validation`, `.memory`, and own one SQLAlchemy Session. Repository methods for immutable record types are `add`/`get`; do not expose generic `update`/`delete`.

- [ ] **Step 6: Run migration and repository tests in CI**

Run:

```bash
alembic upgrade head
python -m pytest tests/integration/test_postgres_schema.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add alembic.ini migrations src/bioharness/adapters/postgres src/bioharness/ports/repositories.py tests/integration/test_postgres_schema.py
git commit -m "feat: add authoritative PostgreSQL persistence"
```

---

### Task 7: Authorized Resolution and Deterministic Planning Service

**Files:**
- Create: `src/bioharness/application/resolve_task.py`
- Create: `src/bioharness/application/plan_analysis.py`
- Create: `tests/contract/test_planning_service.py`

**Interfaces:**
- Consumes: `ScientificTaskSpec`, `DataProvider`, `PolicyEvaluator`, repositories, identity projections.
- Produces: immutable `ResolvedDataRef`, `ScientificAssessment`, `ResolvedConfiguration`, `ContextSnapshot`, `RunSpec`.

- [ ] **Step 1: Write AUTH-02 and TF-03/PLAN-01 tests**

```python
# tests/contract/test_planning_service.py
def test_resolution_authorizes_before_provider_read(planning_service, spying_provider, policy):
    planning_service.resolve(task_id=TASK_ID, actor="alice")
    assert policy.calls[0].action == "read_resolve"
    assert spying_provider.first_call_index > policy.first_call_index


def test_task_intent_does_not_receive_provider_defaults(sample_task):
    assert "min_seqs" not in sample_task.model_dump()


def test_assessment_fingerprint_binds_task_data_and_contract(planned_run):
    assert len(planned_run.assessment.dependency_fingerprint) == 64
    assert planned_run.assessment.resolved_data_ref_ids == planned_run.run_spec.input_ref_ids
```

- [ ] **Step 2: Implement `ResolutionService`**

Algorithm:

```text
load TaskSpec
-> PolicyEvaluator.evaluate(actor, "read_resolve", task resource, current context)
-> DENY/REQUIRE_APPROVAL: stop before DataProvider.resolve
-> DataProvider.resolve
-> convert provider-neutral resources to ResolvedDataRef records
-> persist PolicyDecision + ResolvedDataRefs
```

No provider defaults are written to TaskSpec.

- [ ] **Step 3: Implement deterministic assessment fingerprint**

The dependency fingerprint is:

```python
sha256_canonical({
    "projection_version": "bioharness.assessment-deps.v1",
    "task_spec": {"id": str(task.id), "revision": task.revision},
    "resolved_data_refs": [str(x.id) for x in sorted(refs, key=lambda r: str(r.id))],
    "scientific_contract": {"id": contract_id, "revision": contract_revision},
    "assumption_constraints": assumption_constraints,
})
```

- [ ] **Step 4: Implement `PlanningService.publish_run_spec`**

Inputs must include explicit configuration defaults and environment contract. The service computes `analysis_hash`, creates ContextSnapshot, computes `run_spec_hash`, persists all immutable records, and refuses publication when assessment status is `UNRESOLVED`, `NOT_IDENTIFIABLE`, or `INCOMPATIBLE`.

- [ ] **Step 5: Run planning contract tests**

Run: `python -m pytest tests/contract/test_planning_service.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/bioharness/application/resolve_task.py src/bioharness/application/plan_analysis.py tests/contract/test_planning_service.py
git commit -m "feat: add authorized deterministic planning flow"
```

---

### Task 8: RunAttempt Allocation and Intent-Before-Side-Effect Transaction

**Files:**
- Modify: `src/bioharness/adapters/postgres/repositories.py`
- Create: `src/bioharness/application/execute_run.py`
- Create: `tests/integration/test_attempt_allocation.py`
- Create: `tests/contract/test_execution_intent.py`

**Interfaces:**
- Consumes: executable RunSpec, current `PolicyEvaluator`, `WorkflowExecutor`.
- Produces: atomic `RunAttempt(SUBMITTING)` + PolicyDecision + ordered RunEvents before executor submission.

- [ ] **Step 1: Write concurrent allocation test**

Use two independent PostgreSQL sessions and a barrier. Both call `create_attempt_intent` for the same RunSpec. Assert returned attempt numbers are `{1, 2}` and there is no duplicate `(run_spec_id, attempt_number)`.

- [ ] **Step 2: Implement attempt allocation under row lock**

`RunRepository.create_attempt_intent(...)` must:

```text
SELECT run_specs ... FOR UPDATE
SELECT COALESCE(MAX(attempt_number), 0) for run_spec_id
next = max + 1
INSERT RunAttempt state=SUBMITTING
INSERT AttemptCreated seq=1
INSERT AuthorizationChecked seq=2
INSERT SubmissionIntentRecorded seq=3
```

The three event inserts and attempt insert occur in one transaction.

- [ ] **Step 3: Write AUTH-01 launch test**

```python
def test_historical_allow_does_not_authorize_new_launch(execution_service, policy):
    policy.set_outcome("launch", "DENY")
    with pytest.raises(LaunchDenied):
        execution_service.start(RUN_SPEC_ID, actor="alice")
    assert execution_service.executor.submit_calls == 0
```

- [ ] **Step 4: Implement `ExecutionService.start` phase A**

The service must perform fresh preflight before opening the short transaction, then persist a new current launch PolicyDecision. A historical decision in ContextSnapshot is never reused as authority.

- [ ] **Step 5: Run allocation/intent tests**

Run:

```bash
python -m pytest tests/integration/test_attempt_allocation.py tests/contract/test_execution_intent.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/bioharness/application/execute_run.py src/bioharness/adapters/postgres/repositories.py tests/integration/test_attempt_allocation.py tests/contract/test_execution_intent.py
git commit -m "feat: persist launch intent before external execution"
```

---

### Task 9: Generic Local-Process Primitive and Safe Launch Binding

**Files:**
- Create: `src/bioharness/adapters/local_process/runner.py`
- Create: `src/bioharness/adapters/local_process/probe.py`
- Modify: `src/bioharness/application/execute_run.py`
- Create: `tests/unit/test_local_process.py`
- Create: `tests/contract/test_unknown_submission.py`

**Interfaces:**
- Consumes: `InvocationSpec` from a WorkflowExecutor and a committed SUBMITTING RunAttempt.
- Produces: `ExecutionBinding`; RUNNING or UNKNOWN transition + durable event.

- [ ] **Step 1: Write local process binding test**

Use `sys.executable -c 'import time; time.sleep(2)'` as the process. Assert `LocalProcessRunner.spawn()` returns PID, hostname, and a Linux `/proc/<pid>/stat` start token when available.

- [ ] **Step 2: Implement `LocalProcessRunner.spawn`**

Use:

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

Never use `shell=True`. Create stdout/stderr parent directories before spawn. Record `socket.gethostname()` and `/proc/<pid>/stat` field 22 as `process_start_token` on Linux.

- [ ] **Step 3: Write the ambiguous bind test**

Inject a runner that raises `BindingUncertain` after the submission intent transaction. Assert the same RunAttempt becomes `UNKNOWN`, `ExecutionOutcomeUnknown` is appended, and `WorkflowExecutor.prepare` is not called a second time automatically.

- [ ] **Step 4: Complete `ExecutionService.start` phase B/C**

On successful bind, atomically update state to RUNNING and append `ExternalProcessBound` + `ExecutionStarted`. On known spawn failure before process creation, mark FAILED. On ambiguous post-spawn/bind failure, mark UNKNOWN. Do not create another RunAttempt automatically.

- [ ] **Step 5: Run process/unknown tests**

Run:

```bash
python -m pytest tests/unit/test_local_process.py tests/contract/test_unknown_submission.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/bioharness/adapters/local_process src/bioharness/application/execute_run.py tests/unit/test_local_process.py tests/contract/test_unknown_submission.py
git commit -m "feat: add crash-aware local process execution"
```

---

### Task 10: Evidence-Based Reconciliation

**Files:**
- Create: `src/bioharness/application/reconcile_run.py`
- Modify: `src/bioharness/adapters/local_process/probe.py`
- Create: `tests/contract/test_reconciliation.py`

**Interfaces:**
- Consumes: RunAttempt binding/history and `WorkflowExecutor.inspect` evidence.
- Produces: safe state transition or `NEEDS_OPERATOR_RECONCILIATION`; never blind resubmission.

- [ ] **Step 1: Write reconciliation matrix tests**

Cover exactly:

```text
active=True, matching process identity     -> RUNNING
terminal_outcome="succeeded", exit=0      -> COLLECTING
terminal_outcome="failed", exit!=0        -> FAILED
active=None, terminal=None                 -> NEEDS_OPERATOR_RECONCILIATION
PID exists but process_start_token differs -> NEEDS_OPERATOR_RECONCILIATION
```

- [ ] **Step 2: Implement `LocalProcessProbe`**

`probe(binding)` checks `/proc/<pid>/stat` when available. PID existence without matching recorded start token returns indeterminate, not active.

- [ ] **Step 3: Implement `ReconciliationService.reconcile`**

It loads the attempt and ordered events, asks the executor for provider evidence, combines provider/process evidence conservatively, and writes a state transition plus `ReconciliationResolved` or `ReconciliationRequired` in one transaction.

- [ ] **Step 4: Explicitly block new launch when unresolved attempt exists**

Modify `ExecutionService.start` so a RunSpec with an existing attempt in `UNKNOWN` or `NEEDS_OPERATOR_RECONCILIATION` is rejected with `PriorAttemptUnresolved` until an operator-supported reconciliation resolves it.

- [ ] **Step 5: Run reconciliation tests**

Run: `python -m pytest tests/contract/test_reconciliation.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/bioharness/application/reconcile_run.py src/bioharness/application/execute_run.py src/bioharness/adapters/local_process/probe.py tests/contract/test_reconciliation.py
git commit -m "feat: add conservative run reconciliation"
```

---

### Task 11: Immutable Artifact Registration and Collection

**Files:**
- Create: `src/bioharness/adapters/filesystem/artifacts.py`
- Create: `src/bioharness/application/collect_artifacts.py`
- Create: `tests/unit/test_artifact_store.py`
- Create: `tests/contract/test_artifact_collection.py`

**Interfaces:**
- Consumes: adapter-declared artifact candidates and completed attempt evidence.
- Produces: immutable Artifact rows with digest/size/path; COLLECTING -> FINISHED only after collection completes.

- [ ] **Step 1: Write digest registration test**

```python
def test_register_artifact_hashes_bytes(tmp_path):
    p = tmp_path / "result.txt"
    p.write_text("abc", encoding="utf-8")
    record = inspect_artifact(p, role="result")
    assert record.content_sha256 == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert record.size_bytes == 3
```

- [ ] **Step 2: Implement streaming SHA-256**

Read files in fixed 1 MiB chunks; do not load large scientific outputs fully into memory.

- [ ] **Step 3: Implement collection service**

`ArtifactCollectionService.collect(attempt_id)` asks `WorkflowExecutor.discover_artifacts`, validates each candidate path is under allowed configured roots, hashes/registers each immutable Artifact, appends `ArtifactDiscovered`/`ArtifactRegistered`, then transitions COLLECTING -> FINISHED.

A missing/changed required artifact causes FAILED collection or a failed later validation according to the adapter-declared requirement; never silently relabel an old artifact.

- [ ] **Step 4: Run artifact tests**

Run:

```bash
python -m pytest tests/unit/test_artifact_store.py tests/contract/test_artifact_collection.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/bioharness/adapters/filesystem src/bioharness/application/collect_artifacts.py tests/unit/test_artifact_store.py tests/contract/test_artifact_collection.py
git commit -m "feat: register immutable artifact evidence"
```

---

### Task 12: Typed Validation Profiles and Historical Evaluations

**Files:**
- Create: `src/bioharness/application/validate_run.py`
- Modify: `src/bioharness/adapters/postgres/repositories.py`
- Create: `tests/contract/test_validation.py`

**Interfaces:**
- Consumes: immutable subjects/evidence and a versioned ValidationProfile.
- Produces: typed ValidationReports and immutable ValidationEvaluation.

- [ ] **Step 1: Write VAL-01/VAL-02/VAL-05 tests**

```python
def test_provider_pass_does_not_open_profile_when_provenance_missing(validation_service):
    provider = validation_service.report(kind="provider_contract", outcome="PASS")
    evaluation = validation_service.evaluate("candidate", "1", report_ids=(provider.id,))
    assert evaluation.outcome == "FAIL"


def test_candidate_profile_never_publishes(validation_service):
    evaluation = validation_service.evaluate_complete_candidate()
    assert evaluation.outcome == "PASS"
    assert validation_service.canonical_mutations == 0
```

- [ ] **Step 2: Implement profile requirements**

For the generic P0 `candidate@1` test profile, require:

```text
provider_contract: PASS or PASS_WITH_LIMITATIONS
artifact_integrity: PASS
provenance_completeness: PASS
```

Store the exact report IDs used. `PASS_WITH_LIMITATIONS` remains distinct in reports even when a profile permits it.

- [ ] **Step 3: Ensure historical profile revisions are immutable**

Creating `candidate@2` must not modify `candidate@1` or prior evaluations. Add an integration assertion against PostgreSQL rows.

- [ ] **Step 4: Run validation tests**

Run: `python -m pytest tests/contract/test_validation.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/bioharness/application/validate_run.py src/bioharness/adapters/postgres/repositories.py tests/contract/test_validation.py
git commit -m "feat: add typed versioned validation gates"
```

---

### Task 13: Evidence-Backed MemoryCandidate Without Authority Escalation

**Files:**
- Create: `src/bioharness/application/memory.py`
- Create: `tests/contract/test_memory.py`

**Interfaces:**
- Consumes: evidence refs from RunSpec/RunAttempt/Artifact/Validation.
- Produces: queryable `MemoryCandidate`; never Policy/Finding/Canonical state.

- [ ] **Step 1: Write PROM-04 retrieval test**

```python
def test_memory_candidate_can_be_recalled_but_not_authorize(memory_service):
    candidate = memory_service.record(
        scope="project:p1",
        kind="execution_lesson",
        statement="Executor revision r1 cannot reconcile after disconnect",
        tags=("executor:r1", "reconciliation"),
        applicability={"executor_revision": "r1"},
        evidence_refs=("run_attempt:ra-1", "validation:val-1"),
    )
    recalled = memory_service.search(scope="project:p1", tags=("executor:r1",))
    assert candidate.id in {x.id for x in recalled}
    assert memory_service.policy_decision_count() == 0
```

- [ ] **Step 2: Implement deterministic P0 retrieval**

Search by scope, exact tags, provider/workflow revision keys, and case-insensitive text containment. No vector store and no graph database.

- [ ] **Step 3: Enforce evidence requirement**

Reject creation of a MemoryCandidate with an empty `evidence_refs` tuple in P0.

- [ ] **Step 4: Run memory tests**

Run: `python -m pytest tests/contract/test_memory.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/bioharness/application/memory.py tests/contract/test_memory.py
git commit -m "feat: add evidence-backed memory candidates"
```

---

### Task 14: Headless CLI Over Application Services

**Files:**
- Create: `src/bioharness/cli/__init__.py`
- Create: `src/bioharness/cli/main.py`
- Create: `tests/contract/test_cli.py`

**Interfaces:**
- Consumes: application services only.
- Produces: stable CLI commands and machine-readable IDs/statuses; no direct provider subprocess calls.

- [ ] **Step 1: Write CLI help/architecture test**

Use Typer `CliRunner`. Assert commands exist: `task create`, `task show`, `plan`, `run start`, `run show`, `run reconcile`, `artifact list`, `validate`, `memory list`.

- [ ] **Step 2: Implement command groups**

Each command constructs application services from settings/UoW/registered adapters and prints JSON to stdout for stable IDs/status. Human-friendly formatting can be added later; the P0 source of truth is machine-readable output.

- [ ] **Step 3: Add a static architecture guard**

`tests/contract/test_core_dependency_boundary.py` scans Python files under `src/bioharness` and fails if imports/text include `examples.reference_integrations`, `genome_web`, `deepseek_harness`, or `earendil_works.pi` as executable dependencies. Documentation strings describing boundaries may be exempted only by keeping them outside executable source.

- [ ] **Step 4: Run CLI and boundary tests**

Run:

```bash
python -m pytest tests/contract/test_cli.py tests/contract/test_core_dependency_boundary.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

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
- Consumes: all Core services.
- Produces: one complete fake-provider vertical slice proving Core works with no Genome-web dependency.

- [ ] **Step 1: Implement a deterministic fake external provider process**

`tests/fixtures/fake_science_provider.py` accepts `--input`, `--outdir`, and `--mode success|fail`. In success mode it writes `result.txt`, `provider_evidence.json`, then exits 0. In fail mode it writes stderr and exits 9. It contains no Genome-web/TF logic.

- [ ] **Step 2: Write the full vertical-slice test**

The test performs:

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
-> local fake provider process
-> Artifact registration
-> provider_contract + artifact_integrity + provenance_completeness reports
-> candidate@1 ValidationEvaluation PASS
-> MemoryCandidate record/retrieval
```

Assertions include:

```text
no provider defaults in TaskSpec
one RunSpec
one RunAttempt
ordered RunEvents
artifact digest matches bytes
validation PASS does not create canonical state
memory recall creates no PolicyDecision
```

- [ ] **Step 3: Add unknown-outcome vertical test**

Inject `BindingUncertain` after submission intent. Assert RunAttempt UNKNOWN, no second process launch, and a subsequent `run start` is blocked until reconciliation.

- [ ] **Step 4: Run the complete Core suite in CI**

Run:

```bash
alembic upgrade head
python -m pytest tests/unit tests/contract tests/integration -q
```

Expected: PASS, without the Genome-web repository, Nextflow, MAFFT, IQ-TREE, Pi, or DeepSeek Harness installed.

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/fake_science_provider.py tests/integration/test_p0_vertical_slice.py .github/workflows/ci.yml
git commit -m "test: prove provider-agnostic P0 vertical slice"
```

---

## Plan Completion Gate

Before declaring this plan implemented:

1. Fresh CI on the implementation head must pass `tests/unit`, `tests/contract`, and `tests/integration` against PostgreSQL 16.
2. The Core dependency-boundary test must prove Genome-web reference code is not imported by `src/bioharness`.
3. The fake-provider vertical slice must prove submission intent, unknown handling, typed validation, and non-authoritative memory semantics.
4. Do not mark the Genome-web TF acceptance scenarios PASS from this plan; they remain `NOT_RUN` until the separate reference-integration plan is executed in the isolated server environment.
5. Do not claim production readiness, publication support, remote schedulers, durable cancellation, or exactly-once guarantees.

## Follow-On Plan Boundary

After Core passes this plan, execute `docs/superpowers/plans/2026-09-18-genome-web-tf-reference-integration.md`. That plan may depend on BioHarness public ports and the external Genome-web repository, but BioHarness Core must never depend on it.
