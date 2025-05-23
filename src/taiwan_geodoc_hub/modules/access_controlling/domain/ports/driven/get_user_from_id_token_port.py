from abc import ABC, abstractmethod
from typing import Optional, Awaitable
from firebase_admin.auth import UserRecord


class GetUserFromIdTokenPort(ABC):
    @abstractmethod
    def from_id_token(self, id_token: str) -> Awaitable[Optional[UserRecord]]:
        raise NotImplementedError
