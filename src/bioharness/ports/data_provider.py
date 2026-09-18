from typing import Any, Protocol

from pydantic import Field

from bioharness.domain.base import FrozenRecord


class ProviderResource(FrozenRecord):
    logical_uri: str
    resource_type: str
    biological_identity: dict[str, Any]
    content_identity: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderResolution(FrozenRecord):
    provider: str
    provider_revision: str
    resources: tuple[ProviderResource, ...]
    evidence: tuple[dict[str, Any], ...] = ()


class DataProvider(Protocol):
    def resolve(
        self, logical_resources: tuple[str, ...], context: dict[str, Any]
    ) -> ProviderResolution: ...
