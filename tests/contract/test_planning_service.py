from datetime import datetime, timezone
from uuid import UUID

import pytest

from bioharness.application.plan_analysis import AssessmentDependencyMismatch, PlanningService, assessment_dependency_fingerprint
from bioharness.application.resolve_task import ResolutionDenied, ResolutionService
from bioharness.domain.assessment import AssessmentStatus, ScientificAssessment
from tests.fakes.factories import make_task
from tests.fakes.providers import FakeDataProvider, FakePolicyEvaluator

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


class PlanningSpy:
    def __init__(self, task):
        self.task = task
        self.policy = []
        self.data_refs = []
        self.configurations = []
        self.contexts = []
        self.run_specs = []

    def get_task(self, task_id):
        return self.task if task_id == self.task.id else None

    def add_policy_decision(self, value): self.policy.append(value)
    def add_data_ref(self, value): self.data_refs.append(value)
    def add_configuration(self, value): self.configurations.append(value)
    def add_context(self, value): self.contexts.append(value)
    def add_run_spec(self, value): self.run_specs.append(value)


class SpyUow:
    def __init__(self, planning):
        self.planning = planning
        self.committed = False
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): return False
    def commit(self): self.committed = True
    def rollback(self): pass


def uow_factory_for(planning):
    return lambda: SpyUow(planning)


def test_authorization_precedes_provider_resolution():
    order = []
    task = make_task()
    planning = PlanningSpy(task)
    policy = FakePolicyEvaluator(order=order)
    provider = FakeDataProvider(order=order)
    service = ResolutionService(policy=policy, provider=provider, uow_factory=uow_factory_for(planning), clock=lambda: NOW)
    refs = service.resolve(task.id, actor="alice")
    assert order == [("policy", "read_resolve"), ("provider", "resolve")]
    assert len(refs) == 1
    assert len(planning.policy) == 1
    assert len(planning.data_refs) == 1


def test_denied_resolution_does_not_touch_provider():
    task = make_task()
    planning = PlanningSpy(task)
    policy = FakePolicyEvaluator(denied_actions={"read_resolve"})
    provider = FakeDataProvider()
    service = ResolutionService(policy=policy, provider=provider, uow_factory=uow_factory_for(planning), clock=lambda: NOW)
    with pytest.raises(ResolutionDenied):
        service.resolve(task.id, actor="alice")
    assert provider.calls == []


def test_assumption_relevant_change_forces_new_assessment():
    task = make_task()
    ref_id = UUID("00000000-0000-0000-0000-000000000102")
    fingerprint = assessment_dependency_fingerprint(
        task=task,
        resolved_data_ref_ids=(ref_id,),
        contract_id="generic",
        contract_revision="1",
        assumption_constraints={"model": "A"},
    )
    assessment = ScientificAssessment(
        id=UUID("00000000-0000-0000-0000-000000000301"),
        task_spec_id=task.id,
        task_spec_revision=task.revision,
        resolved_data_ref_ids=(ref_id,),
        scientific_contract_id="generic",
        scientific_contract_revision="1",
        dependency_fingerprint=fingerprint,
        status=AssessmentStatus.ANALYSIS_SUPPORTED,
        assessed_at=NOW,
    )
    planning = PlanningSpy(task)
    service = PlanningService(uow_factory=uow_factory_for(planning), clock=lambda: NOW)
    with pytest.raises(AssessmentDependencyMismatch):
        service.publish_run_spec(
            task=task,
            assessment=assessment,
            resolved_data_ref_ids=(ref_id,),
            provider_workflow_identity={"provider": "fake", "revision": "r1"},
            result_affecting_parameters={"model": "B"},
            environment_contract={"python": "3.12"},
            reproducibility_contract={"class": "DETERMINISTIC"},
            validation_profile=("candidate", "1"),
            expected_outputs=("result",),
            assumption_constraints={"model": "B"},
            context_policy_decision_ids=(),
        )
    assert planning.run_specs == []
