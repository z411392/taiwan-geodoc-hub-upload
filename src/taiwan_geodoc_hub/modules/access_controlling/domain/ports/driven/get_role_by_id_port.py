from abc import ABC, abstractmethod
from typing import Optional, Awaitable
from taiwan_geodoc_hub.modules.access_controlling.dtos.role import Role


class GetRoleByIdPort(ABC):
    @abstractmethod
    def by_id(self, user_id: str) -> Awaitable[Optional[Role]]:
        raise NotImplementedError
