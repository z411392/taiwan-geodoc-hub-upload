from injector import Module, ClassProvider
from taiwan_geodoc_hub.adapters.firestore.ocr_result_firestore_adapter import (
    OCRResultFirestoreAdapter,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.ocr_result_repository import (
    OCRResultRepository,
)
from taiwan_geodoc_hub.adapters.firestore.registration_firestore_adapter import (
    RegistrationFirestoreAdapter,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.registration_repository import (
    RegistrationRepository,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.snapshot_repository import (
    SnapshotRepository,
)
from taiwan_geodoc_hub.adapters.firestore.snapshot_firestore_adapter import (
    SnapshotFirestoreAdapter,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.get_registration_ids_port import (
    GetRegistrationIdsPort,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.ocr_port import (
    OCRPort,
)
from taiwan_geodoc_hub.adapters.http.ocr_http_adapter import OCRHttpAdapter
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driving.ocr_through_cache_port import (
    OCRThroughCachePort,
)
from taiwan_geodoc_hub.modules.registration_managing.application.commands.ocr import OCR
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driving.extract_text_port import (
    ExtractTextPort,
)
from taiwan_geodoc_hub.modules.registration_managing.application.commands.extract_text import (
    ExtractText,
)


class RegistrationManagingModule(Module):
    def configure(self, binder):
        binder.bind(OCRResultRepository, to=ClassProvider(OCRResultFirestoreAdapter))
        binder.bind(
            RegistrationRepository, to=ClassProvider(RegistrationFirestoreAdapter)
        )
        binder.bind(OCRPort, to=ClassProvider(OCRHttpAdapter))
        binder.bind(OCRThroughCachePort, to=ClassProvider(OCR))
        binder.bind(SnapshotRepository, to=ClassProvider(SnapshotFirestoreAdapter))
        binder.bind(GetRegistrationIdsPort, to=ClassProvider(SnapshotFirestoreAdapter))
        binder.bind(ExtractTextPort, to=ClassProvider(ExtractText))


registration_managing_module = RegistrationManagingModule()
