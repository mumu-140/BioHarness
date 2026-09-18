from collections.abc import Callable
from datetime import datetime, timezone
from uuid import UUID

from bioharness.domain.policy import PolicyOutcome


class LaunchDenied(RuntimeError):
    pass


class RunSpecNotFound(LookupError):
    pass


class PreflightFailed(RuntimeError):
    pass


class ExecutionService:
    def __init__(
        self,
        *,
        policy,
        executor,
        process_runner,
        uow_factory,
        preflight: Callable[[object], None] | None = None,
        clock: Callable[[], datetime] | None = None,
        executor_namespace: str = "local",
    ):
        self.policy = policy
        self.executor = executor
        self.process_runner = process_runner
        self.uow_factory = uow_factory
        self.preflight = preflight or (lambda run_spec: None)
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.executor_namespace = executor_namespace

    def start(self, run_spec_id: UUID, actor: str):
        with self.uow_factory() as uow:
            run_spec = uow.planning.get_run_spec(run_spec_id)
        if run_spec is None:
            raise RunSpecNotFound(str(run_spec_id))
        if not run_spec.executable:
            raise PreflightFailed("RunSpec is not executable")

        self.preflight(run_spec)
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
                now=self.clock(),
            )
            uow.commit()
        return attempt
