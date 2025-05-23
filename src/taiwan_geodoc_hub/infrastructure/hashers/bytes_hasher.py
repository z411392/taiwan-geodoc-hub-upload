import hashlib
from io import BytesIO
from uuid import uuid5, UUID
from taiwan_geodoc_hub.modules.general.enums.namespace import Namespace
from base62 import encodebytes


class BytesHasher:
    _chunk_size: int
    _namesapce: UUID

    def __init__(
        self, /, chunk_size: int = 8192, namespace: UUID | None = None
    ) -> None:
        self._chunk_size = chunk_size
        if namespace is None:
            namespace = UUID(str(Namespace.NIL))
        self._namesapce = namespace

    def __call__(self, buffer: bytes) -> str:
        md5 = hashlib.md5()
        io = BytesIO(buffer)
        while chunk := io.read(self._chunk_size):
            md5.update(chunk)
        uuid = uuid5(self._namesapce, md5.digest())
        return encodebytes(uuid.bytes)
