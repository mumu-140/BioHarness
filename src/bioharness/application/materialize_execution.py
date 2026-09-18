from bioharness.domain.run import RunAttempt, RunSpec
from bioharness.ports.workflow_executor import ExecutionDescriptor


class ExecutionMaterializationError(RuntimeError):
    pass


def materialize_execution(
    *,
    uow_factory,
    run_spec: RunSpec,
    attempt: RunAttempt,
) -> ExecutionDescriptor:
    if attempt.run_spec_id != run_spec.id:
        raise ExecutionMaterializationError(
            "RunAttempt does not belong to the requested RunSpec"
        )

    with uow_factory() as uow:
        configuration = uow.planning.get_configuration(run_spec.configuration_id)
        if configuration is None:
            raise ExecutionMaterializationError(
                f"ResolvedConfiguration not found: {run_spec.configuration_id}"
            )
        if (
            configuration.task_spec_id != run_spec.task_spec_id
            or configuration.assessment_id != run_spec.assessment_id
        ):
            raise ExecutionMaterializationError(
                "ResolvedConfiguration does not match RunSpec dependencies"
            )

        refs = []
        for ref_id in run_spec.resolved_data_ref_ids:
            ref = uow.planning.get_data_ref(ref_id)
            if ref is None:
                raise ExecutionMaterializationError(
                    f"ResolvedDataRef not found: {ref_id}"
                )
            refs.append(ref)

    resolved_inputs = tuple(
        {
            "id": str(ref.id),
            "provider": ref.provider,
            "provider_revision": ref.provider_revision,
            "resource_type": ref.resource_type,
            "logical_uri": ref.logical_uri,
            "content_sha256": ref.content_sha256,
            "manifest_sha256": ref.manifest_sha256,
            "member_manifest_sha256": ref.member_manifest_sha256,
            "biological_identity": ref.biological_identity,
            "metadata": ref.metadata,
            "resolved_at": ref.resolved_at.isoformat(),
        }
        for ref in refs
    )

    return ExecutionDescriptor(
        run_spec_id=run_spec.id,
        run_spec_hash=run_spec.run_spec_hash,
        analysis_hash=run_spec.analysis_hash,
        attempt_id=attempt.id,
        attempt_number=attempt.attempt_number,
        submission_key=attempt.submission_key,
        provider_attempt_name=attempt.provider_attempt_name,
        workflow_identity=configuration.provider_workflow_identity,
        resolved_inputs=resolved_inputs,
        result_affecting_parameters=configuration.result_affecting_parameters,
        environment_contract=configuration.environment_contract,
        reproducibility_contract=configuration.reproducibility_contract,
        planned_resource_controls=configuration.planned_resource_controls,
        expected_outputs=run_spec.expected_outputs,
        validation_profile_id=run_spec.validation_profile_id,
        validation_profile_revision=run_spec.validation_profile_revision,
    )
