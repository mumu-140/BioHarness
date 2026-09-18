import os
import subprocess

import pytest


@pytest.fixture(scope="session")
def database_url() -> str:
    return os.environ["BIOHARNESS_TEST_DATABASE_URL"]


@pytest.fixture
def migrated_database(database_url: str):
    subprocess.run(["alembic", "downgrade", "base"], check=True)
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    yield database_url
