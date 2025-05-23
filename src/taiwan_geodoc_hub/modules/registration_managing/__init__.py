from injector import Module, ClassProvider, Provider
from taiwan_geodoc_hub.adapters.firestore.ocr_result_firestore_adapter import (
    OCRResultFirestoreAdapter,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.ocr_result_repository import (
    OCRResultRepository,
)
from taiwan_geodoc_hub.adapters.firestore.registration_firestore_adapter import (
    RegistrationFirestoreAdapter,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.registration_repository import (
    RegistrationRepository,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.snapshot_repository import (
    SnapshotRepository,
)
from taiwan_geodoc_hub.adapters.firestore.snapshot_firestore_adapter import (
    SnapshotFirestoreAdapter,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.ocr_service import (
    OCRService,
)
from taiwan_geodoc_hub.modules.general.application.policies.read_through_cache_policy import (
    ReadThroughCachePolicy,
)
from taiwan_geodoc_hub.infrastructure.hashers.bytes_hasher import BytesHasher

from taiwan_geodoc_hub.infrastructure.clients.http.ocr_space import OCRSpace
from taiwan_geodoc_hub.modules.general.domain.ports.unit_of_work import (
    UnitOfWork,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.get_registration_ids_port import (
    GetRegistrationIdsPort,
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
        binder.bind(OCRResultRepository, to=ClassProvider(OCRResultFirestoreAdapter))
        binder.bind(
            RegistrationRepository, to=ClassProvider(RegistrationFirestoreAdapter)
        )
        binder.bind(OCRService, to=OCRServiceProvider())
        binder.bind(SnapshotRepository, to=ClassProvider(SnapshotFirestoreAdapter))
        binder.bind(GetRegistrationIdsPort, to=ClassProvider(SnapshotFirestoreAdapter))


registration_managing_module = RegistrationManagingModule()
