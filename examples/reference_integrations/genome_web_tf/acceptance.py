import argparse
import json
import subprocess
import tomllib
from pathlib import Path
from typing import Callable
from uuid import UUID

from bioharness.ports.workflow_executor import ExecutionDescriptor

from .config import (
    AUDITED_REVISION,
    GenomeWebTFReferenceConfig,
    observe_repo_revision,
)
from .data_adapter import _configured_scope
from .executor_adapter import GenomeWebTFExecutorAdapter
from .preflight import validate_path_isolation


_DRY_RUN_PARAMETERS = {
    "min_seqs": 4,
    "model": "MFP",
    "bootstrap": 1000,
    "alrt": 1000,
    "seed": 12345,
}
_DRY_RUN_RESOURCES = {
    "mafft_threads": 1,
    "iqtree_threads": 1,
}


def load_config(path: Path) -> GenomeWebTFReferenceConfig:
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    payload["repo_root"] = payload.pop("provider_repo")
    return GenomeWebTFReferenceConfig.model_validate(payload)


def build_dry_run_report(
    config: GenomeWebTFReferenceConfig,
    *,
    run_command: Callable = subprocess.run,
) -> dict:
    validate_path_isolation(config)
    observed = observe_repo_revision(
        config.repo_root,
        run_command=run_command,
    )
    config.require_audited_revision(observed_revision=observed)

    logical_resources = list(_configured_scope(config.input_manifest))
    predicted_manifest = (
        config.planning_root / "dry-run" / "genomes.resolved.tsv"
    )
    execution = ExecutionDescriptor(
        run_spec_id=UUID("00000000-0000-0000-0000-00000000d001"),
        run_spec_hash="0" * 64,
        analysis_hash="1" * 64,
        attempt_id=UUID("00000000-0000-0000-0000-00000000d002"),
        attempt_number=1,
        submission_key="dry-run",
        provider_attempt_name="bh-dry-run-1",
        workflow_identity={
            "provider": "genome-web",
            "revision": AUDITED_REVISION,
        },
        resolved_inputs=tuple(
            {
                "logical_uri": logical_uri,
                "provider": "genome-web",
                "provider_revision": AUDITED_REVISION,
                "metadata": {
                    "resolved_manifest_path": str(predicted_manifest)
                },
            }
            for logical_uri in logical_resources
        ),
        result_affecting_parameters=_DRY_RUN_PARAMETERS,
        environment_contract={"nextflow": "25.10.4"},
        reproducibility_contract={
            "class": "provider-audited-reference"
        },
        planned_resource_controls=_DRY_RUN_RESOURCES,
        expected_outputs=("candidate_manifest",),
        validation_profile_id="candidate",
        validation_profile_revision="1",
    )
    executor = GenomeWebTFExecutorAdapter(
        config,
        run_command=run_command,
    )
    invocation = executor.prepare(execution)

    return {
        "provider_revision": observed,
        "paths": {
            "provider_repo": str(config.repo_root),
            "planning_root": str(config.planning_root),
            "control_root": str(config.control_root),
            "run_root": str(config.run_root),
            "artifact_root": str(config.artifact_root),
        },
        "logical_resources": logical_resources,
        "planned_command": list(invocation.argv),
        "preflight_checks": [
            "provider_revision",
            "path_isolation",
            "frozen_resolved_identity",
            "launcher_environment",
        ],
        "policy_outcomes": {
            "read_resolve": "ALLOW",
            "launch": "ALLOW",
            "production_publication": "DENY",
            "canonical_mutation": "DENY",
        },
    }


def main(
    argv: list[str] | None = None,
    *,
    run_command: Callable = subprocess.run,
) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    if not args.dry_run:
        parser.error("live acceptance is a separate gated task; use --dry-run")
    report = build_dry_run_report(
        config,
        run_command=run_command,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
