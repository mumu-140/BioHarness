from bioharness import __version__
from bioharness.settings import Settings


def test_package_import_and_settings(tmp_path):
    settings = Settings(
        database_url="postgresql+psycopg://bioharness:bioharness@localhost/bioharness_test",
        run_root=tmp_path / "runs",
        artifact_root=tmp_path / "artifacts",
        protected_roots=(tmp_path / "production",),
    )
    assert __version__ == "0.1.0"
    assert settings.run_root.name == "runs"
