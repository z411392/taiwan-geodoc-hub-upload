from typing import Callable, Awaitable, Optional
from functools import wraps
from taiwan_geodoc_hub.modules.system_maintaining.constants.tokens import ProcessId
from taiwan_geodoc_hub.modules.system_maintaining.domain.ports.process_state_repository import (
    ProcessStateRepository,
)
from taiwan_geodoc_hub.modules.system_maintaining.types.process_status import (
    ProcessStatus,
)
from taiwan_geodoc_hub.modules.system_maintaining.dtos.process_state import (
    Progressing,
    Completed,
    Failed,
)
from taiwan_geodoc_hub.infrastructure.transactions.unit_of_work import (
    UnitOfWork,
)


class SingleExecutionPolicy:
    _process_state_repository: ProcessStateRepository
    _process_id: str
    _unit_of_work: UnitOfWork

    def __init__(
        self,
        /,
        process_state_repository: ProcessStateRepository,
        process_id: ProcessId,
        unit_of_work: UnitOfWork,
    ):
        self._process_state_repository = process_state_repository
        self._process_id = process_id
        self._unit_of_work = unit_of_work

    def __call__(self, callable: Callable[..., Awaitable[Optional[Exception]]]):
        @wraps(callable)
        async def wrapped(*args, **kwargs):
            async with self._unit_of_work as unit_of_work:
                try:
                    await self._process_state_repository.save(
                        Progressing(
                            id=self._process_id,
                            status=ProcessStatus.Progressing,
                        )
                    )
                    await callable(*args, **kwargs)
                    await self._process_state_repository.save(
                        Completed(id=self._process_id),
                    )
                    unit_of_work.commit()
                except Exception as exception:
                    await self._process_state_repository.save(
                        Failed(id=self._process_id, reason=str(exception)),
                    )
                    unit_of_work.commit()
                    return exception

        return wrapped
