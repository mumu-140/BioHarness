from pathlib import Path
from typing import Any, Protocol
from uuid import UUID

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


class ExecutionDescriptor(FrozenRecord):
    run_spec_id: UUID
    run_spec_hash: str
    analysis_hash: str
    attempt_id: UUID
    attempt_number: int
    submission_key: str
    provider_attempt_name: str
    workflow_identity: dict[str, Any]
    resolved_inputs: tuple[dict[str, Any], ...]
    result_affecting_parameters: dict[str, Any]
    environment_contract: dict[str, Any]
    reproducibility_contract: dict[str, Any]
    planned_resource_controls: dict[str, Any]
    expected_outputs: tuple[str, ...]
    validation_profile_id: str
    validation_profile_revision: str


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

    def prepare(self, execution: ExecutionDescriptor) -> InvocationSpec: ...

    def inspect(
        self, binding: ExecutionBinding | None, attempt_payload: dict[str, Any]
    ) -> ExecutionEvidence: ...

    def discover_artifacts(
        self, attempt_payload: dict[str, Any]
    ) -> tuple[dict[str, Any], ...]: ...


class ProcessRunner(Protocol):
    def spawn(self, invocation: InvocationSpec) -> ExecutionBinding: ...
