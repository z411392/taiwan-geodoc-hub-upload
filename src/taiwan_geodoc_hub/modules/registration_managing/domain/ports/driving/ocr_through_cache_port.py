from abc import ABC, abstractmethod
from typing import Awaitable, Optional


class OCRThroughCachePort(ABC):
    @abstractmethod
    def __call__(self, image: bytes) -> Awaitable[Optional[str]]:
        raise NotImplementedError
