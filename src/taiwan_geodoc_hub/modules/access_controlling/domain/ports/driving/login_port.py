from abc import ABC, abstractmethod
from taiwan_geodoc_hub.modules.access_controlling.dtos.credentials import (
    Credentials,
)
from typing import Awaitable


class LoginPort(ABC):
    @abstractmethod
    def __call__(self) -> Awaitable[Credentials]:
        raise NotImplementedError
