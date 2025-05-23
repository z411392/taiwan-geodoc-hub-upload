from google.cloud.firestore import AsyncClient, async_transactional, AsyncTransaction
from asyncio import Future, create_task, Task
from typing import Optional, Self
from injector import inject
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
    UnitOfWork,
)
from taiwan_geodoc_hub.utils.asyncio import ensure_event_loop


class _UnitOfWorkManagerAlreadyInUseError(Exception):
    pass


class _ManuallyRollback(Exception):
    pass


class FirestoreUnitOfWork(UnitOfWork):
    _db: AsyncClient
    _future: Optional[Future] = None
    _task: Optional[Task] = None
    _transaction: Optional[AsyncTransaction] = None

    @property
    def transaction(self) -> Optional[AsyncTransaction]:
        return self._transaction

    @inject
    def __init__(self, db: AsyncClient):
        self._db = db

    async def __aenter__(self) -> Self:
        if self._future is not None or self._task is not None:
            raise _UnitOfWorkManagerAlreadyInUseError()
        loop = ensure_event_loop()
        self._future = loop.create_future()
        wait_for_transaction_start = loop.create_future()
        transaction = self._db.transaction()

        @async_transactional
        async def run_in_transaction(_: AsyncTransaction):
            wait_for_transaction_start.set_result(None)
            await self._future

        self._task = create_task(run_in_transaction(transaction))
        await wait_for_transaction_start
        self._transaction = transaction
        return self

    def commit(self):
        if self._future.done():
            return
        self._future.set_result(None)

    def rollback(self, exception: Optional[BaseException] = None):
        if self._future.done():
            return
        if exception is None:
            exception = _ManuallyRollback()
        self._future.set_exception(exception)

    async def __aexit__(self, exc_type, exc_value: Optional[BaseException], exc_tb):
        try:
            if self._task.done():
                if exception := self._task.exception():
                    raise exception.with_traceback(exception.__traceback__)
                return
            if not self._future.done():
                if exc_type is None:
                    self.commit()
                else:
                    exception: Optional[BaseException] = None
                    if exc_tb:
                        exception = exc_value.with_traceback(exc_tb)
                    else:
                        exception = exc_value
                    self.rollback(exception)
            await self._task
        finally:
            self._future = None
            self._task = None
            self._transaction = None
