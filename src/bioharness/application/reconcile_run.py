from collections.abc import Callable
from datetime import datetime, timezone
from uuid import UUID

from bioharness.domain.run import RunAttemptState, RunEventType
from bioharness.ports.workflow_executor import ExecutionEvidence


class AttemptNotFound(LookupError):
    pass


class ReconciliationService:
    def __init__(self, *, executor, process_probe, uow_factory, clock: Callable[[], datetime] | None = None):
        self.executor = executor
        self.process_probe = process_probe
        self.uow_factory = uow_factory
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def reconcile(self, attempt_id: UUID, actor: str):
        with self.uow_factory() as uow:
            attempt = uow.runs.get_attempt(attempt_id)
        if attempt is None:
            raise AttemptNotFound(str(attempt_id))

        binding = attempt.binding
        probe_value = self.process_probe.probe(binding) if binding is not None else None
        if binding is not None:
            evidence = self.executor.inspect(binding, attempt.model_dump(mode="json"))
        else:
            evidence = ExecutionEvidence(active=None, terminal_outcome=None, exit_code=None)

        if evidence.terminal_outcome == "succeeded" and evidence.exit_code == 0:
            target = RunAttemptState.COLLECTING
        elif evidence.terminal_outcome == "failed" or (evidence.exit_code is not None and evidence.exit_code != 0):
            target = RunAttemptState.FAILED
        elif probe_value is True and evidence.active is not False:
            target = RunAttemptState.RUNNING
        else:
            target = RunAttemptState.NEEDS_OPERATOR_RECONCILIATION

        event_type = (
            RunEventType.RECONCILIATION_REQUIRED
            if target is RunAttemptState.NEEDS_OPERATOR_RECONCILIATION
            else RunEventType.RECONCILIATION_RESOLVED
        )
        payload = {
            "actor": actor,
            "process_probe": probe_value,
            "executor_evidence": evidence.model_dump(mode="json"),
        }
        with self.uow_factory() as uow:
            updated = uow.runs.transition(attempt.id, target, event_type, payload, self.clock())
            uow.commit()
        return updated
