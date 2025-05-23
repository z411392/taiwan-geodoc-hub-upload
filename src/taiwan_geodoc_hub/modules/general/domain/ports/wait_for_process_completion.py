from abc import ABC, abstractmethod
from typing import Awaitable


class WaitForProcessCompletionPort(ABC):
    @abstractmethod
    def wait_for_process_completion(self, process_state_id: str) -> Awaitable[None]:
        raise NotImplementedError
