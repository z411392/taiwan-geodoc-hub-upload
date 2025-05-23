from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware
from taiwan_geodoc_hub.utils.lifespan import lifespan
from taiwan_geodoc_hub.modules.general.presentation.http.middlewares.with_resolve_trace_id import (
    WithResolveTraceId,
)
from taiwan_geodoc_hub.modules.general.presentation.http.handlers.exception_handler import (
    exception_handler,
)
from taiwan_geodoc_hub.modules.registration_managing.presentation.http.handlers.handle_upload_pdf import (
    handle_upload_pdf,
)
from taiwan_geodoc_hub.modules.access_managing.presentation.http.middlewares.with_resolve_user import (
    with_resolve_user,
)
from taiwan_geodoc_hub.modules.access_managing.presentation.http.middlewares.with_resolve_tenant import (
    with_resolve_tenant,
)
from taiwan_geodoc_hub.modules.access_managing.presentation.http.middlewares.with_resolve_role import (
    with_resolve_role,
)


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    ),
    Middleware(
        WithResolveTraceId,
    ),
    Middleware(
        ExceptionMiddleware,
        handlers={Exception: exception_handler},
    ),
]

routes = [
    Route(
        "/tenants/{tenant_id}/pdf",
        handle_upload_pdf,
        methods=["POST"],
        middleware=[
            Middleware(
                with_resolve_user(enforce=True),
            ),
            Middleware(
                with_resolve_tenant(enforce=True),
            ),
            Middleware(
                with_resolve_role(enforce=True),
            ),
        ],
    ),
]

app = Starlette(
    middleware=middleware,
    lifespan=lifespan,
    routes=routes,
    debug=False,
)
