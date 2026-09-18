import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest


AUDITED = "05072cbbcd533ca59afa13996d8d0edd8f939c6e"


def module():
    return importlib.import_module(
        "examples.reference_integrations.genome_web_tf.acceptance"
    )


def preflight_module():
    return importlib.import_module(
        "examples.reference_integrations.genome_web_tf.preflight"
    )


def write_manifest(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "species_id\tuid\nAlpha\t90001\nBeta\t00902\n",
        encoding="utf-8",
    )


def write_config(tmp_path: Path) -> Path:
    config = tmp_path / "acceptance.toml"
    config.write_text(
        f'''
provider_repo = "{tmp_path / "genome-web"}"
provider_revision = "{AUDITED}"
input_manifest = "{tmp_path / "fixtures" / "genomes.tsv"}"
planning_root = "{tmp_path / "planning"}"
control_root = "{tmp_path / "control"}"
run_root = "{tmp_path / "runs"}"
artifact_root = "{tmp_path / "artifacts"}"
database_url_env = "BIOHARNESS_DATABASE_URL"
production_roots = ["{tmp_path / "production"}"]
read_only_source_roots = ["{tmp_path / "source"}"]
'''.lstrip(),
        encoding="utf-8",
    )
    write_manifest(tmp_path / "fixtures" / "genomes.tsv")
    return config


def test_acceptance_config_loads_isolated_paths(tmp_path):
    acceptance = module()
    config = acceptance.load_config(write_config(tmp_path))

    assert config.provider_revision == AUDITED
    assert config.artifact_root == tmp_path / "artifacts"
    assert config.database_url_env == "BIOHARNESS_DATABASE_URL"
    assert config.production_roots == (tmp_path / "production",)
    assert config.read_only_source_roots == (tmp_path / "source",)
    preflight_module().validate_path_isolation(config)


def test_path_isolation_rejects_protected_and_provider_attempt_overlap(tmp_path):
    acceptance = module()
    preflight = preflight_module()
    config = acceptance.load_config(write_config(tmp_path))

    protected_overlap = config.model_copy(
        update={"planning_root": config.read_only_source_roots[0] / "planning"}
    )
    with pytest.raises(ValueError, match="protected"):
        preflight.validate_path_isolation(protected_overlap)

    attempt_overlap = config.model_copy(
        update={"control_root": config.run_root / "attempts" / "control"}
    )
    with pytest.raises(ValueError, match="attempt"):
        preflight.validate_path_isolation(attempt_overlap)

    unsafe_root = config.model_copy(update={"artifact_root": Path("/")})
    with pytest.raises(ValueError, match="unsafe"):
        preflight.validate_path_isolation(unsafe_root)


def test_path_isolation_resolves_symlinks_before_comparison(tmp_path):
    acceptance = module()
    preflight = preflight_module()
    config = acceptance.load_config(write_config(tmp_path))
    protected = config.read_only_source_roots[0]
    protected.mkdir(parents=True)
    alias = tmp_path / "source-alias"
    alias.symlink_to(protected, target_is_directory=True)
    linked = config.model_copy(update={"planning_root": alias / "planning"})

    with pytest.raises(ValueError, match="protected"):
        preflight.validate_path_isolation(linked)


class GitRunner:
    def __init__(self):
        self.calls = []

    def __call__(self, argv, **kwargs):
        argv = tuple(str(value) for value in argv)
        self.calls.append((argv, kwargs))
        return SimpleNamespace(returncode=0, stdout=AUDITED + "\n", stderr="")


def test_dry_run_builds_preview_without_resolver_or_launcher_side_effect(tmp_path):
    acceptance = module()
    config_path = write_config(tmp_path)
    config = acceptance.load_config(config_path)
    runner = GitRunner()

    report = acceptance.build_dry_run_report(
        config,
        run_command=runner,
    )

    assert report["provider_revision"] == AUDITED
    assert report["logical_resources"] == [
        "genomeweb:registered-genome:Alpha:90001",
        "genomeweb:registered-genome:Beta:00902",
    ]
    assert report["planned_command"][0] == str(config.launcher)
    assert report["policy_outcomes"] == {
        "read_resolve": "ALLOW",
        "launch": "ALLOW",
        "production_publication": "DENY",
        "canonical_mutation": "DENY",
    }
    assert all(call[0][0] == "git" for call in runner.calls)
