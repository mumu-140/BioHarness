from datetime import datetime, timezone
from uuid import UUID

import pytest

from bioharness.application.execute_run import ExecutionService, LaunchDenied
from bioharness.domain.run import ResolvedConfiguration, RunAttempt, RunAttemptState
from tests.fakes.factories import make_data_ref, make_run_spec
from tests.fakes.providers import (
    FakePolicyEvaluator,
    FakeProcessRunner,
    FakeWorkflowExecutor,
)

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


class PlanningSpy:
    def __init__(self, spec, *, configuration=None, data_refs=()):
        self.spec = spec
        self.configuration = configuration
        self.data_refs = {value.id: value for value in data_refs}
        self.decisions = []

    def get_run_spec(self, value_id, **kwargs):
        return self.spec if value_id == self.spec.id else None

    def get_configuration(self, value_id):
        if self.configuration is not None and value_id == self.configuration.id:
            return self.configuration
        return None

    def get_data_ref(self, value_id):
        return self.data_refs.get(value_id)

    def add_policy_decision(self, value):
        self.decisions.append(value)


class RunsSpy:
    def __init__(self):
        self.allocations = []

    def list_attempts(self, run_spec_id):
        return ()

    def allocate_attempt_intent(self, **kwargs):
        self.allocations.append(kwargs)
        raise AssertionError("should not allocate")


class ExecutableRunsSpy:
    def __init__(self, spec):
        self.spec = spec
        self.attempt = None

    def list_attempts(self, run_spec_id):
        return ()

    def allocate_attempt_intent(
        self,
        *,
        run_spec_id,
        decision,
        capability_snapshot,
        executor_namespace,
        preflight_evidence,
        now,
    ):
        self.attempt = RunAttempt(
            id=UUID("00000000-0000-0000-0000-000000000401"),
            run_spec_id=run_spec_id,
            attempt_number=1,
            executor_namespace=executor_namespace,
            capability_snapshot=capability_snapshot,
            submission_key="submission-1",
            provider_attempt_name="bh-test-1",
            state=RunAttemptState.SUBMITTING,
            submitted_at=now,
        )
        return self.attempt

    def bind_execution(self, attempt_id, binding, occurred_at):
        self.attempt = self.attempt.model_copy(
            update={"binding": binding, "state": RunAttemptState.RUNNING}
        )
        return self.attempt

    def transition(self, attempt_id, target, event_type, payload, occurred_at):
        self.attempt = self.attempt.model_copy(update={"state": target})
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
        preflight=lambda _: {},
        clock=lambda: NOW,
    )
    with pytest.raises(LaunchDenied):
        service.start(spec.id, actor="alice")
    assert executor.prepare_calls == 0
    assert runner.spawn_calls == 0
    assert len(planning.decisions) == 1


def test_execution_service_requires_explicit_preflight():
    spec = make_run_spec()
    planning = PlanningSpy(spec)
    runs = RunsSpy()
    with pytest.raises(TypeError):
        ExecutionService(
            policy=FakePolicyEvaluator(),
            executor=FakeWorkflowExecutor(),
            process_runner=FakeProcessRunner(),
            uow_factory=lambda: Uow(planning, runs),
            clock=lambda: NOW,
        )


def test_prepare_receives_frozen_execution_material_not_run_spec_ids_only():
    spec = make_run_spec()
    ref = make_data_ref().model_copy(
        update={
            "metadata": {"path": "/provider/resolved/input.tsv"},
            "manifest_sha256": "d" * 64,
            "member_manifest_sha256": "e" * 64,
        }
    )
    configuration = ResolvedConfiguration(
        id=spec.configuration_id,
        task_spec_id=spec.task_spec_id,
        assessment_id=spec.assessment_id,
        provider_workflow_identity={
            "provider": "fake-science",
            "workflow": "tf",
            "revision": "r7",
        },
        result_affecting_parameters={"model": "LG", "seed": 12345},
        environment_contract={"python": "3.12", "nextflow": "25.10.4"},
        reproducibility_contract={
            "class": "SEEDED_STOCHASTIC",
            "random_seed": 12345,
        },
        validation_profile_id=spec.validation_profile_id,
        validation_profile_revision=spec.validation_profile_revision,
        planned_resource_controls={"cpus": 4, "memory_gb": 8},
        created_at=NOW,
    )
    planning = PlanningSpy(spec, configuration=configuration, data_refs=(ref,))
    runs = ExecutableRunsSpy(spec)
    executor = FakeWorkflowExecutor()
    service = ExecutionService(
        policy=FakePolicyEvaluator(),
        executor=executor,
        process_runner=FakeProcessRunner(),
        uow_factory=lambda: Uow(planning, runs),
        preflight=lambda _: {"checked": True},
        clock=lambda: NOW,
        executor_namespace="fake-local",
    )

    running = service.start(spec.id, actor="alice")

    assert running.state is RunAttemptState.RUNNING
    prepare_call = next(call for call in executor.calls if call[0] == "prepare")
    material = prepare_call[1]

    assert getattr(material, "run_spec_id", None) == spec.id
    assert getattr(material, "run_spec_hash", None) == spec.run_spec_hash
    assert getattr(material, "attempt_id", None) == runs.attempt.id
    assert getattr(material, "attempt_number", None) == 1
    assert getattr(material, "submission_key", None) == "submission-1"
    assert getattr(material, "provider_attempt_name", None) == "bh-test-1"
    assert getattr(material, "workflow_identity", None) == configuration.provider_workflow_identity
    assert getattr(material, "result_affecting_parameters", None) == configuration.result_affecting_parameters
    assert getattr(material, "environment_contract", None) == configuration.environment_contract
    assert getattr(material, "reproducibility_contract", None) == configuration.reproducibility_contract
    assert getattr(material, "planned_resource_controls", None) == configuration.planned_resource_controls
    assert getattr(material, "expected_outputs", None) == spec.expected_outputs
    assert getattr(material, "validation_profile_id", None) == spec.validation_profile_id
    assert getattr(material, "validation_profile_revision", None) == spec.validation_profile_revision

    inputs = getattr(material, "resolved_inputs", None)
    assert inputs is not None and len(inputs) == 1
    assert inputs[0]["provider"] == ref.provider
    assert inputs[0]["provider_revision"] == ref.provider_revision
    assert inputs[0]["logical_uri"] == ref.logical_uri
    assert inputs[0]["content_sha256"] == ref.content_sha256
    assert inputs[0]["manifest_sha256"] == ref.manifest_sha256
    assert inputs[0]["member_manifest_sha256"] == ref.member_manifest_sha256
    assert inputs[0]["biological_identity"] == ref.biological_identity
    assert inputs[0]["metadata"] == ref.metadata
