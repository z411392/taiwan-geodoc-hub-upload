from abc import ABC, abstractmethod
from typing import Optional, Awaitable
from taiwan_geodoc_hub.modules.access_controlling.dtos.tenant import Tenant


class GetTenantByIdPort(ABC):
    @abstractmethod
    def by_id(self, tenant_id: str) -> Awaitable[Optional[Tenant]]:
        raise NotImplementedError
