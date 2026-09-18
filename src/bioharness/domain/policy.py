from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field

from .base import FrozenRecord


class PolicyOutcome(StrEnum):
    ALLOW = "ALLOW"
    ALLOW_WITH_WARNING = "ALLOW_WITH_WARNING"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"


class PolicyRequest(FrozenRecord):
    actor: str
    action: str
    resource: str
    context: dict[str, Any] = Field(default_factory=dict)


class PolicyDecision(FrozenRecord):
    id: UUID
    actor: str
    action: str
    resource: str
    policy_revision: str
    outcome: PolicyOutcome
    warnings: tuple[str, ...] = ()
    obligations: tuple[str, ...] = ()
    decided_at: datetime
