from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import pytest

from bioharness.adapters.postgres.session import PostgresUnitOfWork
from bioharness.domain.run import RunAttemptState, RunEventType
from tests.fakes.factories import make_run_spec
from tests.fakes.providers import FakePolicyEvaluator, FakeWorkflowExecutor

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


def _allocate(uow, spec, *, preflight_evidence):
    decision = FakePolicyEvaluator().evaluate("alice", "launch", f"runspec:{spec.id}", {})
    return uow.runs.allocate_attempt_intent(
        run_spec_id=spec.id,
        decision=decision,
        capability_snapshot=FakeWorkflowExecutor().capabilities().model_dump(mode="json"),
        executor_namespace="fake-local",
        preflight_evidence=preflight_evidence,
        now=NOW,
    )


def test_concurrent_attempt_allocation_allows_only_one_active_intent(migrated_database):
    spec = make_run_spec()
    with PostgresUnitOfWork(migrated_database) as uow:
        uow.planning.add_run_spec(spec)
        uow.commit()

    def allocate(_):
        try:
            with PostgresUnitOfWork(migrated_database) as uow:
                attempt = _allocate(uow, spec, preflight_evidence={"checked": True})
                uow.commit()
                return ("allocated", attempt.attempt_number)
        except RuntimeError:
            return ("blocked", None)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(allocate, range(2)))

    assert sorted(result[0] for result in results) == ["allocated", "blocked"]
    assert [result[1] for result in results if result[0] == "allocated"] == [1]


def test_submission_intent_persists_preflight_evidence(migrated_database):
    spec = make_run_spec()
    evidence = {
        "run_spec_hash": spec.run_spec_hash,
        "inputs": [{"sha256": "a" * 64}],
        "environment": {"python": "3.12"},
    }
    with PostgresUnitOfWork(migrated_database) as uow:
        uow.planning.add_run_spec(spec)
        uow.commit()

    with PostgresUnitOfWork(migrated_database) as uow:
        attempt = _allocate(uow, spec, preflight_evidence=evidence)
        uow.commit()

    with PostgresUnitOfWork(migrated_database) as uow:
        events = uow.runs.list_events(attempt.id)

    intent = next(event for event in events if event.event_type is RunEventType.SUBMISSION_INTENT_RECORDED)
    assert intent.payload["preflight_evidence"] == evidence


@pytest.mark.parametrize(
    "blocking_state",
    [
        RunAttemptState.SUBMITTING,
        RunAttemptState.RUNNING,
        RunAttemptState.COLLECTING,
        RunAttemptState.UNKNOWN,
        RunAttemptState.NEEDS_OPERATOR_RECONCILIATION,
    ],
)
def test_nonterminal_or_unresolved_attempt_blocks_new_allocation(
    migrated_database, blocking_state
):
    spec = make_run_spec()
    with PostgresUnitOfWork(migrated_database) as uow:
        uow.planning.add_run_spec(spec)
        uow.commit()

    with PostgresUnitOfWork(migrated_database) as uow:
        first = _allocate(uow, spec, preflight_evidence={"checked": True})
        uow.commit()

    if blocking_state is not RunAttemptState.SUBMITTING:
        with PostgresUnitOfWork(migrated_database) as uow:
            if blocking_state in {
                RunAttemptState.RUNNING,
                RunAttemptState.COLLECTING,
                RunAttemptState.NEEDS_OPERATOR_RECONCILIATION,
            }:
                current = uow.runs.transition(
                    first.id,
                    RunAttemptState.RUNNING,
                    RunEventType.EXECUTION_STARTED,
                    {"test": True},
                    NOW,
                )
                if blocking_state is RunAttemptState.COLLECTING:
                    uow.runs.transition(
                        current.id,
                        RunAttemptState.COLLECTING,
                        RunEventType.RECONCILIATION_RESOLVED,
                        {"test": True},
                        NOW,
                    )
                elif blocking_state is RunAttemptState.NEEDS_OPERATOR_RECONCILIATION:
                    unknown = uow.runs.transition(
                        current.id,
                        RunAttemptState.UNKNOWN,
                        RunEventType.EXECUTION_OUTCOME_UNKNOWN,
                        {"test": True},
                        NOW,
                    )
                    uow.runs.transition(
                        unknown.id,
                        RunAttemptState.NEEDS_OPERATOR_RECONCILIATION,
                        RunEventType.RECONCILIATION_REQUIRED,
                        {"test": True},
                        NOW,
                    )
            elif blocking_state is RunAttemptState.UNKNOWN:
                uow.runs.transition(
                    first.id,
                    RunAttemptState.UNKNOWN,
                    RunEventType.EXECUTION_OUTCOME_UNKNOWN,
                    {"test": True},
                    NOW,
                )
            uow.commit()

    with pytest.raises(RuntimeError, match="prior attempt"):
        with PostgresUnitOfWork(migrated_database) as uow:
            _allocate(uow, spec, preflight_evidence={"checked": True})
            uow.commit()


@pytest.mark.parametrize("terminal_state", [RunAttemptState.FINISHED, RunAttemptState.FAILED])
def test_terminal_attempt_allows_later_allocation(migrated_database, terminal_state):
    spec = make_run_spec()
    with PostgresUnitOfWork(migrated_database) as uow:
        uow.planning.add_run_spec(spec)
        uow.commit()

    with PostgresUnitOfWork(migrated_database) as uow:
        first = _allocate(uow, spec, preflight_evidence={"checked": True})
        uow.commit()

    with PostgresUnitOfWork(migrated_database) as uow:
        if terminal_state is RunAttemptState.FAILED:
            uow.runs.transition(
                first.id,
                RunAttemptState.FAILED,
                RunEventType.EXECUTION_EXITED,
                {"test": True},
                NOW,
            )
        else:
            running = uow.runs.transition(
                first.id,
                RunAttemptState.RUNNING,
                RunEventType.EXECUTION_STARTED,
                {"test": True},
                NOW,
            )
            collecting = uow.runs.transition(
                running.id,
                RunAttemptState.COLLECTING,
                RunEventType.RECONCILIATION_RESOLVED,
                {"test": True},
                NOW,
            )
            uow.runs.transition(
                collecting.id,
                RunAttemptState.FINISHED,
                RunEventType.COLLECTION_FINISHED,
                {"test": True},
                NOW,
            )
        uow.commit()

    with PostgresUnitOfWork(migrated_database) as uow:
        second = _allocate(uow, spec, preflight_evidence={"checked": True})
        uow.commit()

    assert second.attempt_number == 2
