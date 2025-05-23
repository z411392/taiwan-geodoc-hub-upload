from abc import ABC, abstractmethod
from taiwan_geodoc_hub.modules.auditing.dtos.tenant_daily_usage import (
    TenantDailyUsage,
)
from typing import Generic, TypeVar, Awaitable, Optional
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
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
        tenant_daily_usage: TenantDailyUsage,
        /,
        unit_of_work: UnitOfWork,
    ) -> Awaitable[None]:
        raise NotImplementedError
