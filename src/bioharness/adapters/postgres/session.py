from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .repositories import ArtifactRepository, MemoryRepository, PlanningRepository, RunRepository, ValidationRepository


@lru_cache(maxsize=8)
def _engine(database_url: str):
    return create_engine(database_url, future=True, pool_pre_ping=True)


class PostgresUnitOfWork:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.session: Session | None = None

    def __enter__(self):
        maker = sessionmaker(bind=_engine(self.database_url), expire_on_commit=False, future=True)
        self.session = maker()
        self.planning = PlanningRepository(self.session)
        self.runs = RunRepository(self.session)
        self.artifacts = ArtifactRepository(self.session)
        self.validation = ValidationRepository(self.session)
        self.memory = MemoryRepository(self.session)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.session is None:
            return False
        try:
            if exc_type is not None:
                self.session.rollback()
        finally:
            self.session.close()
        return False

    def commit(self) -> None:
        assert self.session is not None
        self.session.commit()

    def rollback(self) -> None:
        assert self.session is not None
        self.session.rollback()
