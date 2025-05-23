from injector import Module, ClassProvider, Provider
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.tenant_daily_usage_repository import (
    TenantDailyUsageRepository,
)
from taiwan_geodoc_hub.adapters.firestore.tenant_daily_usage_adapter import (
    TenantDailyUsageAdapter,
)
from taiwan_geodoc_hub.adapters.firestore.ocr_result_adapter import (
    OCRResultAdapter,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.ocr_result_repository import (
    OCRResultRepository,
)
from taiwan_geodoc_hub.adapters.firestore.registration_adapter import (
    RegistrationAdapter,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.registration_repository import (
    RegistrationRepository,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.snapshot_repository import (
    SnapshotRepository,
)
from taiwan_geodoc_hub.adapters.firestore.snapshot_adapter import (
    SnapshotAdapter,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.ocr_service import (
    OCRService,
)
from taiwan_geodoc_hub.modules.system_maintaining.application.policies.read_through_cache_policy import (
    ReadThroughCachePolicy,
)
from taiwan_geodoc_hub.infrastructure.hashers.bytes_hasher import BytesHasher

from taiwan_geodoc_hub.adapters.http.ocr_space import OCRSpace
from taiwan_geodoc_hub.infrastructure.transactions.unit_of_work import (
    UnitOfWork,
)


class OCRServiceProvider(Provider[OCRService]):
    def get(self, injector):
        unit_of_work = injector.get(UnitOfWork)
        compute_key = injector.get(BytesHasher)
        ocr_result_repository = injector.get(OCRResultRepository)
        policy = ReadThroughCachePolicy[str](
            compute_key=compute_key,
            repository=ocr_result_repository,
            unit_of_work=unit_of_work,
        )
        ocr_space = injector.get(OCRSpace)
        return policy(ocr_space)


class RegistrationManagingModule(Module):
    def configure(self, binder):
        binder.bind(OCRResultRepository, to=ClassProvider(OCRResultAdapter))
        binder.bind(RegistrationRepository, to=ClassProvider(RegistrationAdapter))
        binder.bind(OCRService, to=OCRServiceProvider())
        binder.bind(SnapshotRepository, to=ClassProvider(SnapshotAdapter))
        binder.bind(
            TenantDailyUsageRepository, to=ClassProvider(TenantDailyUsageAdapter)
        )


registration_managing_module = RegistrationManagingModule()
