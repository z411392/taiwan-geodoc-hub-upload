from abc import ABC, abstractmethod
from taiwan_geodoc_hub.modules.registration_managing.dtos.tenant_daily_usage import (
    TenantDailyUsage,
)
from typing import Generic, TypeVar, Awaitable, Optional
from taiwan_geodoc_hub.infrastructure.transactions.unit_of_work import (
    UnitOfWork,
)

UnitOfWork = TypeVar("UnitOfWork", bound=UnitOfWork)


class TenantDailyUsageRepository(ABC, Generic[UnitOfWork]):
    @abstractmethod
    def load(
        self,
        date: str,
        /,
        unit_of_work: UnitOfWork,
    ) -> Awaitable[Optional[TenantDailyUsage]]:
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        date: str,
        data: TenantDailyUsage,
        /,
        unit_of_work: UnitOfWork,
    ) -> Awaitable[None]:
        raise NotImplementedError
