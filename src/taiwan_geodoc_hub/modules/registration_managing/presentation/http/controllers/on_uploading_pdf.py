from starlette.responses import JSONResponse
from starlette.requests import Request
from injector import Injector, InstanceProvider
from base64 import b64decode
from taiwan_geodoc_hub.modules.registration_managing.application.commands.upload_pdf import (
    UploadPDF,
)
from taiwan_geodoc_hub.infrastructure.utils.hashers.bytes_hasher import (
    BytesHasher,
)
from taiwan_geodoc_hub.infrastructure.constants.tokens import (
    SnapshotId,
)


async def on_uploading_pdf(request: Request):
    injector: Injector = request.scope["injector"]
    json: dict = await request.json()
    pdf = b64decode(json["content"])
    name: str = json["name"]
    hash_bytes = injector.get(BytesHasher)
    snapshot_id = hash_bytes(pdf)
    injector.binder.bind(SnapshotId, to=InstanceProvider(snapshot_id))
    handler = injector.get(UploadPDF)
    message_id = await handler(name, pdf)
    return JSONResponse(
        dict(
            success=True,
            data=dict(
                snapshotId=snapshot_id,
                messageId=message_id,
            ),
        )
    )
