from injector import inject
from logging import Logger
from taiwan_geodoc_hub.modules.general.domain.ports.driven.wait_for_process_completion import (
    WaitForProcessCompletionPort,
)


class WaitForProcessCompletion:
    _logger: Logger
    _wait_for_process_completion_port: WaitForProcessCompletionPort

    @inject
    async def __init__(
        self,
        /,
        logger: Logger,
        wait_for_process_completion_port: WaitForProcessCompletionPort,
    ):
        self._logger = logger
        self._wait_for_process_completion_port = wait_for_process_completion_port

    async def __call__(self, process_state_id: str):
        await self._wait_for_process_completion_port.wait_for_process_completion(
            process_state_id
        )
