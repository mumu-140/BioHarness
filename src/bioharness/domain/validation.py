from datetime import datetime
from enum import StrEnum
from uuid import UUID

from bioharness.domain.base import FrozenRecord


class ValidationOutcome(StrEnum):
    PASS = "PASS"
    PASS_WITH_LIMITATIONS = "PASS_WITH_LIMITATIONS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


class ValidationReport(FrozenRecord):
    id: UUID
    kind: str
    subject_type: str
    subject_id: str
    validator: str
    validator_revision: str
    outcome: ValidationOutcome
    limitations: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    created_at: datetime


class ValidationRequirement(FrozenRecord):
    kind: str
    allowed_outcomes: tuple[ValidationOutcome, ...]


class ValidationProfile(FrozenRecord):
    profile_id: str
    revision: str
    requirements: tuple[ValidationRequirement, ...]


class ValidationEvaluation(FrozenRecord):
    id: UUID
    profile_id: str
    profile_revision: str
    report_ids: tuple[UUID, ...]
    outcome: ValidationOutcome
    evaluated_at: datetime
