import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from bioharness.adapters.local_process.probe import LocalProcessProbe
from bioharness.application.execute_run import ExecutionService, PriorAttemptUnresolved
from bioharness.application.reconcile_run import ReconciliationService
from bioharness.domain.run import RunAttempt, RunAttemptState, RunEventType
from bioharness.ports.workflow_executor import ExecutionBinding, ExecutionEvidence
from tests.fakes.factories import make_run_spec
from tests.fakes.providers import FakePolicyEvaluator, FakeProcessRunner, FakeWorkflowExecutor

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


class Runs:
    def __init__(self, attempt): self.attempt=attempt; self.events=[]
    def get_attempt(self, value_id, **kwargs): return self.attempt if value_id == self.attempt.id else None
    def list_attempts(self, run_spec_id): return (self.attempt,)
    def transition(self, attempt_id, target, event_type, payload, occurred_at):
        self.attempt=self.attempt.model_copy(update={"state": target, "last_reconciled_at": occurred_at})
        self.events.append(event_type)
        return self.attempt


class Planning:
    def __init__(self, spec): self.spec=spec
    def get_run_spec(self, value_id, **kwargs): return self.spec
    def add_policy_decision(self, value): pass


class Uow:
    def __init__(self, planning, runs): self.planning=planning; self.runs=runs
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def commit(self): pass
    def rollback(self): pass


def make_unknown(binding=None):
    spec=make_run_spec()
    return spec, RunAttempt(
        id=uuid4(), run_spec_id=spec.id, attempt_number=1,
        executor_namespace="local", capability_snapshot={}, submission_key="s1",
        provider_attempt_name="p1", binding=binding,
        state=RunAttemptState.UNKNOWN, submitted_at=NOW,
    )


class Probe:
    def __init__(self, value): self.value=value
    def probe(self, binding): return self.value


@pytest.mark.parametrize(
    "evidence,probe_value,expected",
    [
        (ExecutionEvidence(active=True, terminal_outcome=None, exit_code=None), True, RunAttemptState.RUNNING),
        (ExecutionEvidence(active=False, terminal_outcome="succeeded", exit_code=0), False, RunAttemptState.COLLECTING),
        (ExecutionEvidence(active=False, terminal_outcome="failed", exit_code=9), False, RunAttemptState.FAILED),
        (ExecutionEvidence(active=None, terminal_outcome=None, exit_code=None), None, RunAttemptState.NEEDS_OPERATOR_RECONCILIATION),
    ],
)
def test_reconciliation_matrix(evidence, probe_value, expected):
    binding=ExecutionBinding(host="h",pid=123,process_start_token="x",external_execution_id=None)
    spec,attempt=make_unknown(binding)
    runs=Runs(attempt)
    service=ReconciliationService(
        executor=FakeWorkflowExecutor(evidence=evidence), process_probe=Probe(probe_value),
        uow_factory=lambda: Uow(Planning(spec),runs), clock=lambda: NOW,
    )
    result=service.reconcile(attempt.id,actor="alice")
    assert result.state is expected


def test_pid_start_token_mismatch_is_indeterminate():
    binding=ExecutionBinding(host="local",pid=os.getpid(),process_start_token="definitely-wrong",external_execution_id=None)
    assert LocalProcessProbe().probe(binding) is None


def test_new_start_blocked_while_prior_attempt_unresolved():
    spec,attempt=make_unknown()
    runs=Runs(attempt)
    service=ExecutionService(
        policy=FakePolicyEvaluator(), executor=FakeWorkflowExecutor(), process_runner=FakeProcessRunner(),
        uow_factory=lambda: Uow(Planning(spec),runs), clock=lambda: NOW,
    )
    with pytest.raises(PriorAttemptUnresolved):
        service.start(spec.id,actor="alice")
