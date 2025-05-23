from google.cloud.firestore import (
    AsyncClient,
    AsyncCollectionReference,
    DocumentSnapshot,
)
from taiwan_geodoc_hub.modules.general.enums.collection import (
    Collection,
)
from injector import inject
from typing import Awaitable, Callable, cast
from taiwan_geodoc_hub.modules.general.domain.ports.driven.process_state_repository import (
    ProcessStateRepository,
)
from datetime import datetime, timedelta, UTC
from taiwan_geodoc_hub.modules.general.dtos.process_state import ProcessState
from taiwan_geodoc_hub.modules.general.enums.process_status import (
    ProcessStatus,
)
from taiwan_geodoc_hub.infrastructure.transactions.firestore_unit_of_work import (
    FirestoreUnitOfWork as UnitOfWork,
)
from taiwan_geodoc_hub.modules.general.constants.tokens import UserId
from taiwan_geodoc_hub.utils.asyncio import ensure_event_loop


class ProcessStateFirestoreAdapter(ProcessStateRepository[UnitOfWork]):
    _collection: AsyncCollectionReference

    @inject
    def __init__(
        self,
        /,
        db: AsyncClient,
        userId: UserId,
    ):
        self._collection = db.collection(
            str(Collection.Processes).replace(":userId", userId)
        )

    async def load(
        self,
        process_state_id: str,
        /,
        unit_of_work: UnitOfWork,
    ):
        document = self._collection.document(process_state_id)
        db: AsyncClient = unit_of_work.transaction._client
        document_snapshot = await anext(
            aiter(db.get_all([document], transaction=unit_of_work.transaction))
        )
        if not document_snapshot.exists:
            return None
        data = document_snapshot.to_dict()
        data["status"] = ProcessStatus(data["status"])
        return ProcessState(
            id=document_snapshot.id,
            **data,
        )

    async def save(
        self,
        process_state_id: str,
        process_state: ProcessState,
        /,
        unit_of_work: UnitOfWork,
    ) -> Awaitable[None]:
        document = self._collection.document(process_state_id)
        data = process_state.copy()
        data.pop("id", None)
        data["status"] = str(data["status"])
        if data.get("expiredAt") is None:
            expired_at = datetime.now(UTC) + timedelta(minutes=10)
            data.update(
                expiredAt=expired_at,
            )
        unit_of_work.transaction.set(document, data, merge=True)

    async def wait_for_process_completion(
        self,
        process_state_id: str,
    ) -> Awaitable[None]:
        document = self._collection.document(process_state_id)
        loop = ensure_event_loop()
        future = loop.create_future()

        def on_snapshot(document_snapshot: DocumentSnapshot):
            if not document_snapshot.exists:
                if not future.done():
                    future.set_result(None)
                return
            data = document_snapshot.to_dict()
            if data["status"] == ProcessStatus.Completed:
                if not future.done():
                    future.set_result(None)
            elif data["status"] == ProcessStatus.Failed:
                if not future.done():
                    future.set_exception(Exception(data.get("reason")))

        unsubscribe = cast(Callable[..., None], document.on_snapshot(on_snapshot))
        try:
            await future
        except Exception:
            raise
        finally:
            unsubscribe()
