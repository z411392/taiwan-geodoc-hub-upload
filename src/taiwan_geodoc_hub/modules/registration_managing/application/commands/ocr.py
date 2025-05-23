from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driving.ocr_through_cache_port import (
    OCRThroughCachePort,
)
from injector import inject
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
    UnitOfWork,
)
from taiwan_geodoc_hub.infrastructure.hashers.bytes_hasher import BytesHasher
from taiwan_geodoc_hub.modules.general.application.policies.read_through_cache_policy import (
    ReadThroughCachePolicy,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.ocr_result_repository import (
    OCRResultRepository,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.ocr_port import (
    OCRPort,
)


class OCR(OCRThroughCachePort):
    _unit_of_work: UnitOfWork
    _compute_key: BytesHasher
    _ocr_result_repository: OCRResultRepository
    _ocr_port: OCRPort

    @inject
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        compute_key: BytesHasher,
        ocr_result_repository: OCRResultRepository,
        ocr_port: OCRPort,
    ):
        self._unit_of_work = unit_of_work
        self._compute_key = compute_key
        self._ocr_result_repository = ocr_result_repository
        self._ocr_port = ocr_port

    async def ocr(self, image: bytes):
        policy = ReadThroughCachePolicy[str](
            compute_key=self._compute_key,
            repository=self._ocr_result_repository,
            unit_of_work=self._unit_of_work,
        )
        handler = policy(lambda image: self._ocr_port.ocr(image))
        text: str = await handler(image)
        return text
