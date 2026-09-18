import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from bioharness.adapters.local_process.probe import LocalProcessProbe
from bioharness.adapters.local_process.runner import LocalProcessRunner
from bioharness.adapters.postgres.session import PostgresUnitOfWork
from bioharness.application.collect_artifacts import ArtifactCollectionService
from bioharness.application.execute_run import ExecutionService, PreflightFailed, PriorAttemptUnresolved
from bioharness.application.memory import MemoryService
from bioharness.application.plan_analysis import PlanningService, assessment_dependency_fingerprint
from bioharness.application.reconcile_run import ReconciliationService
from bioharness.application.resolve_task import ResolutionService
from bioharness.application.validate_run import ValidationService
from bioharness.domain.assessment import AssessmentStatus, ScientificAssessment
from bioharness.domain.run import RunAttemptState, RunEventType
from bioharness.domain.validation import ValidationOutcome, ValidationProfile, ValidationRequirement
from bioharness.ports.data_provider import ProviderResolution, ProviderResource
from bioharness.ports.workflow_executor import ExecutionEvidence, ExecutorCapabilities, InvocationSpec
from tests.fakes.factories import make_task
from tests.fakes.providers import FakeDataProvider, FakePolicyEvaluator, FakeProcessRunner, FakeWorkflowExecutor

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)
FAKE_PROVIDER = Path(__file__).parents[1] / "fixtures" / "fake_science_provider.py"


def sha256_file(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class FakeScienceExecutor:
    def __init__(self, *, run_root: Path):
        self.run_root=run_root

    def capabilities(self):
        return ExecutorCapabilities(
            mode="synchronous_process", native_idempotency_key=False,
            durable_external_execution_id=False, poll=False,
            reconcile_after_disconnect="limited", cancellation="unsupported",
            logs=True, trace=False,
        )

    def _outdir(self, attempt_payload):
        return self.run_root / attempt_payload["provider_attempt_name"]

    def prepare(self, execution):
        outdir=self.run_root / execution.provider_attempt_name
        input_path=Path(execution.resolved_inputs[0]["metadata"]["path"])
        return InvocationSpec(
            argv=(sys.executable, str(FAKE_PROVIDER), "--input", str(input_path), "--outdir", str(outdir), "--mode", "success"),
            cwd=self.run_root,
            env=dict(os.environ),
            stdout_path=outdir / "stdout.log",
            stderr_path=outdir / "stderr.log",
        )

    def inspect(self, binding, attempt_payload):
        evidence_path=self._outdir(attempt_payload) / "provider_evidence.json"
        if not evidence_path.exists():
            return ExecutionEvidence(active=None, terminal_outcome=None, exit_code=None)
        evidence=json.loads(evidence_path.read_text(encoding="utf-8"))
        return ExecutionEvidence(
            active=False,
            terminal_outcome=evidence["status"],
            exit_code=evidence["exit_code"],
            evidence=({"path": str(evidence_path)},),
        )

    def discover_artifacts(self, attempt_payload):
        outdir=self._outdir(attempt_payload)
        candidates=[]
        for name, role in (("result.txt", "result"), ("provider_evidence.json", "provider_evidence")):
            path=outdir / name
            if path.exists():
                candidates.append({"path": str(path), "role": role, "metadata": {"provider": "fake-science"}})
        return tuple(candidates)


class FileIdentityPreflight:
    def __init__(self, database_url: str): self.database_url=database_url

    def __call__(self, run_spec):
        evidence=[]
        with PostgresUnitOfWork(self.database_url) as uow:
            for ref_id in run_spec.resolved_data_ref_ids:
                ref=uow.planning.get_data_ref(ref_id)
                path=Path(ref.metadata["path"])
                observed=sha256_file(path)
                if observed != ref.content_sha256:
                    raise PreflightFailed(f"input identity changed: {ref.logical_uri}")
                evidence.append({"resolved_data_ref_id": str(ref.id), "sha256": observed})
        return {"inputs": evidence}


def candidate_profile():
    return ValidationProfile(
        profile_id="candidate", revision="1",
        requirements=(
            ValidationRequirement(kind="provider_contract", allowed_outcomes=(ValidationOutcome.PASS, ValidationOutcome.PASS_WITH_LIMITATIONS)),
            ValidationRequirement(kind="artifact_integrity", allowed_outcomes=(ValidationOutcome.PASS,)),
            ValidationRequirement(kind="provenance_completeness", allowed_outcomes=(ValidationOutcome.PASS,)),
        ),
    )


def planned_run(database_url: str, tmp_path: Path):
    input_path=tmp_path / "input.txt"
    input_path.write_text("science-input", encoding="utf-8")
    task=make_task()
    with PostgresUnitOfWork(database_url) as uow:
        uow.planning.add_task(task)
        uow.validation.add_profile(candidate_profile())
        uow.commit()

    resolution=ProviderResolution(
        provider="fake-science", provider_revision="r1",
        resources=(ProviderResource(
            logical_uri="provider://resource/A", resource_type="generic",
            biological_identity={"sample":"A"},
            content_identity={"content_sha256": sha256_file(input_path)},
            metadata={"path": str(input_path)},
        ),),
        evidence=({"source":"fake-provider"},),
    )
    refs=ResolutionService(
        policy=FakePolicyEvaluator(), provider=FakeDataProvider(resolution=resolution),
        uow_factory=lambda: PostgresUnitOfWork(database_url), clock=lambda: NOW,
    ).resolve(task.id, actor="alice")

    fingerprint=assessment_dependency_fingerprint(
        task=task, resolved_data_ref_ids=tuple(ref.id for ref in refs),
        contract_id="generic", contract_revision="1", assumption_constraints={},
    )
    assessment=ScientificAssessment(
        id=uuid4(), task_spec_id=task.id, task_spec_revision=task.revision,
        resolved_data_ref_ids=tuple(ref.id for ref in refs),
        scientific_contract_id="generic", scientific_contract_revision="1",
        dependency_fingerprint=fingerprint, status=AssessmentStatus.ANALYSIS_SUPPORTED,
        assessed_at=NOW,
    )
    with PostgresUnitOfWork(database_url) as uow:
        uow.planning.add_assessment(assessment)
        uow.commit()

    spec=PlanningService(
        uow_factory=lambda: PostgresUnitOfWork(database_url), clock=lambda: NOW,
    ).publish_run_spec(
        task=task, assessment=assessment, resolved_data_ref_ids=tuple(ref.id for ref in refs),
        provider_workflow_identity={"provider":"fake-science","revision":"r1"},
        result_affecting_parameters={"mode":"success"},
        environment_contract={"python":"3.12+"},
        reproducibility_contract={"class":"DETERMINISTIC"},
        validation_profile=("candidate","1"), expected_outputs=("result",),
        assumption_constraints={}, context_policy_decision_ids=(),
    )
    return task, refs, spec, input_path


def wait_for(path: Path, timeout: float = 5.0):
    deadline=time.time()+timeout
    while time.time() < deadline:
        if path.exists(): return
        time.sleep(0.05)
    raise AssertionError(f"timed out waiting for {path}")


def test_provider_agnostic_p0_success_flow(migrated_database, tmp_path):
    _, refs, spec, input_path=planned_run(migrated_database, tmp_path)
    run_root=tmp_path / "runs"; run_root.mkdir()
    artifact_root=tmp_path / "artifacts"; artifact_root.mkdir()
    executor=FakeScienceExecutor(run_root=run_root)
    execution=ExecutionService(
        policy=FakePolicyEvaluator(), executor=executor, process_runner=LocalProcessRunner(),
        uow_factory=lambda: PostgresUnitOfWork(migrated_database),
        preflight=FileIdentityPreflight(migrated_database), clock=lambda: NOW,
        executor_namespace="fake-local",
    )
    running=execution.start(spec.id, actor="alice")
    assert running.state is RunAttemptState.RUNNING
    evidence_path=run_root / running.provider_attempt_name / "provider_evidence.json"
    wait_for(evidence_path)

    collecting=ReconciliationService(
        executor=executor, process_probe=LocalProcessProbe(),
        uow_factory=lambda: PostgresUnitOfWork(migrated_database), clock=lambda: NOW,
    ).reconcile(running.id, actor="alice")
    assert collecting.state is RunAttemptState.COLLECTING

    artifacts=ArtifactCollectionService(
        executor=executor, uow_factory=lambda: PostgresUnitOfWork(migrated_database),
        allowed_roots=(run_root, artifact_root), clock=lambda: NOW,
    ).collect(running.id)
    assert {artifact.role for artifact in artifacts} == {"result", "provider_evidence"}

    validation=ValidationService(uow_factory=lambda: PostgresUnitOfWork(migrated_database), clock=lambda: NOW)
    reports=(
        validation.report(kind="provider_contract", subject_type="run_attempt", subject_id=str(running.id), validator="fake-science", validator_revision="r1", outcome=ValidationOutcome.PASS, evidence_refs=(artifacts[1].uri,)),
        validation.report(kind="artifact_integrity", subject_type="run_attempt", subject_id=str(running.id), validator="bioharness", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=tuple(a.uri for a in artifacts)),
        validation.report(kind="provenance_completeness", subject_type="run_attempt", subject_id=str(running.id), validator="bioharness", validator_revision="1", outcome=ValidationOutcome.PASS, evidence_refs=(f"runspec:{spec.id}", f"data:{refs[0].id}")),
    )
    evaluation=validation.evaluate("candidate", "1", tuple(report.id for report in reports))
    assert evaluation.outcome is ValidationOutcome.PASS

    memory=MemoryService(uow_factory=lambda: PostgresUnitOfWork(migrated_database), clock=lambda: NOW)
    candidate=memory.record(
        scope="project:p0", kind="procedure", statement="Fake provider completed with explicit evidence",
        tags=("execution","validated"), applicability={"provider":"fake-science","workflow":"r1"},
        evidence_refs=(f"validation:{evaluation.id}",),
    )
    assert memory.search(scope="project:p0", tags=("validated",), applicability={"provider":"fake-science"}) == (candidate,)

    with PostgresUnitOfWork(migrated_database) as uow:
        attempts=uow.runs.list_attempts(spec.id)
        events=uow.runs.list_events(running.id)
        stored_artifacts=uow.artifacts.list_for_attempt(running.id)
    assert len(attempts) == 1 and attempts[0].state is RunAttemptState.FINISHED
    assert [event.event_type for event in events] == [
        RunEventType.ATTEMPT_CREATED,
        RunEventType.AUTHORIZATION_CHECKED,
        RunEventType.SUBMISSION_INTENT_RECORDED,
        RunEventType.EXTERNAL_PROCESS_BOUND,
        RunEventType.EXECUTION_STARTED,
        RunEventType.RECONCILIATION_RESOLVED,
        RunEventType.ARTIFACT_DISCOVERED,
        RunEventType.ARTIFACT_REGISTERED,
        RunEventType.ARTIFACT_DISCOVERED,
        RunEventType.ARTIFACT_REGISTERED,
        RunEventType.COLLECTION_FINISHED,
    ]
    assert {artifact.content_sha256 for artifact in stored_artifacts} == {sha256_file(Path(artifact.uri.removeprefix("file://"))) for artifact in stored_artifacts}
    assert not hasattr(validation, "publish")
    assert not hasattr(memory, "authorize")


def test_unknown_outcome_blocks_duplicate_submission(migrated_database, tmp_path):
    _, _, spec, _=planned_run(migrated_database, tmp_path)
    runner=FakeProcessRunner(raise_after_possible_spawn=True)
    service=ExecutionService(
        policy=FakePolicyEvaluator(), executor=FakeWorkflowExecutor(), process_runner=runner,
        uow_factory=lambda: PostgresUnitOfWork(migrated_database),
        preflight=lambda _: {"checked": True}, clock=lambda: NOW,
    )
    unknown=service.start(spec.id, actor="alice")
    assert unknown.state is RunAttemptState.UNKNOWN
    with pytest.raises(PriorAttemptUnresolved):
        service.start(spec.id, actor="alice")
    assert runner.spawn_calls == 1
