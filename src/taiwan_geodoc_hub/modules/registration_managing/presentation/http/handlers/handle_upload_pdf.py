from starlette.responses import JSONResponse
from starlette.requests import Request
from base64 import b64decode
from taiwan_geodoc_hub.modules.system_maintaining.constants.tokens import TraceId
from taiwan_geodoc_hub.utils.lifespan import ensure_injector
from taiwan_geodoc_hub.modules.registration_managing.application.commands.upload_pdf import (
    UploadPDF,
)


async def handle_upload_pdf(request: Request):
    injector = await ensure_injector(request)
    json: dict = await request.json()
    pdf = b64decode(json["content"])
    name: str = json["name"]
    handler = (lambda flow: flow.with_options(flow_run_name=injector.get(TraceId)))(
        injector.get(UploadPDF).__call__
    )
    snapshot_id, trace_id = await handler(name, pdf)

    return JSONResponse(
        dict(
            success=True,
            data=dict(
                snapshotId=snapshot_id,
                traceId=trace_id,
            ),
        )
    )
