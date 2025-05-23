from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Awaitable
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
    UnitOfWork,
)

UnitOfWork = TypeVar("UnitOfWork", bound=UnitOfWork)


class SnapshotRepository(ABC, Generic[UnitOfWork]):
    @abstractmethod
    def exists(
        self,
        snapshot_id: str,
        /,
        unit_of_work: UnitOfWork,
    ) -> Awaitable[bool]:
        raise NotImplementedError
