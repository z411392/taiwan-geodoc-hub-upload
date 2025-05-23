from injector import inject
from taiwan_geodoc_hub.modules.general.dtos.process_state import (
    Progressing,
    Completed,
    Failed,
)
from taiwan_geodoc_hub.modules.general.enums.process_status import (
    ProcessStatus,
)
from typing import Callable, Awaitable
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
    UnitOfWork,
)
from taiwan_geodoc_hub.modules.general.domain.ports.driven.process_state_repository import (
    ProcessStateRepository,
)
from functools import wraps
from taiwan_geodoc_hub.modules.general.constants.tokens import ProcessId


class SingleExecutionPolicy:
    _process_state_id: str
    _process_state_repository: ProcessStateRepository
    _unit_of_work: UnitOfWork

    @inject
    def __init__(
        self,
        /,
        process_state_id: ProcessId,
        process_state_repository: ProcessStateRepository,
        unit_of_work: UnitOfWork,
    ):
        self._process_state_id = process_state_id
        self._process_state_repository = process_state_repository
        self._unit_of_work = unit_of_work

    def __call__(
        self,
        callable: Callable[..., Awaitable[None]],
    ):
        @wraps(callable)
        async def wrapped(*args, **kwargs):
            async with self._unit_of_work as unit_of_work:
                process_state = await self._process_state_repository.load(
                    self._process_state_id,
                    unit_of_work=unit_of_work,
                )
                if process_state and process_state.status in (
                    ProcessStatus.Completed,
                    ProcessStatus.Failed,
                ):
                    return
                await self._process_state_repository.save(
                    self._process_state_id,
                    Progressing(
                        status=ProcessStatus.Progressing,
                    ),
                    unit_of_work=unit_of_work,
                )
                try:
                    await callable(*args, **kwargs)
                    await self._process_state_repository.save(
                        self._process_state_id,
                        Completed(
                            status=ProcessStatus.Completed,
                        ),
                        unit_of_work=unit_of_work,
                    )
                    return None
                except Exception as exception:
                    await self._process_state_repository.save(
                        self._process_state_id,
                        Failed(
                            status=ProcessStatus.Failed,
                            reason=str(exception),
                        ),
                        unit_of_work=unit_of_work,
                    )
                    return exception

        return wrapped
