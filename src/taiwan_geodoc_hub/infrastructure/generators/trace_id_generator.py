from uuid import uuid1, uuid5, UUID
from base62 import encodebytes
from taiwan_geodoc_hub.modules.general.enums.namespace import Namespace
from typing import Optional


class TraceIdGenerator:
    def __call__(
        self,
        /,
        name: Optional[str] = None,
        namespace: Optional[UUID] = None,
        auto_increment: Optional[bool] = None,
        to_base62: Optional[bool] = None,
    ):
        if name is None:
            name = (
                Namespace.NIL.encode()
                if auto_increment is not None and not auto_increment
                else uuid1().bytes
            )
        if namespace is None:
            namespace = UUID(str(Namespace.Traces))
        uuid = uuid5(namespace, name)
        if to_base62 is not None and not to_base62:
            return uuid.hex
        return encodebytes(uuid.bytes)
