import csv
import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest


AUDITED = "05072cbbcd533ca59afa13996d8d0edd8f939c6e"
PATH_ROLES = (
    "gene_tsv",
    "transcript_tsv",
    "protein_tsv",
    "protein_fasta",
    "tf_tsv",
    "tf_gene_tsv",
)
COLUMNS = (
    "species_id",
    "uid",
    "genome_build",
    "annotation_release",
    "release_id",
    *PATH_ROLES,
)


def module():
    return importlib.import_module(
        "examples.reference_integrations.genome_web_tf.data_adapter"
    )


def config_module():
    return importlib.import_module(
        "examples.reference_integrations.genome_web_tf.config"
    )


def write_manifest(tmp_path: Path) -> Path:
    rows = []
    for species, uid in (("Alpha", "90001"), ("Beta", "00902")):
        member_dir = tmp_path / species
        member_dir.mkdir()
        paths = {}
        for role in PATH_ROLES:
            suffix = ".fa" if role == "protein_fasta" else ".tsv"
            path = member_dir / f"{role}{suffix}"
            path.write_text(f"{species}-{uid}-{role}\n", encoding="utf-8")
            paths[role] = f"{species}/{path.name}"
        rows.append(
            {
                "species_id": species,
                "uid": uid,
                "genome_build": f"{species}_assembly",
                "annotation_release": "annotation1",
                "release_id": "test1",
                **paths,
            }
        )

    manifest = tmp_path / "genomes.tsv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=COLUMNS,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    return manifest


def make_config(tmp_path: Path):
    cfg = config_module()
    manifest = write_manifest(tmp_path)
    return cfg.GenomeWebTFReferenceConfig(
        repo_root=tmp_path / "genome-web",
        provider_revision=AUDITED,
        input_manifest=manifest,
        planning_root=tmp_path / "planning",
        control_root=tmp_path / "control",
        run_root=tmp_path / "runs",
    )


class ResolverRunner:
    def __init__(self, *, resolver_returncode=0, resolver_stderr=""):
        self.calls = []
        self.resolver_returncode = resolver_returncode
        self.resolver_stderr = resolver_stderr

    def __call__(self, argv, **kwargs):
        argv = tuple(str(value) for value in argv)
        self.calls.append((argv, kwargs))
        if argv[0] == "git":
            return SimpleNamespace(returncode=0, stdout=AUDITED + "\n", stderr="")

        if self.resolver_returncode:
            return SimpleNamespace(
                returncode=self.resolver_returncode,
                stdout="",
                stderr=self.resolver_stderr,
            )

        source = Path(argv[argv.index("--genomes") + 1])
        output = Path(argv[argv.index("--output") + 1])
        output.parent.mkdir(parents=True, exist_ok=True)
        with source.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        for row in rows:
            for role in PATH_ROLES:
                path = Path(row[role])
                if not path.is_absolute():
                    path = source.parent / path
                row[role] = str(path.resolve())
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=COLUMNS,
                delimiter="\t",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(sorted(rows, key=lambda row: row["uid"]))
        return SimpleNamespace(returncode=0, stdout="PASS genomes=2\n", stderr="")


def resources():
    return (
        "genomeweb:registered-genome:Alpha:90001",
        "genomeweb:registered-genome:Beta:00902",
    )


def test_external_resolver_command_and_exact_member_identity(tmp_path):
    data = module()
    cfg = make_config(tmp_path)
    runner = ResolverRunner()
    adapter = data.GenomeWebTFDataAdapter(cfg, run_command=runner)

    resolution = adapter.resolve(
        resources(),
        {"task_id": "task-123", "task_revision": 4},
    )

    resolver_calls = [call for call in runner.calls if call[0][0] != "git"]
    assert len(resolver_calls) == 1
    argv, kwargs = resolver_calls[0]
    assert argv[:2] == (str(data.sys.executable), str(cfg.validate_script))
    assert argv[2:] == (
        "--genomes",
        str(cfg.input_manifest),
        "--output",
        str(cfg.planning_root / "task-123" / "genomes.resolved.tsv"),
    )
    assert kwargs == {"check": False, "text": True, "capture_output": True}

    by_uri = {resource.logical_uri: resource for resource in resolution.resources}
    beta = by_uri["genomeweb:registered-genome:Beta:00902"]
    assert beta.biological_identity["uid"] == "00902"
    assert beta.biological_identity["species_id"] == "Beta"
    assert len(beta.content_identity["manifest_sha256"]) == 64
    assert len(beta.content_identity["member_manifest_sha256"]) == 64
    assert beta.metadata["resolved_manifest_path"] == str(
        cfg.planning_root / "task-123" / "genomes.resolved.tsv"
    )
    assert {item["role"] for item in beta.metadata["members"]} == set(PATH_ROLES)
    assert all(len(item["sha256"]) == 64 for item in beta.metadata["members"])


def test_requested_scope_must_exactly_match_configured_manifest(tmp_path):
    data = module()
    cfg = make_config(tmp_path)

    for requested in (
        (resources()[0],),
        resources() + ("genomeweb:registered-genome:Gamma:12345",),
    ):
        runner = ResolverRunner()
        adapter = data.GenomeWebTFDataAdapter(cfg, run_command=runner)
        with pytest.raises(ValueError, match="exactly match"):
            adapter.resolve(requested, {"task_id": "task-scope", "task_revision": 1})
        assert not [call for call in runner.calls if call[0][0] != "git"]


def test_changed_member_changes_member_manifest_digest(tmp_path):
    data = module()
    cfg = make_config(tmp_path)
    runner = ResolverRunner()
    adapter = data.GenomeWebTFDataAdapter(cfg, run_command=runner)

    first = adapter.resolve(resources(), {"task_id": "task-a", "task_revision": 1})
    first_beta = next(
        item for item in first.resources if item.biological_identity["uid"] == "00902"
    )

    member = tmp_path / "Beta" / "protein_fasta.fa"
    member.write_text(member.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")

    second = adapter.resolve(resources(), {"task_id": "task-b", "task_revision": 1})
    second_beta = next(
        item for item in second.resources if item.biological_identity["uid"] == "00902"
    )

    assert (
        first_beta.content_identity["member_manifest_sha256"]
        != second_beta.content_identity["member_manifest_sha256"]
    )


def test_provider_failure_preserves_exit_code_and_stderr_without_retry(tmp_path):
    data = module()
    cfg = make_config(tmp_path)
    runner = ResolverRunner(
        resolver_returncode=7,
        resolver_stderr="cross-uid ID collision",
    )
    adapter = data.GenomeWebTFDataAdapter(cfg, run_command=runner)

    with pytest.raises(data.ProviderResolutionError) as caught:
        adapter.resolve(resources(), {"task_id": "task-fail", "task_revision": 1})

    assert caught.value.returncode == 7
    assert "cross-uid ID collision" in caught.value.stderr
    assert len([call for call in runner.calls if call[0][0] != "git"]) == 1
