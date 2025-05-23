from abc import ABC, abstractmethod
from typing import Self


class UnitOfWork(ABC):
    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, exc_tb):
        raise NotImplementedError
