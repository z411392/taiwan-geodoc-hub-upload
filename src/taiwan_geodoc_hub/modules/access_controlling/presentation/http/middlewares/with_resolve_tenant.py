from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from injector import InstanceProvider, Injector
from taiwan_geodoc_hub.modules.access_controlling.application.queries.resolve_tenant import (
    ResolveTenant,
)
from taiwan_geodoc_hub.modules.access_controlling.exceptions.tenant_not_found import (
    TenantNotFound,
)
from typing import Callable, Coroutine
from taiwan_geodoc_hub.modules.general.constants.tokens import TenantId


def with_resolve_tenant(enforce: bool):
    class Middleware(BaseHTTPMiddleware):
        async def dispatch(
            self,
            request: Request,
            call_next: Callable[[Request], Coroutine[None, None, Response]],
        ):
            injector: Injector = request.scope["injector"]
            tenant_id = request.path_params.get("tenant_id")
            handler = injector.get(ResolveTenant)
            tenant = await handler(tenant_id)
            if tenant is None and enforce:
                raise TenantNotFound(tenant_id)
            if tenant:
                request.scope["tenant"] = tenant
                injector.binder.bind(TenantId, to=InstanceProvider(tenant.get("id")))
            return await call_next(request)

    return Middleware
