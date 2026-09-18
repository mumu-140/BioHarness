from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field

from bioharness.domain.base import FrozenRecord
from bioharness.ports.workflow_executor import ExecutionBinding


class RunAttemptState(StrEnum):
    SUBMITTING = "SUBMITTING"
    RUNNING = "RUNNING"
    COLLECTING = "COLLECTING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    NEEDS_OPERATOR_RECONCILIATION = "NEEDS_OPERATOR_RECONCILIATION"


_ALLOWED_TRANSITIONS: dict[RunAttemptState, frozenset[RunAttemptState]] = {
    RunAttemptState.SUBMITTING: frozenset({RunAttemptState.RUNNING, RunAttemptState.FAILED, RunAttemptState.UNKNOWN}),
    RunAttemptState.RUNNING: frozenset({RunAttemptState.COLLECTING, RunAttemptState.FAILED, RunAttemptState.UNKNOWN}),
    RunAttemptState.COLLECTING: frozenset({RunAttemptState.FINISHED, RunAttemptState.FAILED, RunAttemptState.UNKNOWN}),
    RunAttemptState.UNKNOWN: frozenset({
        RunAttemptState.RUNNING,
        RunAttemptState.COLLECTING,
        RunAttemptState.FINISHED,
        RunAttemptState.FAILED,
        RunAttemptState.NEEDS_OPERATOR_RECONCILIATION,
    }),
    RunAttemptState.NEEDS_OPERATOR_RECONCILIATION: frozenset({
        RunAttemptState.RUNNING,
        RunAttemptState.COLLECTING,
        RunAttemptState.FINISHED,
        RunAttemptState.FAILED,
    }),
    RunAttemptState.FINISHED: frozenset(),
    RunAttemptState.FAILED: frozenset(),
}


def allowed_transition(current: RunAttemptState, target: RunAttemptState) -> bool:
    return target in _ALLOWED_TRANSITIONS[current]


class RunEventType(StrEnum):
    ATTEMPT_CREATED = "AttemptCreated"
    AUTHORIZATION_CHECKED = "AuthorizationChecked"
    SUBMISSION_INTENT_RECORDED = "SubmissionIntentRecorded"
    EXTERNAL_PROCESS_BOUND = "ExternalProcessBound"
    EXECUTION_STARTED = "ExecutionStarted"
    EXECUTION_EXITED = "ExecutionExited"
    EXECUTION_OUTCOME_UNKNOWN = "ExecutionOutcomeUnknown"
    ARTIFACT_DISCOVERED = "ArtifactDiscovered"
    ARTIFACT_REGISTERED = "ArtifactRegistered"
    VALIDATION_REPORTED = "ValidationReported"
    RECONCILIATION_REQUIRED = "ReconciliationRequired"
    RECONCILIATION_RESOLVED = "ReconciliationResolved"


class ResolvedConfiguration(FrozenRecord):
    id: UUID
    task_spec_id: UUID
    assessment_id: UUID
    provider_workflow_identity: dict[str, Any]
    result_affecting_parameters: dict[str, Any]
    environment_contract: dict[str, Any]
    reproducibility_contract: dict[str, Any]
    validation_profile_id: str
    validation_profile_revision: str
    assumption_constraints: dict[str, Any] = Field(default_factory=dict)
    planned_resource_controls: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ContextSnapshot(FrozenRecord):
    id: UUID
    policy_decision_ids: tuple[UUID, ...] = ()
    memory_refs: tuple[str, ...] = ()
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class RunSpec(FrozenRecord):
    id: UUID
    task_spec_id: UUID
    assessment_id: UUID
    configuration_id: UUID
    context_snapshot_id: UUID
    resolved_data_ref_ids: tuple[UUID, ...]
    analysis_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    run_spec_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_profile_id: str
    validation_profile_revision: str
    expected_outputs: tuple[str, ...] = ()
    executable: bool = True
    created_at: datetime


class RunAttempt(FrozenRecord):
    id: UUID
    run_spec_id: UUID
    attempt_number: int = Field(ge=1)
    executor_namespace: str
    capability_snapshot: dict[str, Any]
    submission_key: str
    provider_attempt_name: str
    submission_fingerprint: str | None = None
    binding: ExecutionBinding | None = None
    observed_runtime_environment: dict[str, Any] = Field(default_factory=dict)
    observed_resource_allocation: dict[str, Any] = Field(default_factory=dict)
    state: RunAttemptState
    submitted_at: datetime
    last_reconciled_at: datetime | None = None


class RunEvent(FrozenRecord):
    id: UUID
    run_attempt_id: UUID
    sequence_no: int = Field(ge=1)
    event_type: RunEventType
    payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime
