import pytest
from injector import Injector
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driving.ocr_through_cache_port import (
    OCRThroughCachePort,
)


# @pytest.mark.skip(reason="")
class TestOCRSpace:
    @pytest.fixture
    def ocr_service(self, injector: Injector):
        return injector.get(OCRThroughCachePort)

    @pytest.mark.describe("要能夠 ocr")
    @pytest.mark.asyncio
    async def test_ocr(
        self,
        sample_image: bytes,
        ocr: OCRThroughCachePort,
        sample_ocr_result: str,
    ):
        text = await ocr(sample_image)
        assert text == sample_ocr_result
