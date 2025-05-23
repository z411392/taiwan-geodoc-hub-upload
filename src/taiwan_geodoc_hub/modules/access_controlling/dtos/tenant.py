from typing import TypedDict
from taiwan_geodoc_hub.modules.access_controlling.enums.tenant_status import (
    TenantStatus,
)


class Tenant(TypedDict):
    id: str
    name: str
    status: TenantStatus
