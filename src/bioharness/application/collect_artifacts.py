from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from bioharness.adapters.filesystem.artifacts import inspect_artifact
from bioharness.domain.artifact import Artifact
from bioharness.domain.run import RunAttemptState, RunEventType


class AttemptNotFound(LookupError):
    pass


class ArtifactCollectionStateError(RuntimeError):
    pass


class ArtifactCollectionService:
    def __init__(self, *, executor, uow_factory, allowed_roots: tuple[Path, ...], clock: Callable[[], datetime] | None = None):
        self.executor = executor
        self.uow_factory = uow_factory
        self.allowed_roots = allowed_roots
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def collect(self, attempt_id: UUID) -> tuple[Artifact, ...]:
        with self.uow_factory() as uow:
            attempt = uow.runs.get_attempt(attempt_id)
        if attempt is None:
            raise AttemptNotFound(str(attempt_id))
        if attempt.state is not RunAttemptState.COLLECTING:
            raise ArtifactCollectionStateError(f"attempt must be COLLECTING, got {attempt.state.value}")

        candidates = self.executor.discover_artifacts(attempt.model_dump(mode="json"))
        artifacts: list[Artifact] = []
        now = self.clock()
        for candidate in candidates:
            inspection = inspect_artifact(
                Path(candidate["path"]),
                role=candidate["role"],
                allowed_roots=self.allowed_roots,
            )
            artifacts.append(
                Artifact(
                    id=uuid4(),
                    run_spec_id=attempt.run_spec_id,
                    run_attempt_id=attempt.id,
                    role=inspection.role,
                    content_sha256=inspection.content_sha256,
                    size_bytes=inspection.size_bytes,
                    uri=inspection.path.as_uri(),
                    metadata=candidate.get("metadata", {}),
                    registered_at=now,
                )
            )

        with self.uow_factory() as uow:
            for artifact in artifacts:
                uow.runs.append_event(
                    attempt.id,
                    RunEventType.ARTIFACT_DISCOVERED,
                    {"role": artifact.role, "uri": artifact.uri},
                    now,
                )
                uow.artifacts.add(artifact)
                uow.runs.append_event(
                    attempt.id,
                    RunEventType.ARTIFACT_REGISTERED,
                    {"artifact_id": str(artifact.id), "sha256": artifact.content_sha256},
                    now,
                )
            uow.runs.transition(
                attempt.id,
                RunAttemptState.FINISHED,
                RunEventType.COLLECTION_FINISHED,
                {"artifact_count": len(artifacts)},
                now,
            )
            uow.commit()
        return tuple(artifacts)
