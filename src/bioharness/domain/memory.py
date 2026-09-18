from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from bioharness.domain.base import FrozenRecord


class MemoryCandidate(FrozenRecord):
    id: UUID
    scope: str
    kind: str
    statement: str
    tags: tuple[str, ...] = ()
    applicability: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: tuple[str, ...] = Field(min_length=1)
    status: str
    created_at: datetime
