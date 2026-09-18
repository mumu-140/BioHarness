import subprocess
from pathlib import Path
from typing import Callable

from pydantic import BaseModel, ConfigDict


AUDITED_REVISION = "05072cbbcd533ca59afa13996d8d0edd8f939c6e"


class RevisionMismatch(RuntimeError):
    pass


class GenomeWebTFReferenceConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    repo_root: Path
    provider_revision: str
    input_manifest: Path
    planning_root: Path
    control_root: Path
    run_root: Path
    existing_identities: Path | None = None

    def require_audited_revision(self, *, observed_revision: str) -> None:
        if (
            self.provider_revision != AUDITED_REVISION
            or observed_revision != AUDITED_REVISION
        ):
            raise RevisionMismatch(
                "audited provider revision is required both in configuration "
                f"and observed checkout; configured={self.provider_revision} "
                f"observed={observed_revision}"
            )

    @property
    def validate_script(self) -> Path:
        return self.repo_root / "pipeline/nextflow/scripts/validate_genomes.py"

    @property
    def launcher(self) -> Path:
        return self.repo_root / "pipeline/nextflow/run.sh"


def observe_repo_revision(
    repo_root: Path,
    run_command: Callable = subprocess.run,
) -> str:
    result = run_command(
        ("git", "-C", str(repo_root), "rev-parse", "HEAD"),
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()
