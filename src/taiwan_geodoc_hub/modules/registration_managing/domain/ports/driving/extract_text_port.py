from abc import ABC, abstractmethod
from typing import Awaitable


class ExtractTextPort(ABC):
    @abstractmethod
    def __call__(self, pdf: bytes) -> Awaitable[str]:
        raise NotImplementedError
