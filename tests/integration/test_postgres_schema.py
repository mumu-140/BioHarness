from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from bioharness.adapters.postgres.session import PostgresUnitOfWork
from bioharness.domain.run import RunAttempt, RunAttemptState
from tests.fakes.factories import NOW, make_run_spec


def test_run_spec_hash_is_unique(migrated_database):
    first = make_run_spec()
    second = first.model_copy(update={"id": uuid4()})
    with PostgresUnitOfWork(migrated_database) as uow:
        uow.planning.add_run_spec(first)
        uow.commit()
    with pytest.raises(IntegrityError):
        with PostgresUnitOfWork(migrated_database) as uow:
            uow.planning.add_run_spec(second)
            uow.commit()


def test_submission_key_is_unique(migrated_database):
    spec = make_run_spec()
    with PostgresUnitOfWork(migrated_database) as uow:
        uow.planning.add_run_spec(spec)
        uow.commit()
    a1 = RunAttempt(
        id=uuid4(), run_spec_id=spec.id, attempt_number=1,
        executor_namespace="local", capability_snapshot={}, submission_key="same-key",
        provider_attempt_name="attempt-1", state=RunAttemptState.SUBMITTING,
        submitted_at=NOW,
    )
    a2 = a1.model_copy(update={"id": uuid4(), "attempt_number": 2, "provider_attempt_name": "attempt-2"})
    with PostgresUnitOfWork(migrated_database) as uow:
        uow.runs.add_attempt(a1)
        uow.commit()
    with pytest.raises(IntegrityError):
        with PostgresUnitOfWork(migrated_database) as uow:
            uow.runs.add_attempt(a2)
            uow.commit()
