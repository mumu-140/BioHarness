from typing import Protocol


class UnitOfWork(Protocol):
    planning: object
    runs: object
    artifacts: object
    validation: object
    memory: object

    def commit(self) -> None: ...
    def rollback(self) -> None: ...
