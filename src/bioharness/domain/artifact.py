from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from bioharness.domain.base import FrozenRecord


class Artifact(FrozenRecord):
    id: UUID
    run_spec_id: UUID
    run_attempt_id: UUID
    role: str
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    size_bytes: int = Field(ge=0)
    uri: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    registered_at: datetime
