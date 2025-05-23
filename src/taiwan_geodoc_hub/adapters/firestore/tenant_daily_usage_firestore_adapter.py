from google.cloud.firestore import (
    AsyncClient,
    AsyncCollectionReference,
)
from taiwan_geodoc_hub.modules.general.enums.collection import (
    Collection,
)
from injector import inject
from taiwan_geodoc_hub.modules.general.constants.tokens import TenantId
from taiwan_geodoc_hub.modules.auditing.domain.ports.driven.tenant_daily_usage_repository import (
    TenantDailyUsageRepository,
)
from taiwan_geodoc_hub.modules.auditing.dtos.tenant_daily_usage import (
    TenantDailyUsage,
)
from datetime import datetime, timedelta, UTC
from taiwan_geodoc_hub.infrastructure.transactions.firestore_unit_of_work import (
    FirestoreUnitOfWork as UnitOfWork,
)


class TenantDailyUsageFirestoreAdapter(TenantDailyUsageRepository[UnitOfWork]):
    _collection: AsyncCollectionReference

    @inject
    def __init__(
        self,
        /,
        db: AsyncClient,
        tenant_id: TenantId,
    ):
        self._collection = db.collection(
            str(Collection.TenantDailyUsage).replace(":tenantId", tenant_id)
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
        return TenantDailyUsage(
            id=document_snapshot.id,
            **document_snapshot.to_dict(),
        )

    async def save(
        self,
        date: str,
        tenant_daily_usage: TenantDailyUsage,
        /,
        unit_of_work: UnitOfWork,
    ):
        document = self._collection.document(date)
        data = tenant_daily_usage.copy()
        data.pop("id", None)
        if data.get("expiredAt") is None:
            expired_at = datetime.now(UTC) + timedelta(days=1)
            data.update(
                expiredAt=expired_at,
            )
        unit_of_work.transaction.set(document, data, merge=True)
