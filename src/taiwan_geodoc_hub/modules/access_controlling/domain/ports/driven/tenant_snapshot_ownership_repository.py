from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Awaitable, Optional
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
    UnitOfWork,
)
from taiwan_geodoc_hub.modules.access_controlling.dtos.tenant_snapshot_ownership import (
    TenantSnapshotOwnership,
)

UnitOfWork = TypeVar("UnitOfWork", bound=UnitOfWork)


class TenantSnapshotOwnershipRepository(ABC, Generic[UnitOfWork]):
    @abstractmethod
    def load(
        self,
        snapshot_id: str,
        /,
        unit_of_work: UnitOfWork,
    ) -> Awaitable[Optional[TenantSnapshotOwnership]]:
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        snapshot_id: str,
        tenant_snapshot_ownership: TenantSnapshotOwnership,
        /,
        unit_of_work: UnitOfWork,
    ) -> Awaitable[None]:
        raise NotImplementedError
