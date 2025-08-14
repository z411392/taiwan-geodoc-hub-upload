from base64 import b64encode
from injector import inject
from os import getenv
from httpx import AsyncClient as HttpConnectionPool
from typing import Optional


class OCRSpace:
    _endpoint: str = "https://api.ocr.space/parse/image"
    _api_key: str
    _http_connection_pool: HttpConnectionPool
    _language: str = "cht"

    @inject
    def __init__(self, /, http_connection_pool: HttpConnectionPool):
        self._api_key = getenv("OCR_SPACE_API_KEY")
        self._http_connection_pool = http_connection_pool

    async def ocr(self, image: bytes) -> Optional[str]:
        base64_encoded = b64encode(image).decode("utf-8")
        base64_image = f"data:image/jpeg;base64,{base64_encoded}"
        body = {
            "apikey": self._api_key,
            "language": self._language,
            "base64Image": base64_image,
        }
        response = await self._http_connection_pool.post(self._endpoint, data=body)
        if response.status_code != 200:
            return None
        payload: dict = response.json()
        if "ParsedResults" not in payload:
            return ""
        results: dict = payload["ParsedResults"]
        joined = "".join(result["ParsedText"] for result in results)
        stripped = joined.replace("\r", "").replace("\n", "").strip()
        return stripped
