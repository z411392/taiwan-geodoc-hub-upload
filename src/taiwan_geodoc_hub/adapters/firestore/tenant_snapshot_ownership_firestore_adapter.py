from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.tenant_snapshot_ownership_repository import (
    TenantSnapshotOwnershipRepository,
)
from taiwan_geodoc_hub.infrastructure.transactions.firestore_unit_of_work import (
    FirestoreUnitOfWork as UnitOfWork,
)
from injector import inject
from google.cloud.firestore import (
    AsyncCollectionReference,
    AsyncClient,
)
from taiwan_geodoc_hub.modules.general.enums.collection import (
    Collection,
)
from taiwan_geodoc_hub.modules.general.constants.tokens import (
    TenantId,
)
from taiwan_geodoc_hub.modules.access_controlling.dtos.tenant_snapshot_ownership import (
    TenantSnapshotOwnership,
)


class TenantSnapshotOwnershipFirestoreAdapter(
    TenantSnapshotOwnershipRepository[UnitOfWork]
):
    _collection: AsyncCollectionReference

    @inject
    def __init__(
        self,
        db: AsyncClient,
        tenant_id: TenantId,
    ):
        self._collection = db.collection(
            str(Collection.TenantSnapshotOwnerships).replace(":tenantId", tenant_id)
        )

    async def load(
        self,
        date: str,
        /,
        unit_of_work: UnitOfWork,
    ):
        document = self._collection.document(date)
        db: AsyncClient = unit_of_work.transaction._client
        document_snapshot = await anext(
            aiter(db.get_all([document], transaction=unit_of_work.transaction))
        )
        if not document_snapshot.exists:
            return None
        return TenantSnapshotOwnership(
            id=document_snapshot.id,
            **document_snapshot.to_dict(),
        )

    async def save(
        self,
        date: str,
        tenant_snapshot_ownership: TenantSnapshotOwnership,
        /,
        unit_of_work: UnitOfWork,
    ):
        document = self._collection.document(date)
        data = tenant_snapshot_ownership.copy()
        data.pop("id", None)
        unit_of_work.transaction.set(document, data, merge=True)
