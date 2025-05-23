from injector import inject
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.get_role_by_id_port import (
    GetRoleByIdPort,
)
from logging import Logger
from time import perf_counter
from taiwan_geodoc_hub.modules.access_controlling.enums.role_status import (
    RoleStatus,
)


class ResolveRole:
    _get_role_by_id_port: GetRoleByIdPort
    _logger: Logger

    @inject
    def __init__(
        self,
        get_role_by_id: GetRoleByIdPort,
        logger: Logger,
    ):
        self._get_role_by_id_port = get_role_by_id
        self._logger = logger

    async def __call__(self, user_id: str):
        start = perf_counter()
        try:
            role = await self._get_role_by_id_port.by_id(user_id=user_id)
            if role and role.get("status") != RoleStatus.Approved:
                role = None
            self._logger.info(
                "ResolveRole finished", extra=dict(elapsed=perf_counter() - start)
            )
            return role
        except Exception:
            self._logger.exception(
                "ResolveRole failed",
            )
            raise
