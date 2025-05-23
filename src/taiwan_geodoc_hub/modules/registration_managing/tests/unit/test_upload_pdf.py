import pytest
from injector import Injector, InstanceProvider
from taiwan_geodoc_hub.modules.general.constants.tokens import (
    TraceId,
    TenantId,
    UserId,
)
from base64 import b64decode
from os import getenv
from taiwan_geodoc_hub.modules.registration_managing.application.commands.upload_pdf import (
    UploadPDF,
)


# @pytest.mark.skip(reason="")
class TestBytesHasher:
    @pytest.mark.describe("要能夠上傳 pdf")
    @pytest.mark.asyncio
    async def test_upload_pdf(
        self,
        injector: Injector,
        sample_pdf: str,
        trace_id: str,
    ):
        pdf = b64decode(sample_pdf)
        injector.binder.bind(TraceId, to=InstanceProvider(trace_id))
        injector.binder.bind(UserId, to=InstanceProvider(getenv("USER_ID")))
        injector.binder.bind(TenantId, to=InstanceProvider(getenv("TENANT_ID")))
        handler = (lambda flow: flow.with_options(flow_run_name=injector.get(TraceId)))(
            injector.get(UploadPDF).__call__
        )
        await handler("建物謄本.pdf", pdf)
