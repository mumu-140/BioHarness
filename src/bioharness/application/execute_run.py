from collections.abc import Callable
from datetime import datetime, timezone
from uuid import UUID

from bioharness.domain.policy import PolicyOutcome
from bioharness.domain.run import RunAttemptState, RunEventType

from .materialize_execution import materialize_execution


class LaunchDenied(RuntimeError):
    pass


class RunSpecNotFound(LookupError):
    pass


class PreflightFailed(RuntimeError):
    pass


class PriorAttemptUnresolved(RuntimeError):
    pass


class ExecutionService:
    def __init__(
        self,
        *,
        policy,
        executor,
        process_runner,
        uow_factory,
        preflight: Callable[[object], dict],
        clock: Callable[[], datetime] | None = None,
        executor_namespace: str = "local",
    ):
        self.policy = policy
        self.executor = executor
        self.process_runner = process_runner
        self.uow_factory = uow_factory
        self.preflight = preflight
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.executor_namespace = executor_namespace

    def start(self, run_spec_id: UUID, actor: str):
        with self.uow_factory() as uow:
            run_spec = uow.planning.get_run_spec(run_spec_id)
        if run_spec is None:
            raise RunSpecNotFound(str(run_spec_id))
        if not run_spec.executable:
            raise PreflightFailed("RunSpec is not executable")

        with self.uow_factory() as uow:
            prior_attempts = uow.runs.list_attempts(run_spec_id)
        if any(
            attempt.state in {
                RunAttemptState.UNKNOWN,
                RunAttemptState.NEEDS_OPERATOR_RECONCILIATION,
            }
            for attempt in prior_attempts
        ):
            raise PriorAttemptUnresolved(str(run_spec_id))

        preflight_evidence = self.preflight(run_spec)
        decision = self.policy.evaluate(actor, "launch", f"runspec:{run_spec_id}", {"run_spec_hash": run_spec.run_spec_hash})
        if decision.outcome in {PolicyOutcome.DENY, PolicyOutcome.REQUIRE_APPROVAL}:
            with self.uow_factory() as uow:
                uow.planning.add_policy_decision(decision)
                uow.commit()
            raise LaunchDenied(f"launch not authorized: {decision.outcome.value}")

        capabilities = self.executor.capabilities().model_dump(mode="json")
        with self.uow_factory() as uow:
            attempt = uow.runs.allocate_attempt_intent(
                run_spec_id=run_spec.id,
                decision=decision,
                capability_snapshot=capabilities,
                executor_namespace=self.executor_namespace,
                preflight_evidence=preflight_evidence,
                now=self.clock(),
            )
            uow.commit()

        try:
            execution = materialize_execution(
                uow_factory=self.uow_factory,
                run_spec=run_spec,
                attempt=attempt,
            )
            invocation = self.executor.prepare(execution)
        except Exception as exc:
            with self.uow_factory() as uow:
                failed = uow.runs.transition(
                    attempt.id,
                    RunAttemptState.FAILED,
                    RunEventType.EXECUTION_EXITED,
                    {"phase": "prepare", "error": type(exc).__name__, "message": str(exc)},
                    self.clock(),
                )
                uow.commit()
            return failed

        try:
            binding = self.process_runner.spawn(invocation)
        except OSError as exc:
            with self.uow_factory() as uow:
                failed = uow.runs.transition(
                    attempt.id,
                    RunAttemptState.FAILED,
                    RunEventType.EXECUTION_EXITED,
                    {
                        "phase": "spawn",
                        "process_started": False,
                        "error": type(exc).__name__,
                        "message": str(exc),
                    },
                    self.clock(),
                )
                uow.commit()
            return failed
        except Exception as exc:
            with self.uow_factory() as uow:
                unknown = uow.runs.transition(
                    attempt.id,
                    RunAttemptState.UNKNOWN,
                    RunEventType.EXECUTION_OUTCOME_UNKNOWN,
                    {"phase": "spawn", "error": type(exc).__name__, "message": str(exc)},
                    self.clock(),
                )
                uow.commit()
            return unknown

        try:
            with self.uow_factory() as uow:
                running = uow.runs.bind_execution(attempt.id, binding, self.clock())
                uow.commit()
        except Exception as exc:
            with self.uow_factory() as uow:
                unknown = uow.runs.transition(
                    attempt.id,
                    RunAttemptState.UNKNOWN,
                    RunEventType.EXECUTION_OUTCOME_UNKNOWN,
                    {
                        "phase": "bind",
                        "binding": binding.model_dump(mode="json"),
                        "error": type(exc).__name__,
                        "message": str(exc),
                    },
                    self.clock(),
                )
                uow.commit()
            return unknown
        return running
