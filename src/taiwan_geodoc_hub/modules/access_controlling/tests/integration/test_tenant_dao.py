import pytest
from injector import Injector
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.get_tenant_by_id_port import (
    GetTenantByIdPort,
)
from os import getenv


# @pytest.mark.skip(reason="")
class TestTenantDao:
    @pytest.fixture
    def get_tenant_by_id_port(self, injector: Injector):
        get_tenant_by_id_port = injector.get(GetTenantByIdPort)
        return get_tenant_by_id_port

    @pytest.mark.describe("要能夠取得 tenant")
    @pytest.mark.asyncio
    async def test_get_tenant_by_id(self, get_tenant_by_id_port: GetTenantByIdPort):
        tenant_id: str = getenv("TENANT_ID")
        tenant = await get_tenant_by_id_port.by_id(tenant_id)
        if tenant is None:
            return pytest.fail(f"無法取得 tenant, tenant_id={tenant_id}")
        assert tenant.get("id") == tenant_id
