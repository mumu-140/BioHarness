import csv
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Callable

from bioharness.ports.data_provider import ProviderResolution, ProviderResource

from .config import GenomeWebTFReferenceConfig, observe_repo_revision


_MEMBER_ROLES = (
    "gene_tsv",
    "transcript_tsv",
    "protein_tsv",
    "protein_fasta",
    "tf_tsv",
    "tf_gene_tsv",
)
_RESOLVED_COLUMNS = (
    "species_id",
    "uid",
    "genome_build",
    "annotation_release",
    "release_id",
    *_MEMBER_ROLES,
)


class ProviderResolutionError(RuntimeError):
    def __init__(self, returncode: int, stderr: str):
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(
            f"Genome-web resolver failed with exit code {returncode}: {stderr.strip()}"
        )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _logical_uri(species_id: str, uid: str) -> str:
    return f"genomeweb:registered-genome:{species_id}:{uid}"


def _configured_scope(input_manifest: Path) -> tuple[str, ...]:
    with input_manifest.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames or not {"species_id", "uid"} <= set(reader.fieldnames):
            raise ValueError(
                "configured manifest must expose species_id and uid for logical scope"
            )
        return tuple(
            _logical_uri(row["species_id"], row["uid"])
            for row in reader
        )


def _member_identity(row: dict[str, str]) -> tuple[tuple[dict[str, object], ...], str]:
    members = []
    digest_lines = []
    for role in _MEMBER_ROLES:
        path = Path(row[role]).resolve(strict=True)
        sha256 = _sha256_file(path)
        members.append(
            {
                "role": role,
                "path": str(path),
                "sha256": sha256,
                "size_bytes": path.stat().st_size,
            }
        )
        digest_lines.append(f"{role}\t{sha256}\n")
    member_manifest_sha256 = hashlib.sha256(
        "".join(digest_lines).encode("utf-8")
    ).hexdigest()
    return tuple(members), member_manifest_sha256


class GenomeWebTFDataAdapter:
    def __init__(
        self,
        config: GenomeWebTFReferenceConfig,
        *,
        run_command: Callable = subprocess.run,
    ):
        self.config = config
        self.run_command = run_command

    def resolve(
        self,
        logical_resources: tuple[str, ...],
        context: dict,
    ) -> ProviderResolution:
        expected = _configured_scope(self.config.input_manifest)
        if (
            len(logical_resources) != len(expected)
            or set(logical_resources) != set(expected)
        ):
            raise ValueError(
                "requested logical resources must exactly match configured manifest"
            )

        observed_revision = observe_repo_revision(
            self.config.repo_root,
            run_command=self.run_command,
        )
        self.config.require_audited_revision(
            observed_revision=observed_revision
        )

        task_id = str(context["task_id"])
        task_revision = context["task_revision"]
        planning_dir = self.config.planning_root / task_id
        planning_dir.mkdir(parents=True, exist_ok=True)
        resolved_manifest = planning_dir / "genomes.resolved.tsv"

        argv = [
            sys.executable,
            str(self.config.validate_script),
            "--genomes",
            str(self.config.input_manifest),
            "--output",
            str(resolved_manifest),
        ]
        if self.config.existing_identities is not None:
            argv.extend(
                ["--existing-identities", str(self.config.existing_identities)]
            )

        result = self.run_command(
            tuple(argv),
            check=False,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            raise ProviderResolutionError(result.returncode, result.stderr)

        manifest_sha256 = _sha256_file(resolved_manifest)
        with resolved_manifest.open(
            encoding="utf-8",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if not reader.fieldnames or not set(_RESOLVED_COLUMNS) <= set(
                reader.fieldnames
            ):
                raise ValueError(
                    "resolved manifest does not match audited Genome-web columns"
                )
            rows = list(reader)

        resolved_scope = tuple(
            _logical_uri(row["species_id"], row["uid"])
            for row in rows
        )
        if (
            len(resolved_scope) != len(logical_resources)
            or set(resolved_scope) != set(logical_resources)
        ):
            raise ValueError(
                "resolved logical resources do not exactly match requested scope"
            )

        resources = []
        for row in rows:
            members, member_manifest_sha256 = _member_identity(row)
            resources.append(
                ProviderResource(
                    logical_uri=_logical_uri(row["species_id"], row["uid"]),
                    resource_type="registered_genome",
                    biological_identity={
                        "species_id": row["species_id"],
                        "uid": row["uid"],
                        "genome_build": row["genome_build"],
                        "annotation_release": row["annotation_release"],
                        "release_id": row["release_id"],
                    },
                    content_identity={
                        "manifest_sha256": manifest_sha256,
                        "member_manifest_sha256": member_manifest_sha256,
                    },
                    metadata={
                        "resolved_manifest_path": str(resolved_manifest),
                        "members": members,
                        "task_revision": task_revision,
                    },
                )
            )

        return ProviderResolution(
            provider="genome-web",
            provider_revision=self.config.provider_revision,
            resources=tuple(resources),
            evidence=(
                {
                    "kind": "resolved_manifest",
                    "path": str(resolved_manifest),
                    "sha256": manifest_sha256,
                },
            ),
        )
