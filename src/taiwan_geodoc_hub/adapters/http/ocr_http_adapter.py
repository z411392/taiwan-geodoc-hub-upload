from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.ocr_port import (
    OCRPort,
)
from injector import inject
from taiwan_geodoc_hub.infrastructure.clients.http.ocr_space import OCRSpace


class OCRHttpAdapter(OCRPort):
    _ocr_space: OCRSpace

    @inject
    def __init__(self, /, ocr_space: OCRSpace):
        self._ocr_space = ocr_space

    async def ocr(self, image: bytes):
        text = await self._ocr_space.ocr(image)
        return text
