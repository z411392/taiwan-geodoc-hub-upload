from google.cloud.firestore import (
    AsyncCollectionReference,
    AsyncClient,
    FieldFilter,
)
from taiwan_geodoc_hub.modules.access_controlling.dtos.tenant import Tenant
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.get_tenant_by_id_port import (
    GetTenantByIdPort,
)
from taiwan_geodoc_hub.modules.general.enums.collection import (
    Collection,
)
from injector import inject
from taiwan_geodoc_hub.modules.access_controlling.enums.tenant_status import (
    TenantStatus,
)
from typing import List
from google.cloud.firestore_v1.field_path import FieldPath


class TenantFirestoreAdapter(GetTenantByIdPort):
    _collection: AsyncCollectionReference

    @inject
    def __init__(self, /, db: AsyncClient):
        self._collection = db.collection(str(Collection.Tenants))

    async def in_ids(self, tenant_ids: List[str]) -> List[Tenant]:
        batch_size = 30
        tenants: List[Tenant] = []
        for offset in range(0, len(tenant_ids), batch_size):
            documents = list(
                map(self._collection.document, tenant_ids[offset : offset + batch_size])
            )
            stream = (
                self._collection.where(
                    filter=FieldFilter(
                        FieldPath.document_id(),
                        "in",
                        documents,
                    )
                )
                # .select([])
                .stream()
            )
            async for document_snapshot in stream:
                tenant_data = document_snapshot.to_dict()
                tenant = Tenant(
                    id=document_snapshot.id,
                    name=tenant_data.get("name"),
                    status=TenantStatus(tenant_data.get("status")),
                )
                tenants.append(tenant)
        return tenants

    async def by_id(self, tenant_id: str):
        tenants = await self.in_ids([tenant_id])
        if len(tenants) == 0:
            return None
        [tenant] = tenants
        return tenant
