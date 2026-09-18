from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from .base import FrozenRecord


class AssessmentStatus(StrEnum):
    ANALYSIS_SUPPORTED = "ANALYSIS_SUPPORTED"
    ANALYSIS_SUPPORTED_WITH_LIMITATIONS = "ANALYSIS_SUPPORTED_WITH_LIMITATIONS"
    UNRESOLVED = "UNRESOLVED"
    NOT_IDENTIFIABLE = "NOT_IDENTIFIABLE"
    INCOMPATIBLE = "INCOMPATIBLE"


class ScientificAssessment(FrozenRecord):
    id: UUID
    task_spec_id: UUID
    task_spec_revision: int = Field(ge=1)
    resolved_data_ref_ids: tuple[UUID, ...]
    scientific_contract_id: str
    scientific_contract_revision: str
    dependency_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    status: AssessmentStatus
    limitations: tuple[str, ...] = ()
    assessed_at: datetime
