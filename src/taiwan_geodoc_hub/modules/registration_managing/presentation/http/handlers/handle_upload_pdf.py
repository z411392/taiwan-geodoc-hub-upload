from starlette.responses import JSONResponse
from starlette.requests import Request
from base64 import b64decode
from taiwan_geodoc_hub.modules.general.constants.tokens import TraceId
from taiwan_geodoc_hub.modules.registration_managing.application.commands.upload_pdf import (
    UploadPDF,
)
from injector import Injector
from taiwan_geodoc_hub.modules.general.enums.bff import Bff


async def handle_upload_pdf(request: Request):
    injector: Injector = request.scope["injector"]
    json: dict = await request.json()
    pdf = b64decode(json["content"])
    name: str = json["name"]

    flow = injector.get(UploadPDF).__call__
    trace_id = injector.get(TraceId)
    handler = flow.with_options(flow_run_name=trace_id)
    snapshot_id = await handler(name, pdf)
    return JSONResponse(
        dict(
            success=True,
            data=dict(
                snapshotId=snapshot_id,
            ),
        )
    )
