from abc import ABC, abstractmethod
from taiwan_geodoc_hub.modules.registration_managing.dtos.registration import (
    Registration,
)
from typing import Generic, TypeVar, Awaitable
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
    UnitOfWork,
)

UnitOfWork = TypeVar("UnitOfWork", bound=UnitOfWork)


class RegistrationRepository(ABC, Generic[UnitOfWork]):
    @abstractmethod
    def exists(
        self,
        registration_id: str,
        /,
        unit_of_work: UnitOfWork,
    ) -> Awaitable[bool]:
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        registration_id: str,
        data: Registration,
        /,
        unit_of_work: UnitOfWork,
    ) -> Awaitable[None]:
        raise NotImplementedError
