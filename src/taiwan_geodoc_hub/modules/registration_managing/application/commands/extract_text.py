from taiwan_geodoc_hub.infrastructure.helpers.media.pdf.pdf_text_extractor import (
    PDFTextExtractor,
)
from io import StringIO
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driving.ocr_through_cache_port import (
    OCRThroughCachePort,
)
from injector import inject
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driving.extract_text_port import (
    ExtractTextPort,
)


class ExtractText(ExtractTextPort):
    _ocr: OCRThroughCachePort

    @inject
    def __init__(
        self,
        /,
        ocr: OCRThroughCachePort,
    ):
        self._ocr = ocr

    async def _rip_from_image(self, ripped: StringIO, image: bytes):
        ocr_result = await self._ocr(image)
        ripped.write(f"\n{ocr_result}")

    async def _append_text(self, ripped: StringIO, text: str):
        ripped.write(f"\n{text}")

    async def __call__(self, pdf: bytes):
        pdf_text_extractor = PDFTextExtractor(pdf)
        buffered = StringIO()
        for is_image, content in pdf_text_extractor:
            if is_image:
                await self._rip_from_image(buffered, content)
            else:
                await self._append_text(buffered, content)
        ripped = buffered.getvalue()
        stripped = ripped.strip()
        return stripped
