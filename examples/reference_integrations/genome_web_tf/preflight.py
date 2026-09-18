import hashlib
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

        try:
            launcher_check = self.command_runner(
                (str(self.config.launcher), "--help"),
                check=False,
                text=True,
                capture_output=True,
            )
        except OSError as exc:
            raise PreflightFailed(
                f"launcher environment check failed: {exc}"
            ) from exc
        if launcher_check.returncode != 0:
            raise PreflightFailed(
                "launcher environment check failed: "
                + str(launcher_check.stderr).strip()
            )

        return {
            "run_spec_hash": run_spec.run_spec_hash,
            "provider_revision": observed_revision,
            "resolved_inputs": resolved_inputs,
            "environment": {
                "launcher_help": "PASS",
            },
        }
