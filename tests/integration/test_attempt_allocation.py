from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from bioharness.adapters.postgres.session import PostgresUnitOfWork
from tests.fakes.factories import make_run_spec
from tests.fakes.providers import FakePolicyEvaluator, FakeWorkflowExecutor

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


def test_concurrent_attempt_allocation_is_serialized(migrated_database):
    spec = make_run_spec()
    with PostgresUnitOfWork(migrated_database) as uow:
        uow.planning.add_run_spec(spec)
        uow.commit()

    def allocate(_):
        decision = FakePolicyEvaluator().evaluate("alice", "launch", f"runspec:{spec.id}", {})
        with PostgresUnitOfWork(migrated_database) as uow:
            attempt = uow.runs.allocate_attempt_intent(
                run_spec_id=spec.id,
                decision=decision,
                capability_snapshot=FakeWorkflowExecutor().capabilities().model_dump(mode="json"),
                executor_namespace="fake-local",
                now=NOW,
            )
            uow.commit()
            return attempt.attempt_number

    with ThreadPoolExecutor(max_workers=2) as pool:
        numbers = set(pool.map(allocate, range(2)))
    assert numbers == {1, 2}
