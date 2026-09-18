from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field

from .base import FrozenRecord


class OutputIntent(StrEnum):
    EXPLORATORY = "exploratory"
    CANDIDATE = "candidate"
    OFFICIAL = "official"


class ScientificTaskSpec(FrozenRecord):
    id: UUID
    revision: int = Field(ge=1)
    question: str = Field(min_length=1)
    requested_inference: str = Field(min_length=1)
    analysis_class: str = Field(min_length=1)
    biological_scope: dict[str, Any]
    output_intent: OutputIntent
    unresolved_fields: tuple[str, ...] = ()
    created_at: datetime
