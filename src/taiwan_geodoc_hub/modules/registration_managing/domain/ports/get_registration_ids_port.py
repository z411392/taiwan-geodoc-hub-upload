from abc import ABC, abstractmethod
from typing import Awaitable, List


class GetRegistrationIdsPort(ABC):
    @abstractmethod
    def registration_ids(
        self,
        snapshot_id: str,
    ) -> Awaitable[List[str]]:
        raise NotImplementedError
