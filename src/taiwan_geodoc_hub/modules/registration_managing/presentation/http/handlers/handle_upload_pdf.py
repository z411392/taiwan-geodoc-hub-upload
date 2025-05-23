from starlette.responses import JSONResponse
from starlette.requests import Request
from base64 import b64decode
from taiwan_geodoc_hub.modules.general.constants.tokens import TraceId
from taiwan_geodoc_hub.modules.registration_managing.application.commands.upload_pdf import (
    UploadPDF,
)
from injector import Injector
from marshmallow import Schema, fields, ValidationError, pre_load


class Validator(Schema):
    name = fields.String(required=True, validate=lambda s: len(s) > 0)
    content = fields.String(required=True)  # base64 string

    @pre_load
    def decode_content(self, data):
        if "content" in data:
            try:
                data["content"] = b64decode(data["content"])
            except Exception:
                raise ValidationError("Invalid base64 content", field_name="content")
        return data


async def handle_upload_pdf(request: Request):
    injector: Injector = request.scope["injector"]
    validator = Validator()
    command = validator.load(**await request.json())
    handler = (
        lambda flow, flow_run_name: flow.with_options(flow_run_name=flow_run_name)
    )(
        injector.get(UploadPDF).__call__,
        injector.get(TraceId),
    )
    snapshot_id = await handler(command["name"], command["content"])
    return JSONResponse(
        dict(
            success=True,
            data=dict(
                snapshotId=snapshot_id,
            ),
        )
    )
