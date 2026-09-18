from pathlib import Path

from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    database_url: str
    run_root: Path
    artifact_root: Path
    protected_roots: tuple[Path, ...] = ()
