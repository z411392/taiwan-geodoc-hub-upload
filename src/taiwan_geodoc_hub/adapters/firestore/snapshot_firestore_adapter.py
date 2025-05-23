from google.cloud.firestore import (
    AsyncClient,
    AsyncCollectionReference,
)
from google.cloud.firestore_v1.async_query import AsyncAggregationQuery, AsyncQuery
from taiwan_geodoc_hub.modules.general.enums.collection import (
    Collection,
)
from injector import inject
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.snapshot_repository import (
    SnapshotRepository,
)
from taiwan_geodoc_hub.infrastructure.transactions.firestore_unit_of_work import (
    FirestoreUnitOfWork as UnitOfWork,
)
from typing import List
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.get_registration_ids_port import (
    GetRegistrationIdsPort,
)


class SnapshotFirestoreAdapter(SnapshotRepository[UnitOfWork], GetRegistrationIdsPort):
    _collection: AsyncCollectionReference

    @inject
    def __init__(self, /, db: AsyncClient):
        self._collection = db.collection(str(Collection.Snapshots))

    async def exists(
        self,
        snapshot_id: str,
        /,
        unit_of_work: UnitOfWork,
    ):
        count = await self._registrations_count(snapshot_id, unit_of_work=unit_of_work)
        return count > 0

    async def _registrations_count(
        self,
        snapshot_id: str,
        /,
        unit_of_work: UnitOfWork,
    ):
        document = self._collection.document(snapshot_id)
        subcollection: AsyncCollectionReference = document.collection("registrations")
        query: AsyncAggregationQuery = subcollection.count()
        stream = query.stream(transaction=unit_of_work.transaction)

        async for query_results in stream:
            for query_result in query_results:
                return int(query_result.value)
        return 0

    async def registration_ids(self, snapshot_id: str):
        document = self._collection.document(snapshot_id)
        subcollection: AsyncCollectionReference = document.collection("registrations")
        query: AsyncQuery = subcollection.select([])
        stream = query.stream()

        registration_ids: List[str] = []
        async for document_snapshot in stream:
            registration_ids.append(document_snapshot.id)
        return registration_ids
