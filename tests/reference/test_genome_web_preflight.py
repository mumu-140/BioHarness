import hashlib
import importlib
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from bioharness.application.execute_run import PreflightFailed
from bioharness.domain.data import ResolvedDataRef
from bioharness.domain.run import ResolvedConfiguration
from tests.fakes.factories import make_run_spec


AUDITED = "05072cbbcd533ca59afa13996d8d0edd8f939c6e"
NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)
ROLES = (
    "gene_tsv",
    "transcript_tsv",
    "protein_tsv",
    "protein_fasta",
    "tf_tsv",
    "tf_gene_tsv",
)


def module():
    return importlib.import_module(
        "examples.reference_integrations.genome_web_tf.preflight"
    )


def config_module():
    return importlib.import_module(
        "examples.reference_integrations.genome_web_tf.config"
    )


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state(tmp_path):
    cfg_type = config_module().GenomeWebTFReferenceConfig
    repo_root = tmp_path / "genome-web"
    repo_root.mkdir()
    launcher = repo_root / "pipeline" / "nextflow" / "run.sh"
    launcher.parent.mkdir(parents=True)
    launcher.write_text("#!/bin/bash\n", encoding="utf-8")

    source_root = tmp_path / "source"
    source_root.mkdir()
    manifest = tmp_path / "planning" / "task" / "genomes.resolved.tsv"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("resolved-manifest\n", encoding="utf-8")

    members = []
    digest_lines = []
    for role in ROLES:
        path = source_root / role
        path.write_text(role + "\n", encoding="utf-8")
        digest = sha(path)
        members.append(
            {
                "role": role,
                "path": str(path),
                "sha256": digest,
                "size_bytes": path.stat().st_size,
            }
        )
        digest_lines.append(f"{role}\t{digest}\n")
    member_manifest_sha = hashlib.sha256(
        "".join(digest_lines).encode("utf-8")
    ).hexdigest()

    ref = ResolvedDataRef(
        id=uuid4(),
        provider="genome-web",
        provider_revision=AUDITED,
        resource_type="registered_genome",
        logical_uri="genomeweb:registered-genome:Beta:00902",
        manifest_sha256=sha(manifest),
        member_manifest_sha256=member_manifest_sha,
        biological_identity={
            "species_id": "Beta",
            "uid": "00902",
            "genome_build": "Beta_assembly",
            "annotation_release": "annotation1",
            "release_id": "test1",
        },
        metadata={
            "resolved_manifest_path": str(manifest),
            "members": members,
        },
        resolved_at=NOW,
    )

    base = make_run_spec()
    configuration = ResolvedConfiguration(
        id=base.configuration_id,
        task_spec_id=base.task_spec_id,
        assessment_id=base.assessment_id,
        provider_workflow_identity={
            "provider": "genome-web",
            "revision": AUDITED,
        },
        result_affecting_parameters={"min_seqs": 4},
        environment_contract={
            "nextflow": "25.10.4",
            "provider_python": "3.10.12",
            "biopython": "1.78",
            "mafft": "7.526",
            "iqtree3": "3.1.2",
        },
        reproducibility_contract={"class": "DETERMINISTIC"},
        validation_profile_id=base.validation_profile_id,
        validation_profile_revision=base.validation_profile_revision,
        created_at=NOW,
    )
    run_spec = base.model_copy(
        update={"resolved_data_ref_ids": (ref.id,)}
    )
    config = cfg_type(
        repo_root=repo_root,
        provider_revision=AUDITED,
        input_manifest=tmp_path / "input.tsv",
        planning_root=tmp_path / "planning",
        control_root=tmp_path / "control",
        run_root=tmp_path / "runs",
        artifact_root=tmp_path / "artifacts",
        production_roots=(tmp_path / "production",),
        read_only_source_roots=(source_root,),
        nextflow_executable=tmp_path / "runtime" / "nextflow",
        provider_python=tmp_path / "runtime" / "python",
        mafft_executable=tmp_path / "runtime" / "mafft",
        iqtree_executable=tmp_path / "runtime" / "iqtree3",
    )
    return config, run_spec, configuration, ref, members


class Planning:
    def __init__(self, run_spec, configuration, ref):
        self.run_spec = run_spec
        self.configuration = configuration
        self.ref = ref

    def get_run_spec(self, value_id, **kwargs):
        return self.run_spec if value_id == self.run_spec.id else None

    def get_configuration(self, value_id):
        return self.configuration if value_id == self.configuration.id else None

    def get_data_ref(self, value_id):
        return self.ref if value_id == self.ref.id else None


class Uow:
    def __init__(self, planning):
        self.planning = planning

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class CommandRunner:
    DEFAULT_VERSIONS = {
        "nextflow": "25.10.4",
        "provider_python": "3.10.12",
        "biopython": "1.78",
        "mafft": "7.526",
        "iqtree3": "3.1.2",
    }

    def __init__(
        self,
        *,
        revision=AUDITED,
        launcher_returncode=0,
        versions=None,
        ps_returncode=0,
    ):
        self.revision = revision
        self.launcher_returncode = launcher_returncode
        self.versions = dict(self.DEFAULT_VERSIONS)
        self.versions.update(versions or {})
        self.ps_returncode = ps_returncode
        self.calls = []

    def __call__(self, argv, **kwargs):
        argv = tuple(str(value) for value in argv)
        self.calls.append((argv, kwargs))
        if argv[0] == "git":
            return SimpleNamespace(
                returncode=0,
                stdout=self.revision + "\n",
                stderr="",
            )
        if argv[0] == "bash":
            return SimpleNamespace(
                returncode=self.launcher_returncode,
                stdout="usage\n" if not self.launcher_returncode else "",
                stderr="launcher unavailable" if self.launcher_returncode else "",
            )
        if argv == ("ps", "--version"):
            return SimpleNamespace(
                returncode=self.ps_returncode,
                stdout="procps-ng 4.0.4\n" if not self.ps_returncode else "",
                stderr="ps unavailable" if self.ps_returncode else "",
            )

        name = Path(argv[0]).name
        if name == "nextflow":
            return SimpleNamespace(
                returncode=0,
                stdout=f"version {self.versions['nextflow']} build 11173\n",
                stderr="",
            )
        if name == "python" and argv[1:] == ("--version",):
            return SimpleNamespace(
                returncode=0,
                stdout=f"Python {self.versions['provider_python']}\n",
                stderr="",
            )
        if name == "python" and argv[1] == "-c":
            return SimpleNamespace(
                returncode=0,
                stdout=self.versions["biopython"] + "\n",
                stderr="",
            )
        if name == "mafft":
            return SimpleNamespace(
                returncode=0,
                stdout="",
                stderr=f"v{self.versions['mafft']} (2024/Apr/26)\n",
            )
        if name == "iqtree3":
            return SimpleNamespace(
                returncode=0,
                stdout=f"IQ-TREE version {self.versions['iqtree3']} for Linux\n",
                stderr="",
            )
        return SimpleNamespace(
            returncode=127,
            stdout="",
            stderr=f"unexpected command: {argv}",
        )


def make_preflight(tmp_path, **runner_kwargs):
    cfg, run_spec, configuration, ref, members = state(tmp_path)
    planning = Planning(run_spec, configuration, ref)
    runner = CommandRunner(**runner_kwargs)
    check = module().GenomeWebTFPreflight(
        cfg,
        uow_factory=lambda: Uow(planning),
        command_runner=runner,
    )
    return check, runner, cfg, run_spec, configuration, ref, members


def test_preflight_rechecks_frozen_identity_and_revision(tmp_path):
    check, runner, cfg, run_spec, _, ref, _ = make_preflight(tmp_path)

    evidence = check(run_spec)

    assert evidence["run_spec_hash"] == run_spec.run_spec_hash
    assert evidence["provider_revision"] == AUDITED
    assert evidence["resolved_inputs"] == [
        {
            "logical_uri": ref.logical_uri,
            "manifest_sha256": ref.manifest_sha256,
            "member_manifest_sha256": ref.member_manifest_sha256,
        }
    ]
    assert evidence["environment"] == {
        "launcher_help": "PASS",
        "nextflow": "25.10.4",
        "provider_python": "3.10.12",
        "biopython": "1.78",
        "mafft": "7.526",
        "iqtree3": "3.1.2",
        "ps": "PASS",
    }
    non_git_commands = [call[0] for call in runner.calls if call[0][0] != "git"]
    assert ("bash", str(cfg.launcher), "--help") in non_git_commands
    assert (str(cfg.nextflow_executable), "-version") in non_git_commands
    assert (str(cfg.provider_python), "--version") in non_git_commands
    assert (
        str(cfg.provider_python),
        "-c",
        "import Bio; print(Bio.__version__)",
    ) in non_git_commands
    assert (str(cfg.mafft_executable), "--version") in non_git_commands
    assert (str(cfg.iqtree_executable), "--version") in non_git_commands
    assert ("ps", "--version") in non_git_commands


def test_preflight_rejects_member_tampering(tmp_path):
    check, _, _, run_spec, _, _, members = make_preflight(tmp_path)
    path = next(
        item["path"] for item in members if item["role"] == "protein_fasta"
    )
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("changed\n")

    with pytest.raises(PreflightFailed, match="member"):
        check(run_spec)


def test_preflight_rejects_resolved_manifest_tampering(tmp_path):
    check, _, _, run_spec, _, ref, _ = make_preflight(tmp_path)
    with open(ref.metadata["resolved_manifest_path"], "a", encoding="utf-8") as handle:
        handle.write("changed\n")

    with pytest.raises(PreflightFailed, match="manifest"):
        check(run_spec)


def test_preflight_rejects_provider_revision_or_environment_drift(tmp_path):
    check, _, _, run_spec, _, _, _ = make_preflight(
        tmp_path,
        revision="different",
    )
    with pytest.raises(PreflightFailed, match="revision"):
        check(run_spec)

    other = tmp_path / "other"
    other.mkdir()
    check, _, _, run_spec, _, _, _ = make_preflight(
        other,
        launcher_returncode=9,
    )
    with pytest.raises(PreflightFailed, match="launcher"):
        check(run_spec)



def test_preflight_rejects_runtime_contract_version_drift(tmp_path):
    check, _, _, run_spec, _, _, _ = make_preflight(
        tmp_path,
        versions={"mafft": "7.525"},
    )

    with pytest.raises(PreflightFailed, match="environment.*mafft"):
        check(run_spec)


def test_preflight_rejects_missing_process_metrics_tool(tmp_path):
    check, _, _, run_spec, _, _, _ = make_preflight(
        tmp_path,
        ps_returncode=127,
    )

    with pytest.raises(PreflightFailed, match="ps"):
        check(run_spec)
