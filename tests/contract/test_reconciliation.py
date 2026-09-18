import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from bioharness.adapters.local_process.probe import LocalProcessProbe
from bioharness.application.execute_run import ExecutionService, PriorAttemptUnresolved
from bioharness.application.reconcile_run import ReconciliationService
from bioharness.domain.run import (
    RunAttempt,
    RunAttemptState,
    RunEventType,
    allowed_transition,
)
from bioharness.ports.workflow_executor import ExecutionBinding, ExecutionEvidence
from tests.fakes.factories import make_run_spec
from tests.fakes.providers import FakePolicyEvaluator, FakeProcessRunner, FakeWorkflowExecutor

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


class Runs:
    def __init__(self, attempt):
        self.attempt = attempt
        self.events = []

    def get_attempt(self, value_id, **kwargs):
        return self.attempt if value_id == self.attempt.id else None

    def list_attempts(self, run_spec_id):
        return (self.attempt,)

    def transition(self, attempt_id, target, event_type, payload, occurred_at):
        if not allowed_transition(self.attempt.state, target):
            raise ValueError(
                f"illegal RunAttempt transition {self.attempt.state} -> {target}"
            )
        self.attempt = self.attempt.model_copy(
            update={"state": target, "last_reconciled_at": occurred_at}
        )
        self.events.append(event_type)
        return self.attempt


class Planning:
    def __init__(self, spec):
        self.spec = spec

    def get_run_spec(self, value_id, **kwargs):
        return self.spec

    def add_policy_decision(self, value):
        pass


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


def make_attempt(*, state=RunAttemptState.UNKNOWN, binding=None):
    spec = make_run_spec()
    return spec, RunAttempt(
        id=uuid4(),
        run_spec_id=spec.id,
        attempt_number=1,
        executor_namespace="local",
        capability_snapshot={},
        submission_key="s1",
        provider_attempt_name="p1",
        binding=binding,
        state=state,
        submitted_at=NOW,
    )


class Probe:
    def __init__(self, value):
        self.value = value

    def probe(self, binding):
        return self.value


@pytest.mark.parametrize(
    "evidence,probe_value,expected",
    [
        (
            ExecutionEvidence(active=True, terminal_outcome=None, exit_code=None),
            True,
            RunAttemptState.RUNNING,
        ),
        (
            ExecutionEvidence(active=False, terminal_outcome="succeeded", exit_code=0),
            False,
            RunAttemptState.COLLECTING,
        ),
        (
            ExecutionEvidence(active=False, terminal_outcome="failed", exit_code=9),
            False,
            RunAttemptState.FAILED,
        ),
        (
            ExecutionEvidence(active=None, terminal_outcome=None, exit_code=None),
            None,
            RunAttemptState.NEEDS_OPERATOR_RECONCILIATION,
        ),
    ],
)
def test_reconciliation_matrix(evidence, probe_value, expected):
    binding = ExecutionBinding(
        host="h", pid=123, process_start_token="x", external_execution_id=None
    )
    spec, attempt = make_attempt(binding=binding)
    runs = Runs(attempt)
    service = ReconciliationService(
        executor=FakeWorkflowExecutor(evidence=evidence),
        process_probe=Probe(probe_value),
        uow_factory=lambda: Uow(Planning(spec), runs),
        clock=lambda: NOW,
    )
    result = service.reconcile(attempt.id, actor="alice")
    assert result.state is expected


def test_submitting_without_binding_uses_executor_evidence():
    spec, attempt = make_attempt(state=RunAttemptState.SUBMITTING)
    runs = Runs(attempt)
    executor = FakeWorkflowExecutor(
        evidence=ExecutionEvidence(
            active=False,
            terminal_outcome="succeeded",
            exit_code=0,
            evidence=({"path": "attempt/provider_evidence.json"},),
        )
    )
    service = ReconciliationService(
        executor=executor,
        process_probe=Probe(None),
        uow_factory=lambda: Uow(Planning(spec), runs),
        clock=lambda: NOW,
    )

    result = service.reconcile(attempt.id, actor="alice")

    assert result.state is RunAttemptState.COLLECTING
    inspect_calls = [call for call in executor.calls if call[0] == "inspect"]
    assert len(inspect_calls) == 1
    assert inspect_calls[0][1][0] is None
    assert runs.events == [
        RunEventType.EXECUTION_OUTCOME_UNKNOWN,
        RunEventType.RECONCILIATION_RESOLVED,
    ]


def test_submitting_without_binding_and_without_evidence_requires_operator():
    spec, attempt = make_attempt(state=RunAttemptState.SUBMITTING)
    runs = Runs(attempt)
    service = ReconciliationService(
        executor=FakeWorkflowExecutor(
            evidence=ExecutionEvidence(
                active=None, terminal_outcome=None, exit_code=None
            )
        ),
        process_probe=Probe(None),
        uow_factory=lambda: Uow(Planning(spec), runs),
        clock=lambda: NOW,
    )

    result = service.reconcile(attempt.id, actor="alice")

    assert result.state is RunAttemptState.NEEDS_OPERATOR_RECONCILIATION
    assert runs.events == [
        RunEventType.EXECUTION_OUTCOME_UNKNOWN,
        RunEventType.RECONCILIATION_REQUIRED,
    ]


def test_running_inconclusive_routes_through_unknown_before_operator_review():
    binding = ExecutionBinding(
        host="h", pid=123, process_start_token="x", external_execution_id=None
    )
    spec, attempt = make_attempt(state=RunAttemptState.RUNNING, binding=binding)
    runs = Runs(attempt)
    service = ReconciliationService(
        executor=FakeWorkflowExecutor(
            evidence=ExecutionEvidence(
                active=None, terminal_outcome=None, exit_code=None
            )
        ),
        process_probe=Probe(False),
        uow_factory=lambda: Uow(Planning(spec), runs),
        clock=lambda: NOW,
    )

    result = service.reconcile(attempt.id, actor="alice")

    assert result.state is RunAttemptState.NEEDS_OPERATOR_RECONCILIATION
    assert runs.events == [
        RunEventType.EXECUTION_OUTCOME_UNKNOWN,
        RunEventType.RECONCILIATION_REQUIRED,
    ]


def test_pid_start_token_mismatch_is_indeterminate():
    binding = ExecutionBinding(
        host="local",
        pid=os.getpid(),
        process_start_token="definitely-wrong",
        external_execution_id=None,
    )
    assert LocalProcessProbe().probe(binding) is None


@pytest.mark.parametrize(
    "blocking_state",
    [
        RunAttemptState.SUBMITTING,
        RunAttemptState.RUNNING,
        RunAttemptState.COLLECTING,
        RunAttemptState.UNKNOWN,
        RunAttemptState.NEEDS_OPERATOR_RECONCILIATION,
    ],
)
def test_new_start_blocked_while_prior_attempt_active_or_unresolved(blocking_state):
    spec, attempt = make_attempt(state=blocking_state)
    runs = Runs(attempt)
    runner = FakeProcessRunner()
    preflight_calls = []

    def preflight(_):
        preflight_calls.append(True)
        return {}

    service = ExecutionService(
        policy=FakePolicyEvaluator(),
        executor=FakeWorkflowExecutor(),
        process_runner=runner,
        uow_factory=lambda: Uow(Planning(spec), runs),
        preflight=preflight,
        clock=lambda: NOW,
    )
    with pytest.raises(PriorAttemptUnresolved):
        service.start(spec.id, actor="alice")

    assert preflight_calls == []
    assert runner.spawn_calls == 0
