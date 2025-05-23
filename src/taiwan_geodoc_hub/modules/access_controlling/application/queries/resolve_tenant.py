from injector import inject
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.get_tenant_by_id_port import (
    GetTenantByIdPort,
)
from logging import Logger
from time import perf_counter
from taiwan_geodoc_hub.modules.access_controlling.enums.tenant_status import (
    TenantStatus,
)


class ResolveTenant:
    _get_tenant_by_id_port: GetTenantByIdPort
    _logger: Logger

    @inject
    def __init__(
        self,
        get_tenant_by_id_port: GetTenantByIdPort,
        logger: Logger,
    ):
        self._get_tenant_by_id_port = get_tenant_by_id_port
        self._logger = logger

    async def __call__(self, tenant_id: str):
        start = perf_counter()
        try:
            tenant = await self._get_tenant_by_id_port.by_id(tenant_id)
            if tenant and tenant.get("status") != TenantStatus.Approved:
                tenant = None
            self._logger.info(
                "ResolveTenant finished", extra=dict(elapsed=perf_counter() - start)
            )
            return tenant
        except Exception:
            self._logger.exception(
                "ResolveTenant failed",
            )
            raise
