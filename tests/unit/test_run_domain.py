from datetime import datetime, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from bioharness.domain.memory import MemoryCandidate
from bioharness.domain.run import RunAttemptState, allowed_transition
from bioharness.domain.validation import ValidationOutcome, ValidationReport

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


def test_finished_is_execution_not_validation_state():
    assert allowed_transition(RunAttemptState.COLLECTING, RunAttemptState.FINISHED)


def test_unknown_cannot_be_resubmitted_in_place():
    assert not allowed_transition(RunAttemptState.UNKNOWN, RunAttemptState.SUBMITTING)


def test_memory_candidate_requires_evidence():
    with pytest.raises(ValidationError):
        MemoryCandidate(
            id=UUID("00000000-0000-0000-0000-000000000201"),
            scope="project:p1",
            kind="procedure",
            statement="Use explicit run identity",
            tags=("execution",),
            applicability={},
            evidence_refs=(),
            status="candidate",
            created_at=NOW,
        )


def test_validation_report_has_one_typed_kind():
    report = ValidationReport(
        id=UUID("00000000-0000-0000-0000-000000000202"),
        kind="provider_contract",
        subject_type="run_attempt",
        subject_id="ra-1",
        validator="fake-validator",
        validator_revision="1",
        outcome=ValidationOutcome.PASS,
        limitations=(),
        evidence_refs=("event:1",),
        created_at=NOW,
    )
    assert report.kind == "provider_contract"
