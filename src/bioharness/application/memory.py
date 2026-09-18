from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from bioharness.domain.memory import MemoryCandidate


class MemoryService:
    def __init__(self, *, uow_factory, clock: Callable[[], datetime] | None = None):
        self.uow_factory = uow_factory
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def record(
        self,
        *,
        scope: str,
        kind: str,
        statement: str,
        tags: tuple[str, ...] = (),
        applicability: dict[str, Any] | None = None,
        evidence_refs: tuple[str, ...],
        status: str = "candidate",
    ) -> MemoryCandidate:
        candidate = MemoryCandidate(
            id=uuid4(),
            scope=scope,
            kind=kind,
            statement=statement,
            tags=tags,
            applicability=applicability or {},
            evidence_refs=evidence_refs,
            status=status,
            created_at=self.clock(),
        )
        with self.uow_factory() as uow:
            uow.memory.add(candidate)
            uow.commit()
        return candidate

    def search(
        self,
        *,
        scope: str,
        tags: tuple[str, ...] = (),
        text: str | None = None,
        applicability: dict[str, Any] | None = None,
    ) -> tuple[MemoryCandidate, ...]:
        with self.uow_factory() as uow:
            candidates = uow.memory.list_scope(scope)
        required_tags = set(tags)
        required_applicability = applicability or {}
        needle = text.casefold() if text else None
        matched = [
            candidate
            for candidate in candidates
            if required_tags.issubset(candidate.tags)
            and all(candidate.applicability.get(key) == value for key, value in required_applicability.items())
            and (needle is None or needle in candidate.statement.casefold())
        ]
        return tuple(sorted(matched, key=lambda item: (item.created_at, str(item.id))))
