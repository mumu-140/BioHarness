import hashlib
import re
import subprocess
from pathlib import Path
from typing import Callable

from bioharness.application.execute_run import PreflightFailed

from .config import (
    AUDITED_REVISION,
    GenomeWebTFReferenceConfig,
    RevisionMismatch,
    observe_repo_revision,
)
from .data_adapter import _sha256_file


def _overlaps(left: Path, right: Path) -> bool:
    return (
        left == right
        or left.is_relative_to(right)
        or right.is_relative_to(left)
    )


def validate_path_isolation(config: GenomeWebTFReferenceConfig) -> None:
    if config.artifact_root is None:
        raise ValueError("artifact_root is required for acceptance isolation")

    writable = tuple(
        path.resolve(strict=False)
        for path in (
            config.planning_root,
            config.control_root,
            config.run_root,
            config.artifact_root,
        )
    )
    protected = tuple(
        path.resolve(strict=False)
        for path in (
            *config.production_roots,
            *config.read_only_source_roots,
        )
    )
    root = Path("/").resolve()
    home = Path.home().resolve(strict=False)

    for path in writable:
        if path in {root, home}:
            raise ValueError(f"unsafe writable root: {path}")
        for protected_path in protected:
            if _overlaps(path, protected_path):
                raise ValueError(
                    f"writable root overlaps protected path: {path} <-> {protected_path}"
                )

    control = config.control_root.resolve(strict=False)
    provider_attempts = (
        config.run_root.resolve(strict=False) / "attempts"
    )
    if _overlaps(control, provider_attempts):
        raise ValueError(
            "control_root overlaps provider-owned run_root/attempts namespace"
        )


def _member_manifest_digest(
    observed_members: list[tuple[str, str]],
) -> str:
    payload = "".join(
        f"{role}\t{sha256}\n"
        for role, sha256 in observed_members
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _probe(
    command_runner: Callable,
    argv: tuple[str, ...],
    *,
    label: str,
):
    try:
        result = command_runner(
            argv,
            check=False,
            text=True,
            capture_output=True,
        )
    except OSError as exc:
        raise PreflightFailed(
            f"environment check failed for {label}: {exc}"
        ) from exc
    if result.returncode != 0:
        detail = str(result.stderr or result.stdout).strip()
        raise PreflightFailed(
            f"environment check failed for {label}: {detail}"
        )
    return result


def _version_text(result) -> str:
    return "\n".join(
        part for part in (result.stdout, result.stderr) if part
    )


def _extract_version(result, pattern: str, *, label: str) -> str:
    match = re.search(pattern, _version_text(result), flags=re.IGNORECASE)
    if match is None:
        raise PreflightFailed(
            f"environment check could not parse {label} version"
        )
    return match.group(1)


def _require_runtime_path(
    path: Path | None,
    *,
    contract_key: str,
) -> str:
    if path is None:
        raise PreflightFailed(
            f"environment contract {contract_key!r} requires a configured executable"
        )
    return str(path)


def _observe_environment(
    *,
    config: GenomeWebTFReferenceConfig,
    environment_contract: dict,
    command_runner: Callable,
) -> dict[str, str]:
    observed: dict[str, str] = {}

    if "nextflow" in environment_contract:
        executable = _require_runtime_path(
            config.nextflow_executable,
            contract_key="nextflow",
        )
        result = _probe(
            command_runner,
            (executable, "-version"),
            label="nextflow",
        )
        observed["nextflow"] = _extract_version(
            result,
            r"\bversion\s+([0-9]+(?:\.[0-9]+)+)",
            label="nextflow",
        )

    if "provider_python" in environment_contract:
        executable = _require_runtime_path(
            config.provider_python,
            contract_key="provider_python",
        )
        result = _probe(
            command_runner,
            (executable, "--version"),
            label="provider_python",
        )
        observed["provider_python"] = _extract_version(
            result,
            r"Python\s+([0-9]+(?:\.[0-9]+)+)",
            label="provider_python",
        )

    if "biopython" in environment_contract:
        executable = _require_runtime_path(
            config.provider_python,
            contract_key="biopython",
        )
        result = _probe(
            command_runner,
            (
                executable,
                "-c",
                "import Bio; print(Bio.__version__)",
            ),
            label="biopython",
        )
        observed["biopython"] = _extract_version(
            result,
            r"([0-9]+(?:\.[0-9]+)+)",
            label="biopython",
        )

    if "mafft" in environment_contract:
        executable = _require_runtime_path(
            config.mafft_executable,
            contract_key="mafft",
        )
        result = _probe(
            command_runner,
            (executable, "--version"),
            label="mafft",
        )
        observed["mafft"] = _extract_version(
            result,
            r"v?([0-9]+(?:\.[0-9]+)+)",
            label="mafft",
        )

    if "iqtree3" in environment_contract:
        executable = _require_runtime_path(
            config.iqtree_executable,
            contract_key="iqtree3",
        )
        result = _probe(
            command_runner,
            (executable, "--version"),
            label="iqtree3",
        )
        observed["iqtree3"] = _extract_version(
            result,
            r"IQ-TREE\s+version\s+([0-9]+(?:\.[0-9]+)+)",
            label="iqtree3",
        )

    _probe(
        command_runner,
        ("ps", "--version"),
        label="ps",
    )
    observed["ps"] = "PASS"

    for key, observed_value in observed.items():
        if key == "ps":
            continue
        expected = environment_contract.get(key)
        if expected is not None and str(expected) != observed_value:
            raise PreflightFailed(
                f"environment contract mismatch for {key}: "
                f"expected={expected} observed={observed_value}"
            )
    return observed


class GenomeWebTFPreflight:
    def __init__(
        self,
        config: GenomeWebTFReferenceConfig,
        *,
        uow_factory,
        command_runner: Callable = subprocess.run,
    ):
        self.config = config
        self.uow_factory = uow_factory
        self.command_runner = command_runner

    def __call__(self, run_spec) -> dict:
        try:
            validate_path_isolation(self.config)
        except ValueError as exc:
            raise PreflightFailed(f"path isolation failed: {exc}") from exc

        try:
            observed_revision = observe_repo_revision(
                self.config.repo_root,
                run_command=self.command_runner,
            )
            self.config.require_audited_revision(
                observed_revision=observed_revision
            )
        except (OSError, subprocess.SubprocessError, RevisionMismatch) as exc:
            raise PreflightFailed(
                f"provider revision check failed: {exc}"
            ) from exc

        with self.uow_factory() as uow:
            stored = uow.planning.get_run_spec(run_spec.id)
            if (
                stored is None
                or stored.run_spec_hash != run_spec.run_spec_hash
            ):
                raise PreflightFailed("RunSpec identity mismatch")

            configuration = uow.planning.get_configuration(
                run_spec.configuration_id
            )
            if configuration is None:
                raise PreflightFailed("ResolvedConfiguration not found")

            refs = []
            for ref_id in run_spec.resolved_data_ref_ids:
                ref = uow.planning.get_data_ref(ref_id)
                if ref is None:
                    raise PreflightFailed(
                        f"ResolvedDataRef not found: {ref_id}"
                    )
                refs.append(ref)

        workflow_revision = configuration.provider_workflow_identity.get(
            "revision"
        )
        if workflow_revision != AUDITED_REVISION:
            raise PreflightFailed(
                "provider workflow revision does not match audited revision"
            )

        resolved_inputs = []
        for ref in refs:
            if ref.provider_revision != AUDITED_REVISION:
                raise PreflightFailed(
                    "resolved input provider revision does not match audited revision"
                )

            manifest_path_value = ref.metadata.get(
                "resolved_manifest_path"
            )
            if not manifest_path_value or not ref.manifest_sha256:
                raise PreflightFailed(
                    "resolved manifest identity is incomplete"
                )
            manifest_path = Path(str(manifest_path_value))
            try:
                observed_manifest_sha = _sha256_file(manifest_path)
            except OSError as exc:
                raise PreflightFailed(
                    f"resolved manifest unavailable: {manifest_path}"
                ) from exc
            if observed_manifest_sha != ref.manifest_sha256:
                raise PreflightFailed(
                    f"resolved manifest digest mismatch: {manifest_path}"
                )

            observed_members: list[tuple[str, str]] = []
            members = ref.metadata.get("members", ())
            if not members or not ref.member_manifest_sha256:
                raise PreflightFailed("resolved member identity is incomplete")
            for member in members:
                role = str(member["role"])
                path = Path(str(member["path"]))
                expected_sha = str(member["sha256"])
                try:
                    observed_sha = _sha256_file(path)
                except OSError as exc:
                    raise PreflightFailed(
                        f"resolved member unavailable: {role} {path}"
                    ) from exc
                if observed_sha != expected_sha:
                    raise PreflightFailed(
                        f"resolved member digest mismatch: {role} {path}"
                    )
                observed_members.append((role, observed_sha))

            if (
                _member_manifest_digest(observed_members)
                != ref.member_manifest_sha256
            ):
                raise PreflightFailed(
                    f"resolved member manifest mismatch: {ref.logical_uri}"
                )

            resolved_inputs.append(
                {
                    "logical_uri": ref.logical_uri,
                    "manifest_sha256": ref.manifest_sha256,
                    "member_manifest_sha256": ref.member_manifest_sha256,
                }
            )

        _probe(
            self.command_runner,
            ("bash", str(self.config.launcher), "--help"),
            label="launcher",
        )
        environment = {
            "launcher_help": "PASS",
            **_observe_environment(
                config=self.config,
                environment_contract=configuration.environment_contract,
                command_runner=self.command_runner,
            ),
        }

        return {
            "run_spec_hash": run_spec.run_spec_hash,
            "provider_revision": observed_revision,
            "resolved_inputs": resolved_inputs,
            "environment": environment,
        }
