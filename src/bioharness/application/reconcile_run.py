from collections.abc import Callable
from datetime import datetime, timezone
from uuid import UUID

from bioharness.domain.run import (
    RunAttemptState,
    RunEventType,
    allowed_transition,
)


class AttemptNotFound(LookupError):
    pass


class ReconciliationService:
    def __init__(
        self,
        *,
        executor,
        process_probe,
        uow_factory,
        clock: Callable[[], datetime] | None = None,
    ):
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
        evidence = self.executor.inspect(
            binding,
            attempt.model_dump(mode="json"),
        )

        if evidence.terminal_outcome == "succeeded" and evidence.exit_code == 0:
            target = RunAttemptState.COLLECTING
        elif evidence.terminal_outcome == "failed" or (
            evidence.exit_code is not None and evidence.exit_code != 0
        ):
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
        now = self.clock()

        with self.uow_factory() as uow:
            current = uow.runs.get_attempt(attempt.id)
            if current is None:
                raise AttemptNotFound(str(attempt.id))

            if current.state is target:
                return current

            if allowed_transition(current.state, target):
                updated = uow.runs.transition(
                    current.id,
                    target,
                    event_type,
                    payload,
                    now,
                )
            elif (
                allowed_transition(current.state, RunAttemptState.UNKNOWN)
                and allowed_transition(RunAttemptState.UNKNOWN, target)
            ):
                unknown = uow.runs.transition(
                    current.id,
                    RunAttemptState.UNKNOWN,
                    RunEventType.EXECUTION_OUTCOME_UNKNOWN,
                    payload,
                    now,
                )
                updated = uow.runs.transition(
                    unknown.id,
                    target,
                    event_type,
                    payload,
                    now,
                )
            else:
                raise ValueError(
                    f"cannot reconcile RunAttempt {current.state} -> {target}"
                )
            uow.commit()
        return updated
