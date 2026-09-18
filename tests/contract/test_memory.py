from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from bioharness.application.memory import MemoryService
from bioharness.domain.memory import MemoryCandidate

NOW = datetime(2026, 9, 18, tzinfo=timezone.utc)


class MemoryRepo:
    def __init__(self): self.values=[]
    def add(self, value): self.values.append(value)
    def list_scope(self, scope): return tuple(v for v in self.values if v.scope == scope)


class Uow:
    def __init__(self, repo): self.memory=repo
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def commit(self): pass
    def rollback(self): pass


def test_memory_record_requires_evidence():
    service=MemoryService(uow_factory=lambda: Uow(MemoryRepo()), clock=lambda: NOW)
    with pytest.raises(ValidationError):
        service.record(
            scope="project:p1", kind="procedure", statement="Use explicit identity",
            tags=("execution",), applicability={"provider":"fake"}, evidence_refs=(),
        )


def test_memory_search_is_scoped_tagged_and_non_authoritative():
    repo=MemoryRepo(); service=MemoryService(uow_factory=lambda: Uow(repo), clock=lambda: NOW)
    kept=service.record(
        scope="project:p1", kind="procedure", statement="Use explicit run identity for retry",
        tags=("execution","retry"), applicability={"provider":"fake","workflow":"wf1"},
        evidence_refs=("validation:v1",),
    )
    service.record(
        scope="project:p1", kind="procedure", statement="Other provider lesson",
        tags=("execution",), applicability={"provider":"other"}, evidence_refs=("event:e2",),
    )
    service.record(
        scope="project:p2", kind="procedure", statement="Use explicit run identity for retry",
        tags=("execution","retry"), applicability={"provider":"fake","workflow":"wf1"},
        evidence_refs=("event:e3",),
    )
    found=service.search(
        scope="project:p1", tags=("execution","retry"), text="RUN identity",
        applicability={"provider":"fake","workflow":"wf1"},
    )
    assert found == (kept,)
    assert isinstance(found[0], MemoryCandidate)
    assert not hasattr(service, "publish")
    assert not hasattr(service, "authorize")
