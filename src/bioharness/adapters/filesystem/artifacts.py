import hashlib
from pathlib import Path

from pydantic import ConfigDict

from bioharness.domain.base import FrozenRecord


class ArtifactPathOutsideAllowedRoots(ValueError):
    pass


class ArtifactInspection(FrozenRecord):
    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    path: Path
    role: str
    content_sha256: str
    size_bytes: int


def _is_within(path: Path, roots: tuple[Path, ...]) -> bool:
    return any(path == root or path.is_relative_to(root) for root in roots)


def inspect_artifact(
    path: Path,
    role: str,
    *,
    allowed_roots: tuple[Path, ...] | None = None,
) -> ArtifactInspection:
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(f"artifact is not a regular file: {resolved}")
    if allowed_roots is not None:
        roots = tuple(root.resolve(strict=False) for root in allowed_roots)
        if not _is_within(resolved, roots):
            raise ArtifactPathOutsideAllowedRoots(str(resolved))

    digest = hashlib.sha256()
    size = 0
    with resolved.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    return ArtifactInspection(
        path=resolved,
        role=role,
        content_sha256=digest.hexdigest(),
        size_bytes=size,
    )
