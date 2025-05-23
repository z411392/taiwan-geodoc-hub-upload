from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Awaitable
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
    UnitOfWork,
)

UnitOfWork = TypeVar("UnitOfWork", bound=UnitOfWork)


class OCRResultRepository(ABC, Generic[UnitOfWork]):
    @abstractmethod
    def load(
        self, ocr_result_id: str, /, unit_of_work: UnitOfWork
    ) -> Awaitable[Optional[str]]:
        raise NotImplementedError

    @abstractmethod
    def save(
        self, ocr_result_id: str, text: str, /, unit_of_work: UnitOfWork
    ) -> Awaitable[None]:
        raise NotImplementedError
