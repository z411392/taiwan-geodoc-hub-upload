import pytest
from injector import Injector
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.get_user_from_id_token_port import (
    GetUserFromIdTokenPort,
)
from os import getenv


# @pytest.mark.skip(reason="")
class TestUserDao:
    @pytest.fixture
    def get_user_from_id_token_port(self, injector: Injector):
        return injector.get(GetUserFromIdTokenPort)

    @pytest.mark.describe("要能夠解析 id_token")
    @pytest.mark.asyncio
    async def test_user_from_id_token(
        self, get_user_from_id_token_port: GetUserFromIdTokenPort
    ):
        id_token = getenv("ID_TOKEN")
        user = await get_user_from_id_token_port.from_id_token(id_token)
        assert user is not None
