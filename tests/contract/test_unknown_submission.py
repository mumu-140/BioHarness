from datetime import datetime, timezone
from uuid import uuid4

from bioharness.application.execute_run import ExecutionService
from bioharness.domain.run import (
    ResolvedConfiguration,
    RunAttempt,
    RunAttemptState,
    RunEventType,
)
from tests.fakes.factories import make_data_ref, make_run_spec
from tests.fakes.providers import (
    FakePolicyEvaluator,
    FakeProcessRunner,
    FakeWorkflowExecutor,
)

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


class Planning:
    def __init__(self, spec):
        self.spec = spec
        self.decisions = []
        self.ref = make_data_ref()
        self.configuration = ResolvedConfiguration(
            id=spec.configuration_id,
            task_spec_id=spec.task_spec_id,
            assessment_id=spec.assessment_id,
            provider_workflow_identity={"provider": "fake", "revision": "r1"},
            result_affecting_parameters={},
            environment_contract={},
            reproducibility_contract={"class": "DETERMINISTIC"},
            validation_profile_id=spec.validation_profile_id,
            validation_profile_revision=spec.validation_profile_revision,
            created_at=NOW,
        )

    def get_run_spec(self, value_id, **kwargs):
        return self.spec

    def get_configuration(self, value_id):
        return self.configuration if value_id == self.configuration.id else None

    def get_data_ref(self, value_id):
        return self.ref if value_id == self.ref.id else None

    def add_policy_decision(self, value):
        self.decisions.append(value)


class Runs:
    def __init__(self, spec):
        self.spec = spec
        self.attempt = None
        self.events = []

    def list_attempts(self, run_spec_id):
        return () if self.attempt is None else (self.attempt,)

    def allocate_attempt_intent(self, **kwargs):
        self.attempt = RunAttempt(
            id=uuid4(),
            run_spec_id=self.spec.id,
            attempt_number=1,
            executor_namespace="local",
            capability_snapshot=kwargs["capability_snapshot"],
            submission_key="s1",
            provider_attempt_name="p1",
            state=RunAttemptState.SUBMITTING,
            submitted_at=NOW,
        )
        return self.attempt

    def transition(self, attempt_id, target, event_type, payload, occurred_at):
        self.attempt = self.attempt.model_copy(update={"state": target})
        self.events.append(event_type)
        return self.attempt

    def bind_execution(self, attempt_id, binding, occurred_at):
        self.attempt = self.attempt.model_copy(
            update={"binding": binding, "state": RunAttemptState.RUNNING}
        )
        return self.attempt


class Uow:
    def __init__(self, planning, runs):
        self.planning = planning
        self.runs = runs

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def commit(self):
        pass

    def rollback(self):
        pass


def test_ambiguous_spawn_leaves_single_unknown_attempt():
    spec = make_run_spec()
    planning = Planning(spec)
    runs = Runs(spec)
    executor = FakeWorkflowExecutor()
    runner = FakeProcessRunner(raise_after_possible_spawn=True)
    service = ExecutionService(
        policy=FakePolicyEvaluator(),
        executor=executor,
        process_runner=runner,
        uow_factory=lambda: Uow(planning, runs),
        preflight=lambda _: {"checked": True},
        clock=lambda: NOW,
    )
    attempt = service.start(spec.id, actor="alice")
    assert attempt.state is RunAttemptState.UNKNOWN
    assert runner.spawn_calls == 1
    assert executor.prepare_calls == 1
    assert runs.events == [RunEventType.EXECUTION_OUTCOME_UNKNOWN]


class KnownNoSpawnFailureRunner:
    def __init__(self):
        self.spawn_calls = 0

    def spawn(self, invocation):
        self.spawn_calls += 1
        raise FileNotFoundError("executable not found")


def test_known_no_spawn_failure_is_failed_not_unknown():
    spec = make_run_spec()
    planning = Planning(spec)
    runs = Runs(spec)
    runner = KnownNoSpawnFailureRunner()
    service = ExecutionService(
        policy=FakePolicyEvaluator(),
        executor=FakeWorkflowExecutor(),
        process_runner=runner,
        uow_factory=lambda: Uow(planning, runs),
        preflight=lambda _: {"checked": True},
        clock=lambda: NOW,
    )
    attempt = service.start(spec.id, actor="alice")
    assert attempt.state is RunAttemptState.FAILED
    assert runner.spawn_calls == 1
    assert runs.events == [RunEventType.EXECUTION_EXITED]


class BindPersistenceFailureRuns(Runs):
    def bind_execution(self, attempt_id, binding, occurred_at):
        raise RuntimeError("binding persistence failed")


def test_bind_persistence_failure_after_spawn_is_unknown():
    spec = make_run_spec()
    planning = Planning(spec)
    runs = BindPersistenceFailureRuns(spec)
    runner = FakeProcessRunner()
    service = ExecutionService(
        policy=FakePolicyEvaluator(),
        executor=FakeWorkflowExecutor(),
        process_runner=runner,
        uow_factory=lambda: Uow(planning, runs),
        preflight=lambda _: {"checked": True},
        clock=lambda: NOW,
    )
    attempt = service.start(spec.id, actor="alice")
    assert attempt.state is RunAttemptState.UNKNOWN
    assert runner.spawn_calls == 1
    assert runs.events == [RunEventType.EXECUTION_OUTCOME_UNKNOWN]
