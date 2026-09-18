import importlib
import json
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from bioharness.ports.workflow_executor import ExecutionDescriptor


AUDITED = "05072cbbcd533ca59afa13996d8d0edd8f939c6e"


def module():
    return importlib.import_module(
        "examples.reference_integrations.genome_web_tf.executor_adapter"
    )


def config_module():
    return importlib.import_module(
        "examples.reference_integrations.genome_web_tf.config"
    )


class GitRunner:
    def __init__(self, revision=AUDITED):
        self.revision = revision
        self.calls = []

    def __call__(self, argv, **kwargs):
        self.calls.append((tuple(str(value) for value in argv), kwargs))
        return SimpleNamespace(
            returncode=0,
            stdout=self.revision + "\n",
            stderr="",
        )


def make_config(tmp_path, *, revision=AUDITED, existing=False):
    cfg = config_module()
    existing_identities = None
    if existing:
        existing_identities = tmp_path / "identities.tsv"
        existing_identities.write_text("entity\tid\tuid\n", encoding="utf-8")
    return cfg.GenomeWebTFReferenceConfig(
        repo_root=tmp_path / "genome-web",
        provider_revision=revision,
        input_manifest=tmp_path / "genomes.tsv",
        planning_root=tmp_path / "planning",
        control_root=tmp_path / "control",
        run_root=tmp_path / "runs",
        existing_identities=existing_identities,
    )


def make_execution(tmp_path, *, manifest_paths=None):
    manifest = tmp_path / "planning" / "task-1" / "genomes.resolved.tsv"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("resolved\n", encoding="utf-8")
    paths = manifest_paths or (manifest, manifest)
    return ExecutionDescriptor(
        run_spec_id=uuid4(),
        run_spec_hash="a" * 64,
        analysis_hash="b" * 64,
        attempt_id=uuid4(),
        attempt_number=1,
        submission_key="submission-1",
        provider_attempt_name="bh-test-1",
        workflow_identity={"provider": "genome-web", "revision": AUDITED},
        resolved_inputs=tuple(
            {
                "id": str(uuid4()),
                "provider": "genome-web",
                "provider_revision": AUDITED,
                "metadata": {"resolved_manifest_path": str(path)},
            }
            for path in paths
        ),
        result_affecting_parameters={
            "min_seqs": 4,
            "model": "LG",
            "bootstrap": 0,
            "alrt": 0,
            "seed": 12345,
        },
        environment_contract={"nextflow": "25.10.4"},
        reproducibility_contract={"class": "DETERMINISTIC"},
        planned_resource_controls={
            "mafft_threads": 2,
            "iqtree_threads": 3,
        },
        expected_outputs=("candidate_manifest",),
        validation_profile_id="candidate",
        validation_profile_revision="1",
    )


def test_capabilities_are_revision_guarded(tmp_path):
    executor = module()
    cfg = make_config(tmp_path)
    runner = GitRunner()
    adapter = executor.GenomeWebTFExecutorAdapter(cfg, run_command=runner)

    capabilities = adapter.capabilities()

    assert capabilities.model_dump() == {
        "mode": "synchronous_process",
        "native_idempotency_key": False,
        "durable_external_execution_id": False,
        "poll": False,
        "reconcile_after_disconnect": "limited",
        "cancellation": "unsupported",
        "logs": True,
        "trace": True,
    }

    mismatched = executor.GenomeWebTFExecutorAdapter(
        cfg,
        run_command=GitRunner("different"),
    )
    with pytest.raises(config_module().RevisionMismatch):
        mismatched.capabilities()


def test_prepare_composes_only_audited_launcher_command(tmp_path):
    executor = module()
    cfg = make_config(tmp_path, existing=True)
    execution = make_execution(tmp_path)
    adapter = executor.GenomeWebTFExecutorAdapter(
        cfg,
        run_command=GitRunner(),
    )

    invocation = adapter.prepare(execution)

    manifest = execution.resolved_inputs[0]["metadata"]["resolved_manifest_path"]
    assert invocation.argv == (
        str(cfg.launcher),
        str(cfg.run_root),
        manifest,
        execution.provider_attempt_name,
        "--min-seqs",
        "4",
        "--model",
        "LG",
        "--bootstrap",
        "0",
        "--alrt",
        "0",
        "--seed",
        "12345",
        "--mafft-threads",
        "2",
        "--iqtree-threads",
        "3",
        "--existing-identities",
        str(cfg.existing_identities),
    )
    assert all(arg != "nextflow" for arg in invocation.argv)
    assert invocation.stdout_path == (
        cfg.control_root / execution.provider_attempt_name / "stdout.log"
    )
    assert invocation.stderr_path == (
        cfg.control_root / execution.provider_attempt_name / "stderr.log"
    )
    assert not (
        cfg.run_root / "attempts" / execution.provider_attempt_name
    ).exists()


def test_prepare_rejects_inconsistent_resolved_manifest_paths(tmp_path):
    executor = module()
    cfg = make_config(tmp_path)
    one = tmp_path / "one.tsv"
    two = tmp_path / "two.tsv"
    execution = make_execution(tmp_path, manifest_paths=(one, two))
    adapter = executor.GenomeWebTFExecutorAdapter(
        cfg,
        run_command=GitRunner(),
    )

    with pytest.raises(ValueError, match="exactly one resolved manifest"):
        adapter.prepare(execution)


def test_bindingless_inspect_uses_only_observed_attempt_evidence(tmp_path):
    executor = module()
    cfg = make_config(tmp_path)
    attempt_name = "bh-test-1"
    provider_attempt = cfg.run_root / "attempts" / attempt_name
    candidate = provider_attempt / "output" / "candidate"
    candidate.mkdir(parents=True)
    (candidate / "manifest.json").write_text(
        json.dumps(
            {
                "status": "validated_candidate",
                "production_publication": "NOT_AUTHORIZED",
                "genomes": [{"uid": "00902"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (provider_attempt / "invocation.json").write_text("{}\n", encoding="utf-8")

    adapter = executor.GenomeWebTFExecutorAdapter(
        cfg,
        run_command=GitRunner(),
    )
    evidence = adapter.inspect(
        None,
        {"provider_attempt_name": attempt_name},
    )

    assert evidence.active is None
    assert evidence.terminal_outcome == "succeeded"
    assert evidence.exit_code == 0
    roles = {item["role"] for item in evidence.evidence}
    assert roles == {"provider_invocation", "candidate_manifest"}

    empty = adapter.inspect(
        None,
        {"provider_attempt_name": "missing-attempt"},
    )
    assert empty.active is None
    assert empty.terminal_outcome is None
    assert empty.exit_code is None
    assert empty.evidence == ()


def test_invalid_candidate_manifest_is_not_treated_as_success(tmp_path):
    executor = module()
    cfg = make_config(tmp_path)
    attempt_name = "bh-invalid"
    candidate = (
        cfg.run_root
        / "attempts"
        / attempt_name
        / "output"
        / "candidate"
    )
    candidate.mkdir(parents=True)
    (candidate / "manifest.json").write_text(
        json.dumps(
            {
                "status": "validated_candidate",
                "production_publication": "AUTHORIZED",
            }
        ),
        encoding="utf-8",
    )
    adapter = executor.GenomeWebTFExecutorAdapter(
        cfg,
        run_command=GitRunner(),
    )

    evidence = adapter.inspect(
        None,
        {"provider_attempt_name": attempt_name},
    )

    assert evidence.terminal_outcome is None
    assert evidence.exit_code is None
    assert {item["role"] for item in evidence.evidence} == {"candidate_manifest"}


def test_discover_artifacts_returns_only_existing_provider_outputs(tmp_path):
    executor = module()
    cfg = make_config(tmp_path)
    attempt_name = "bh-artifacts"
    provider_attempt = cfg.run_root / "attempts" / attempt_name
    candidate = provider_attempt / "output" / "candidate"

    files = {
        provider_attempt / "genomes.resolved.tsv": "resolved\n",
        provider_attempt / "invocation.json": "{}\n",
        provider_attempt / "nextflow.log": "log\n",
        provider_attempt / "trace.tsv": "trace\n",
        candidate / "manifest.json": "{}\n",
        candidate / "trees" / "00902" / "tree" / "FamilyA_tree.treefile": "(A,B);\n",
        candidate / "analysis" / "Beta" / "tf_tree_catalog" / "test1" / "audit.tsv": "audit\n",
    }
    for path, value in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")

    adapter = executor.GenomeWebTFExecutorAdapter(
        cfg,
        run_command=GitRunner(),
    )
    artifacts = adapter.discover_artifacts(
        {"provider_attempt_name": attempt_name}
    )

    roles = [item["role"] for item in artifacts]
    assert "resolved_manifest" in roles
    assert "provider_invocation" in roles
    assert "execution_log" in roles
    assert "execution_trace" in roles
    assert "candidate_manifest" in roles
    assert "tree" in roles
    assert "audit_table" in roles
    assert "alignment" not in roles
    assert all(Path(item["path"]).is_file() for item in artifacts)
