import pytest
from injector import Injector, InstanceProvider
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.get_role_by_id_port import (
    GetRoleByIdPort,
)
from taiwan_geodoc_hub.modules.general.constants.tokens import (
    TenantId,
)
from os import getenv
from taiwan_geodoc_hub.modules.access_controlling.enums.role_type import RoleType


# @pytest.mark.skip(reason="")
class TestRoleDao:
    @pytest.fixture
    def get_role_by_id_port(self, injector: Injector):
        injector.binder.bind(TenantId, to=InstanceProvider(getenv("TENANT_ID")))
        return injector.get(GetRoleByIdPort)

    @pytest.mark.describe("要能夠取得 role")
    @pytest.mark.asyncio
    async def test_get_role_under_tenant(self, get_role_by_id_port: GetRoleByIdPort):
        user_id = getenv("USER_ID")
        role = await get_role_by_id_port.by_id(user_id=user_id)
        assert role.get("type") == RoleType.Manager
