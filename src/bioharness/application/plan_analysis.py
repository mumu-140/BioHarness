from collections.abc import Callable
from datetime import datetime, timezone
from uuid import UUID, uuid4

from bioharness.domain.assessment import AssessmentStatus, ScientificAssessment
from bioharness.domain.run import ContextSnapshot, ResolvedConfiguration, RunSpec
from bioharness.domain.task import ScientificTaskSpec
from bioharness.identity.canonical import sha256_canonical
from bioharness.identity.projections import analysis_projection, run_spec_projection


class AssessmentDependencyMismatch(RuntimeError):
    pass


class UnsupportedAssessment(RuntimeError):
    pass


def assessment_dependency_fingerprint(
    *,
    task: ScientificTaskSpec,
    resolved_data_ref_ids: tuple[UUID, ...],
    contract_id: str,
    contract_revision: str,
    assumption_constraints: dict,
) -> str:
    return sha256_canonical(
        {
            "projection_version": "bioharness.assessment-deps.v1",
            "task_spec": {"id": str(task.id), "revision": task.revision},
            "resolved_data_refs": [str(value) for value in sorted(resolved_data_ref_ids, key=str)],
            "scientific_contract": {"id": contract_id, "revision": contract_revision},
            "assumption_constraints": assumption_constraints,
        }
    )


class PlanningService:
    def __init__(self, *, uow_factory, clock: Callable[[], datetime] | None = None):
        self.uow_factory = uow_factory
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def publish_run_spec(
        self,
        *,
        task: ScientificTaskSpec,
        assessment: ScientificAssessment,
        resolved_data_ref_ids: tuple[UUID, ...],
        provider_workflow_identity: dict,
        result_affecting_parameters: dict,
        environment_contract: dict,
        reproducibility_contract: dict,
        validation_profile: tuple[str, str],
        expected_outputs: tuple[str, ...],
        assumption_constraints: dict,
        context_policy_decision_ids: tuple[UUID, ...],
        planned_resource_controls: dict | None = None,
    ) -> RunSpec:
        if assessment.status in {
            AssessmentStatus.UNRESOLVED,
            AssessmentStatus.NOT_IDENTIFIABLE,
            AssessmentStatus.INCOMPATIBLE,
        }:
            raise UnsupportedAssessment(assessment.status.value)
        expected_dependency = assessment_dependency_fingerprint(
            task=task,
            resolved_data_ref_ids=resolved_data_ref_ids,
            contract_id=assessment.scientific_contract_id,
            contract_revision=assessment.scientific_contract_revision,
            assumption_constraints=assumption_constraints,
        )
        if expected_dependency != assessment.dependency_fingerprint:
            raise AssessmentDependencyMismatch("assessment dependencies no longer match final configuration")

        now = self.clock()
        configuration = ResolvedConfiguration(
            id=uuid4(),
            task_spec_id=task.id,
            assessment_id=assessment.id,
            provider_workflow_identity=provider_workflow_identity,
            result_affecting_parameters=result_affecting_parameters,
            environment_contract=environment_contract,
            reproducibility_contract=reproducibility_contract,
            validation_profile_id=validation_profile[0],
            validation_profile_revision=validation_profile[1],
            assumption_constraints=assumption_constraints,
            planned_resource_controls=planned_resource_controls or {},
            created_at=now,
        )
        context = ContextSnapshot(
            id=uuid4(),
            policy_decision_ids=context_policy_decision_ids,
            metadata={"task_spec_id": str(task.id), "assessment_id": str(assessment.id)},
            created_at=now,
        )
        task_semantics = {
            "question": task.question,
            "requested_inference": task.requested_inference,
            "analysis_class": task.analysis_class,
            "biological_scope": task.biological_scope,
            "output_intent": task.output_intent.value,
            "unresolved_fields": list(task.unresolved_fields),
        }
        analysis = analysis_projection(
            task_semantics=task_semantics,
            input_identities=tuple({"resolved_data_ref_id": str(ref_id)} for ref_id in resolved_data_ref_ids),
            workflow_identity=provider_workflow_identity,
            result_affecting_parameters=result_affecting_parameters,
            environment_contract=environment_contract,
            reproducibility=reproducibility_contract,
        )
        analysis_hash = sha256_canonical(analysis)
        run_projection = run_spec_projection(
            analysis,
            {"id": validation_profile[0], "revision": validation_profile[1]},
            {
                "task_spec_id": str(task.id),
                "assessment_id": str(assessment.id),
                "configuration_id": str(configuration.id),
                "context_snapshot_id": str(context.id),
                "expected_outputs": list(expected_outputs),
            },
        )
        run_spec = RunSpec(
            id=uuid4(),
            task_spec_id=task.id,
            assessment_id=assessment.id,
            configuration_id=configuration.id,
            context_snapshot_id=context.id,
            resolved_data_ref_ids=resolved_data_ref_ids,
            analysis_hash=analysis_hash,
            run_spec_hash=sha256_canonical(run_projection),
            validation_profile_id=validation_profile[0],
            validation_profile_revision=validation_profile[1],
            expected_outputs=expected_outputs,
            executable=True,
            created_at=now,
        )
        with self.uow_factory() as uow:
            uow.planning.add_configuration(configuration)
            uow.planning.add_context(context)
            uow.planning.add_run_spec(run_spec)
            uow.commit()
        return run_spec
