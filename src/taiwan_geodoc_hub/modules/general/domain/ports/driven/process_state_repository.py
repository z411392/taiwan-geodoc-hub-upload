from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Awaitable
from taiwan_geodoc_hub.modules.general.dtos.process_state import (
    ProcessState,
)
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
    UnitOfWork,
)

UnitOfWork = TypeVar("UnitOfWork", bound=UnitOfWork)


class ProcessStateRepository(ABC, Generic[UnitOfWork]):
    @abstractmethod
    def load(
        self,
        process_state_id: str,
        /,
        unit_of_work: UnitOfWork,
    ) -> Awaitable[ProcessState]:
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        process_state_id: str,
        process_state: ProcessState,
        /,
        unit_of_work: UnitOfWork,
    ) -> Awaitable[None]:
        raise NotImplementedError
