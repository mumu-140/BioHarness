from datetime import datetime, timezone

import pytest

from bioharness.application.execute_run import ExecutionService, LaunchDenied
from tests.fakes.factories import make_run_spec
from tests.fakes.providers import FakePolicyEvaluator, FakeProcessRunner, FakeWorkflowExecutor

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


class PlanningSpy:
    def __init__(self, spec): self.spec = spec; self.decisions = []
    def get_run_spec(self, value_id, **kwargs): return self.spec if value_id == self.spec.id else None
    def add_policy_decision(self, value): self.decisions.append(value)


class RunsSpy:
    def __init__(self): self.allocations = []
    def list_attempts(self, run_spec_id): return ()
    def allocate_attempt_intent(self, **kwargs): self.allocations.append(kwargs); raise AssertionError("should not allocate")


class Uow:
    def __init__(self, planning, runs): self.planning=planning; self.runs=runs
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def commit(self): pass
    def rollback(self): pass


def test_current_denial_blocks_launch_before_prepare_or_spawn():
    spec = make_run_spec()
    planning = PlanningSpy(spec)
    runs = RunsSpy()
    policy = FakePolicyEvaluator(denied_actions={"launch"})
    executor = FakeWorkflowExecutor()
    runner = FakeProcessRunner()
    service = ExecutionService(
        policy=policy,
        executor=executor,
        process_runner=runner,
        uow_factory=lambda: Uow(planning, runs),
        clock=lambda: NOW,
    )
    with pytest.raises(LaunchDenied):
        service.start(spec.id, actor="alice")
    assert executor.prepare_calls == 0
    assert runner.spawn_calls == 0
    assert len(planning.decisions) == 1
