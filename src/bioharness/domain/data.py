from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from .base import FrozenRecord


class ResolvedDataRef(FrozenRecord):
    id: UUID
    provider: str
    provider_revision: str
    resource_type: str
    logical_uri: str
    content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    manifest_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    member_manifest_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    biological_identity: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    resolved_at: datetime
