from typing import Any

ANALYSIS_PROJECTION_VERSION = "bioharness.analysis.v1"
RUN_SPEC_PROJECTION_VERSION = "bioharness.runspec.v1"


def analysis_projection(
    *,
    task_semantics: dict[str, Any],
    input_identities: tuple[dict[str, Any], ...],
    workflow_identity: dict[str, Any],
    result_affecting_parameters: dict[str, Any],
    environment_contract: dict[str, Any],
    reproducibility: dict[str, Any],
) -> dict[str, Any]:
    return {
        "projection_version": ANALYSIS_PROJECTION_VERSION,
        "task_semantics": task_semantics,
        "input_identities": list(input_identities),
        "workflow_identity": workflow_identity,
        "result_affecting_parameters": result_affecting_parameters,
        "environment_contract": environment_contract,
        "reproducibility": reproducibility,
    }


def run_spec_projection(
    analysis: dict[str, Any],
    validation_profile: dict[str, Any],
    control_context: dict[str, Any],
) -> dict[str, Any]:
    return {
        "projection_version": RUN_SPEC_PROJECTION_VERSION,
        "analysis": analysis,
        "validation_profile": validation_profile,
        "control_context": control_context,
    }
