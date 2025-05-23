from google.cloud.firestore import (
    AsyncClient,
    AsyncCollectionReference,
)
from taiwan_geodoc_hub.modules.system_maintaining.types.collection import (
    Collection,
)
from injector import inject
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.snapshot_repository import (
    SnapshotRepository,
)
from taiwan_geodoc_hub.infrastructure.transactions.firestore_unit_of_work import (
    FirestoreUnitOfWork as UnitOfWork,
)


class SnapshotAdapter(SnapshotRepository[UnitOfWork]):
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
        document = self._collection.document(snapshot_id)
        db: AsyncClient = unit_of_work.transaction._client
        document_snapshot = await anext(
            aiter(db.get_all([document], transaction=unit_of_work.transaction))
        )
        return document_snapshot.exists
