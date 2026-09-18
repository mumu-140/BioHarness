import importlib

import pytest


AUDITED = "05072cbbcd533ca59afa13996d8d0edd8f939c6e"


def config_module():
    return importlib.import_module(
        "examples.reference_integrations.genome_web_tf.config"
    )


def config(tmp_path, revision=AUDITED):
    module = config_module()
    return module.GenomeWebTFReferenceConfig(
        repo_root=tmp_path,
        provider_revision=revision,
        input_manifest=tmp_path / "genomes.tsv",
        planning_root=tmp_path / "planning",
        control_root=tmp_path / "control",
        run_root=tmp_path / "runs",
    )


def test_audited_revision_is_fixed():
    assert config_module().AUDITED_REVISION == AUDITED


def test_configured_revision_mismatch_is_rejected(tmp_path):
    module = config_module()
    with pytest.raises(module.RevisionMismatch):
        config(tmp_path, revision="different").require_audited_revision(
            observed_revision=AUDITED
        )


def test_observed_checkout_revision_mismatch_is_rejected(tmp_path):
    module = config_module()
    with pytest.raises(module.RevisionMismatch):
        config(tmp_path).require_audited_revision(observed_revision="different")


def test_observe_repo_revision_uses_injected_command_runner(tmp_path):
    module = config_module()
    calls = []

    class Result:
        stdout = AUDITED + "\n"

    def run_command(argv, **kwargs):
        calls.append((argv, kwargs))
        return Result()

    observed = module.observe_repo_revision(tmp_path, run_command=run_command)

    assert observed == AUDITED
    assert calls == [
        (
            ("git", "-C", str(tmp_path), "rev-parse", "HEAD"),
            {"check": True, "text": True, "capture_output": True},
        )
    ]
