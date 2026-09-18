import json
import os
import subprocess
from pathlib import Path
from typing import Callable

from bioharness.ports.workflow_executor import (
    ExecutionBinding,
    ExecutionDescriptor,
    ExecutionEvidence,
    ExecutorCapabilities,
    InvocationSpec,
)

from .config import GenomeWebTFReferenceConfig, observe_repo_revision


_PARAMETER_FLAGS = (
    ("min_seqs", "--min-seqs"),
    ("model", "--model"),
    ("bootstrap", "--bootstrap"),
    ("alrt", "--alrt"),
    ("seed", "--seed"),
)
_RESOURCE_FLAGS = (
    ("mafft_threads", "--mafft-threads"),
    ("iqtree_threads", "--iqtree-threads"),
)


class GenomeWebTFExecutorAdapter:
    def __init__(
        self,
        config: GenomeWebTFReferenceConfig,
        *,
        run_command: Callable = subprocess.run,
    ):
        self.config = config
        self.run_command = run_command

    def _require_revision(self) -> None:
        observed = observe_repo_revision(
            self.config.repo_root,
            run_command=self.run_command,
        )
        self.config.require_audited_revision(observed_revision=observed)

    def capabilities(self) -> ExecutorCapabilities:
        self._require_revision()
        return ExecutorCapabilities(
            mode="synchronous_process",
            native_idempotency_key=False,
            durable_external_execution_id=False,
            poll=False,
            reconcile_after_disconnect="limited",
            cancellation="unsupported",
            logs=True,
            trace=True,
        )

    def prepare(self, execution: ExecutionDescriptor) -> InvocationSpec:
        self._require_revision()

        manifest_paths = []
        for resolved_input in execution.resolved_inputs:
            metadata = resolved_input.get("metadata", {})
            path = metadata.get("resolved_manifest_path")
            if path is None:
                raise ValueError(
                    "execution inputs must expose exactly one resolved manifest"
                )
            manifest_paths.append(str(path))
        unique_manifests = set(manifest_paths)
        if not manifest_paths or len(unique_manifests) != 1:
            raise ValueError(
                "execution inputs must expose exactly one resolved manifest"
            )
        resolved_manifest = manifest_paths[0]

        argv = [
            str(self.config.launcher),
            str(self.config.run_root),
            resolved_manifest,
            execution.provider_attempt_name,
        ]
        for key, flag in _PARAMETER_FLAGS:
            if key in execution.result_affecting_parameters:
                argv.extend(
                    [flag, str(execution.result_affecting_parameters[key])]
                )
        for key, flag in _RESOURCE_FLAGS:
            if key in execution.planned_resource_controls:
                argv.extend(
                    [flag, str(execution.planned_resource_controls[key])]
                )
        if self.config.existing_identities is not None:
            argv.extend(
                [
                    "--existing-identities",
                    str(self.config.existing_identities),
                ]
            )

        control_dir = (
            self.config.control_root / execution.provider_attempt_name
        )
        return InvocationSpec(
            argv=tuple(argv),
            cwd=self.config.repo_root,
            env=dict(os.environ),
            stdout_path=control_dir / "stdout.log",
            stderr_path=control_dir / "stderr.log",
        )

    def _observed_evidence(
        self,
        attempt_name: str,
    ) -> tuple[dict[str, str], ...]:
        control_dir = self.config.control_root / attempt_name
        provider_attempt = self.config.run_root / "attempts" / attempt_name
        candidates = (
            ("process_record", control_dir / "process.json"),
            ("wrapper_stdout", control_dir / "stdout.log"),
            ("wrapper_stderr", control_dir / "stderr.log"),
            ("provider_invocation", provider_attempt / "invocation.json"),
            ("resolved_manifest", provider_attempt / "genomes.resolved.tsv"),
            ("execution_log", provider_attempt / "nextflow.log"),
            ("execution_trace", provider_attempt / "trace.tsv"),
            (
                "candidate_manifest",
                provider_attempt / "output" / "candidate" / "manifest.json",
            ),
        )
        return tuple(
            {"role": role, "path": str(path)}
            for role, path in candidates
            if path.is_file()
        )

    @staticmethod
    def _validated_candidate(evidence: tuple[dict[str, str], ...]) -> bool:
        manifest = next(
            (
                Path(item["path"])
                for item in evidence
                if item["role"] == "candidate_manifest"
            ),
            None,
        )
        if manifest is None:
            return False
        try:
            record = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        return (
            record.get("status") == "validated_candidate"
            and record.get("production_publication") == "NOT_AUTHORIZED"
        )

    def inspect(
        self,
        binding: ExecutionBinding | None,
        attempt_payload: dict,
    ) -> ExecutionEvidence:
        self._require_revision()
        attempt_name = str(attempt_payload["provider_attempt_name"])
        evidence = self._observed_evidence(attempt_name)
        if self._validated_candidate(evidence):
            return ExecutionEvidence(
                active=None,
                terminal_outcome="succeeded",
                exit_code=0,
                evidence=evidence,
            )
        return ExecutionEvidence(
            active=None,
            terminal_outcome=None,
            exit_code=None,
            evidence=evidence,
        )

    def discover_artifacts(
        self,
        attempt_payload: dict,
    ) -> tuple[dict[str, object], ...]:
        self._require_revision()
        attempt_name = str(attempt_payload["provider_attempt_name"])
        provider_attempt = self.config.run_root / "attempts" / attempt_name
        candidate = provider_attempt / "output" / "candidate"

        artifacts: list[dict[str, object]] = []

        def add(role: str, path: Path, **metadata: object) -> None:
            if path.is_file():
                item: dict[str, object] = {
                    "path": str(path),
                    "role": role,
                }
                if metadata:
                    item["metadata"] = metadata
                artifacts.append(item)

        add("resolved_manifest", provider_attempt / "genomes.resolved.tsv")
        add("provider_invocation", provider_attempt / "invocation.json")
        add("execution_log", provider_attempt / "nextflow.log")
        add("execution_trace", provider_attempt / "trace.tsv")
        add("candidate_manifest", candidate / "manifest.json")

        for path in sorted(candidate.glob("trees/*/alignment/*")):
            add("alignment", path)
        for path in sorted(candidate.glob("trees/*/tree/*")):
            add("tree", path)
        for path in sorted(candidate.glob("analysis/**/audit.tsv")):
            add("audit_table", path)

        return tuple(artifacts)
