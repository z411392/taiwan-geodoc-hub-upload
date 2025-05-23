from google.cloud.firestore import (
    AsyncClient,
    AsyncCollectionReference,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.registration_repository import (
    RegistrationRepository,
)
from taiwan_geodoc_hub.modules.registration_managing.dtos.registration import (
    Registration,
)
from taiwan_geodoc_hub.modules.system_maintaining.types.collection import (
    Collection,
)
from taiwan_geodoc_hub.modules.system_maintaining.constants.tokens import (
    SnapshotId,
)
from injector import inject
from taiwan_geodoc_hub.infrastructure.transactions.firestore_unit_of_work import (
    FirestoreUnitOfWork as UnitOfWork,
)


class RegistrationAdapter(RegistrationRepository[UnitOfWork]):
    _collection: AsyncCollectionReference

    @inject
    def __init__(
        self,
        /,
        db: AsyncClient,
        snapshot_id: SnapshotId,
    ):
        self._collection = db.collection(
            str(Collection.Registrations).replace(":snapshotId", snapshot_id)
        )

    async def exists(
        self,
        registration_id: str,
        /,
        unit_of_work: UnitOfWork,
    ):
        document = self._collection.document(registration_id)
        db: AsyncClient = unit_of_work.transaction._client
        document_snapshot = await anext(
            aiter(db.get_all([document], transaction=unit_of_work.transaction))
        )
        return document_snapshot.exists

    async def save(
        self,
        registration_id: str,
        registration: Registration,
        /,
        unit_of_work: UnitOfWork,
    ):
        data = {k: v for k, v in registration.items() if k not in ("id")}
        data["type"] = str(data["type"])
        document = self._collection.document(registration_id)
        unit_of_work.transaction.set(document, data, merge=True)
