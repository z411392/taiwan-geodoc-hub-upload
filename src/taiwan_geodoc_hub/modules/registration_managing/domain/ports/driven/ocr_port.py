from abc import ABC, abstractmethod
from typing import Awaitable, Optional


class OCRPort(ABC):
    @abstractmethod
    def ocr(self, image: bytes) -> Awaitable[Optional[str]]:
        raise NotImplementedError
