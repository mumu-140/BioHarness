from datetime import datetime, timezone
from uuid import uuid4

from bioharness.application.collect_artifacts import ArtifactCollectionService
from bioharness.domain.run import RunAttempt, RunAttemptState, RunEventType
from tests.fakes.factories import make_run_spec
from tests.fakes.providers import FakeWorkflowExecutor

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


class Runs:
    def __init__(self, attempt):
        self.attempt = attempt
        self.events = []

    def get_attempt(self, value_id, **kwargs):
        return self.attempt if value_id == self.attempt.id else None

    def append_event(self, attempt_id, event_type, payload, occurred_at):
        self.events.append(event_type)

    def transition(self, attempt_id, target, event_type, payload, occurred_at):
        self.events.append(event_type)
        self.attempt = self.attempt.model_copy(update={"state": target})
        return self.attempt


class Artifacts:
    def __init__(self):
        self.values = []

    def add(self, value):
        self.values.append(value)


class Uow:
    def __init__(self, runs, artifacts):
        self.runs = runs
        self.artifacts = artifacts

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def commit(self):
        pass

    def rollback(self):
        pass


def test_collection_registers_digest_events_and_finishes(tmp_path):
    spec = make_run_spec()
    attempt = RunAttempt(
        id=uuid4(),
        run_spec_id=spec.id,
        attempt_number=1,
        executor_namespace="fake",
        capability_snapshot={},
        submission_key="s1",
        provider_attempt_name="p1",
        state=RunAttemptState.COLLECTING,
        submitted_at=NOW,
    )
    result = tmp_path / "runs" / "p1" / "result.txt"
    result.parent.mkdir(parents=True)
    result.write_text("abc", encoding="utf-8")
    executor = FakeWorkflowExecutor(artifacts=({"path": str(result), "role": "result", "metadata": {"kind": "text"}},))
    runs = Runs(attempt)
    artifacts = Artifacts()
    service = ArtifactCollectionService(
        executor=executor,
        uow_factory=lambda: Uow(runs, artifacts),
        allowed_roots=(tmp_path / "runs", tmp_path / "artifacts"),
        clock=lambda: NOW,
    )

    collected = service.collect(attempt.id)

    assert len(collected) == 1
    assert collected[0].content_sha256 == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert artifacts.values == list(collected)
    assert runs.attempt.state is RunAttemptState.FINISHED
    assert runs.events == [
        RunEventType.ARTIFACT_DISCOVERED,
        RunEventType.ARTIFACT_REGISTERED,
        RunEventType.COLLECTION_FINISHED,
    ]
