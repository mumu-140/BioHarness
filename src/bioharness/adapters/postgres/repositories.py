from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from bioharness.domain.artifact import Artifact
from bioharness.domain.assessment import ScientificAssessment
from bioharness.domain.data import ResolvedDataRef
from bioharness.domain.memory import MemoryCandidate
from bioharness.domain.policy import PolicyDecision
from bioharness.domain.run import (
    ContextSnapshot,
    ResolvedConfiguration,
    RunAttempt,
    RunAttemptState,
    RunEvent,
    RunEventType,
    RunSpec,
    allowed_transition,
)
from bioharness.domain.task import ScientificTaskSpec
from bioharness.domain.validation import ValidationEvaluation, ValidationProfile, ValidationReport

from .models import (
    ArtifactRow,
    ContextSnapshotRow,
    MemoryCandidateRow,
    PolicyDecisionRow,
    ResolvedConfigurationRow,
    ResolvedDataRefRow,
    RunAttemptRow,
    RunEventRow,
    RunSpecRow,
    ScientificAssessmentRow,
    ScientificTaskSpecRow,
    ValidationEvaluationRow,
    ValidationProfileRow,
    ValidationReportRow,
)


def _payload(record) -> dict:
    return record.model_dump(mode="json")


class PlanningRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_task(self, value: ScientificTaskSpec) -> None:
        self.session.add(ScientificTaskSpecRow(id=value.id, revision=value.revision, payload=_payload(value), created_at=value.created_at))

    def get_task(self, value_id: UUID) -> ScientificTaskSpec | None:
        row = self.session.get(ScientificTaskSpecRow, value_id)
        return ScientificTaskSpec.model_validate(row.payload) if row else None

    def add_policy_decision(self, value: PolicyDecision) -> None:
        self.session.add(PolicyDecisionRow(id=value.id, action=value.action, outcome=value.outcome.value, payload=_payload(value), decided_at=value.decided_at))

    def add_data_ref(self, value: ResolvedDataRef) -> None:
        self.session.add(ResolvedDataRefRow(id=value.id, provider=value.provider, provider_revision=value.provider_revision, logical_uri=value.logical_uri, payload=_payload(value), resolved_at=value.resolved_at))

    def get_data_ref(self, value_id: UUID) -> ResolvedDataRef | None:
        row = self.session.get(ResolvedDataRefRow, value_id)
        return ResolvedDataRef.model_validate(row.payload) if row else None

    def add_assessment(self, value: ScientificAssessment) -> None:
        self.session.add(ScientificAssessmentRow(id=value.id, task_spec_id=value.task_spec_id, status=value.status.value, dependency_fingerprint=value.dependency_fingerprint, payload=_payload(value), assessed_at=value.assessed_at))

    def get_assessment(self, value_id: UUID) -> ScientificAssessment | None:
        row = self.session.get(ScientificAssessmentRow, value_id)
        return ScientificAssessment.model_validate(row.payload) if row else None

    def add_configuration(self, value: ResolvedConfiguration) -> None:
        self.session.add(ResolvedConfigurationRow(id=value.id, task_spec_id=value.task_spec_id, assessment_id=value.assessment_id, payload=_payload(value), created_at=value.created_at))

    def get_configuration(self, value_id: UUID) -> ResolvedConfiguration | None:
        row = self.session.get(ResolvedConfigurationRow, value_id)
        return ResolvedConfiguration.model_validate(row.payload) if row else None

    def add_context(self, value: ContextSnapshot) -> None:
        self.session.add(ContextSnapshotRow(id=value.id, payload=_payload(value), created_at=value.created_at))

    def get_context(self, value_id: UUID) -> ContextSnapshot | None:
        row = self.session.get(ContextSnapshotRow, value_id)
        return ContextSnapshot.model_validate(row.payload) if row else None

    def add_run_spec(self, value: RunSpec) -> None:
        self.session.add(RunSpecRow(id=value.id, task_spec_id=value.task_spec_id, analysis_hash=value.analysis_hash, run_spec_hash=value.run_spec_hash, executable=value.executable, payload=_payload(value), created_at=value.created_at))

    def get_run_spec(self, value_id: UUID, *, for_update: bool = False) -> RunSpec | None:
        stmt = select(RunSpecRow).where(RunSpecRow.id == value_id)
        if for_update:
            stmt = stmt.with_for_update()
        row = self.session.execute(stmt).scalar_one_or_none()
        return RunSpec.model_validate(row.payload) if row else None


class RunRepository:
    def __init__(self, session: Session):
        self.session = session

    def allocate_attempt_intent(self, *, run_spec_id: UUID, decision: PolicyDecision, capability_snapshot: dict, executor_namespace: str, now: datetime) -> RunAttempt:
        spec_row = self.session.execute(
            select(RunSpecRow).where(RunSpecRow.id == run_spec_id).with_for_update()
        ).scalar_one()
        if not spec_row.executable:
            raise ValueError("RunSpec is not executable")
        max_number = self.session.execute(
            select(func.max(RunAttemptRow.attempt_number)).where(RunAttemptRow.run_spec_id == run_spec_id)
        ).scalar_one()
        attempt_number = (max_number or 0) + 1
        attempt = RunAttempt(
            id=uuid4(),
            run_spec_id=run_spec_id,
            attempt_number=attempt_number,
            executor_namespace=executor_namespace,
            capability_snapshot=capability_snapshot,
            submission_key=str(uuid4()),
            provider_attempt_name=f"bh-{str(run_spec_id)[:8]}-{attempt_number}",
            state=RunAttemptState.SUBMITTING,
            submitted_at=now,
        )
        self.session.add(PolicyDecisionRow(
            id=decision.id, action=decision.action, outcome=decision.outcome.value,
            payload=_payload(decision), decided_at=decision.decided_at,
        ))
        self.add_attempt(attempt)
        for seq, event_type, payload in (
            (1, RunEventType.ATTEMPT_CREATED, {"run_spec_id": str(run_spec_id)}),
            (2, RunEventType.AUTHORIZATION_CHECKED, {"policy_decision_id": str(decision.id)}),
            (3, RunEventType.SUBMISSION_INTENT_RECORDED, {"submission_key": attempt.submission_key}),
        ):
            self.add_event(RunEvent(
                id=uuid4(), run_attempt_id=attempt.id, sequence_no=seq,
                event_type=event_type, payload=payload, occurred_at=now,
            ))
        return attempt

    def add_attempt(self, value: RunAttempt) -> None:
        self.session.add(RunAttemptRow(
            id=value.id,
            run_spec_id=value.run_spec_id,
            attempt_number=value.attempt_number,
            executor_namespace=value.executor_namespace,
            submission_key=value.submission_key,
            provider_attempt_name=value.provider_attempt_name,
            state=value.state.value,
            payload=_payload(value),
            submitted_at=value.submitted_at,
            last_reconciled_at=value.last_reconciled_at,
        ))

    def get_attempt(self, value_id: UUID, *, for_update: bool = False) -> RunAttempt | None:
        stmt = select(RunAttemptRow).where(RunAttemptRow.id == value_id)
        if for_update:
            stmt = stmt.with_for_update()
        row = self.session.execute(stmt).scalar_one_or_none()
        return RunAttempt.model_validate(row.payload) if row else None

    def list_attempts(self, run_spec_id: UUID) -> tuple[RunAttempt, ...]:
        rows = self.session.execute(select(RunAttemptRow).where(RunAttemptRow.run_spec_id == run_spec_id).order_by(RunAttemptRow.attempt_number)).scalars().all()
        return tuple(RunAttempt.model_validate(row.payload) for row in rows)

    def add_event(self, value: RunEvent) -> None:
        self.session.add(RunEventRow(id=value.id, run_attempt_id=value.run_attempt_id, sequence_no=value.sequence_no, event_type=value.event_type.value, payload=_payload(value), occurred_at=value.occurred_at))

    def list_events(self, attempt_id: UUID) -> tuple[RunEvent, ...]:
        rows = self.session.execute(select(RunEventRow).where(RunEventRow.run_attempt_id == attempt_id).order_by(RunEventRow.sequence_no)).scalars().all()
        return tuple(RunEvent.model_validate(row.payload) for row in rows)

    def transition(self, attempt_id: UUID, target: RunAttemptState, event_type: RunEventType, payload: dict, occurred_at: datetime) -> RunAttempt:
        row = self.session.execute(select(RunAttemptRow).where(RunAttemptRow.id == attempt_id).with_for_update()).scalar_one()
        current = RunAttempt.model_validate(row.payload)
        if not allowed_transition(current.state, target):
            raise ValueError(f"illegal RunAttempt transition {current.state} -> {target}")
        reconciled_at = occurred_at if event_type in {RunEventType.RECONCILIATION_REQUIRED, RunEventType.RECONCILIATION_RESOLVED} else current.last_reconciled_at
        updated = current.model_copy(update={"state": target, "last_reconciled_at": reconciled_at})
        row.state = target.value
        row.last_reconciled_at = updated.last_reconciled_at
        row.payload = _payload(updated)
        seq = self.session.execute(select(RunEventRow.sequence_no).where(RunEventRow.run_attempt_id == attempt_id).order_by(RunEventRow.sequence_no.desc()).limit(1)).scalar_one_or_none()
        self.add_event(RunEvent(id=uuid4(), run_attempt_id=attempt_id, sequence_no=(seq or 0) + 1, event_type=event_type, payload=payload, occurred_at=occurred_at))
        return updated


class ArtifactRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, value: Artifact) -> None:
        self.session.add(ArtifactRow(id=value.id, run_spec_id=value.run_spec_id, run_attempt_id=value.run_attempt_id, role=value.role, content_sha256=value.content_sha256, size_bytes=value.size_bytes, uri=value.uri, payload=_payload(value), registered_at=value.registered_at))

    def list_for_attempt(self, attempt_id: UUID) -> tuple[Artifact, ...]:
        rows = self.session.execute(select(ArtifactRow).where(ArtifactRow.run_attempt_id == attempt_id)).scalars().all()
        return tuple(Artifact.model_validate(r.payload) for r in rows)


class ValidationRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_profile(self, value: ValidationProfile) -> None:
        self.session.add(ValidationProfileRow(profile_id=value.profile_id, revision=value.revision, payload=_payload(value)))

    def get_profile(self, profile_id: str, revision: str) -> ValidationProfile | None:
        row = self.session.execute(select(ValidationProfileRow).where(ValidationProfileRow.profile_id == profile_id, ValidationProfileRow.revision == revision)).scalar_one_or_none()
        return ValidationProfile.model_validate(row.payload) if row else None

    def add_report(self, value: ValidationReport) -> None:
        self.session.add(ValidationReportRow(id=value.id, kind=value.kind, subject_type=value.subject_type, subject_id=value.subject_id, outcome=value.outcome.value, payload=_payload(value), created_at=value.created_at))

    def get_report(self, value_id: UUID) -> ValidationReport | None:
        row = self.session.get(ValidationReportRow, value_id)
        return ValidationReport.model_validate(row.payload) if row else None

    def add_evaluation(self, value: ValidationEvaluation) -> None:
        self.session.add(ValidationEvaluationRow(id=value.id, profile_id=value.profile_id, profile_revision=value.profile_revision, outcome=value.outcome.value, payload=_payload(value), evaluated_at=value.evaluated_at))


class MemoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, value: MemoryCandidate) -> None:
        self.session.add(MemoryCandidateRow(id=value.id, scope=value.scope, kind=value.kind, statement=value.statement, payload=_payload(value), created_at=value.created_at))

    def list_scope(self, scope: str) -> tuple[MemoryCandidate, ...]:
        rows = self.session.execute(select(MemoryCandidateRow).where(MemoryCandidateRow.scope == scope).order_by(MemoryCandidateRow.created_at)).scalars().all()
        return tuple(MemoryCandidate.model_validate(r.payload) for r in rows)
