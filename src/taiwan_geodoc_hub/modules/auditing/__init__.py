from injector import Module, ClassProvider
from taiwan_geodoc_hub.modules.auditing.domain.ports.driven.tenant_daily_usage_repository import (
    TenantDailyUsageRepository,
)
from taiwan_geodoc_hub.adapters.firestore.tenant_daily_usage_firestore_adapter import (
    TenantDailyUsageFirestoreAdapter,
)


class AuditingModule(Module):
    def configure(self, binder):
        binder.bind(
            TenantDailyUsageRepository,
            to=ClassProvider(TenantDailyUsageFirestoreAdapter),
        )


auditing_module = AuditingModule()
