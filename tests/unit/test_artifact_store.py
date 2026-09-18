import pytest

from bioharness.adapters.filesystem.artifacts import ArtifactPathOutsideAllowedRoots, inspect_artifact


def test_inspect_artifact_hashes_bytes(tmp_path):
    p = tmp_path / "result.txt"
    p.write_text("abc", encoding="utf-8")
    record = inspect_artifact(p, role="result")
    assert record.content_sha256 == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert record.size_bytes == 3
    assert record.role == "result"


def test_inspect_artifact_rejects_path_outside_allowed_roots(tmp_path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("x", encoding="utf-8")
    with pytest.raises(ArtifactPathOutsideAllowedRoots):
        inspect_artifact(outside, role="result", allowed_roots=(allowed,))
