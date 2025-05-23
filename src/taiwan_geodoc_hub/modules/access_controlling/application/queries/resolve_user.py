from injector import inject
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.get_user_from_id_token_port import (
    GetUserFromIdTokenPort,
)
from logging import Logger
from time import perf_counter


class ResolveUser:
    _get_user_from_id_token_port: GetUserFromIdTokenPort
    _logger: Logger

    @inject
    def __init__(
        self, get_user_from_id_token_port: GetUserFromIdTokenPort, logger: Logger
    ):
        self._get_user_from_id_token_port = get_user_from_id_token_port
        self._logger = logger

    async def __call__(self, id_token: str):
        start = perf_counter()
        try:
            user = await self._get_user_from_id_token_port.from_id_token(id_token)
            self._logger.info(
                "ResolveUser finished", extra=dict(elapsed=perf_counter() - start)
            )
            return user
        except Exception:
            self._logger.exception(
                "ResolveUser failed",
            )
            raise
