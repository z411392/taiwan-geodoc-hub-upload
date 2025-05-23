from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.exceptions import ExceptionMiddleware
from taiwan_geodoc_hub.utils.lifespan import lifespan
from vellox import Vellox
from firebase_functions.https_fn import on_request
from taiwan_geodoc_hub.utils.asyncio import ensure_event_loop
from taiwan_geodoc_hub.modules.general.enums.bff import Bff
from taiwan_geodoc_hub.modules.general.presentation.http.middlewares.with_resolve_trace_id import (
    with_resolve_trace_id,
)
from taiwan_geodoc_hub.modules.general.presentation.http.handlers.exception_handler import (
    exception_handler,
)
from taiwan_geodoc_hub.modules.registration_managing.presentation.http.handlers.handle_upload_pdf import (
    handle_upload_pdf,
)
from taiwan_geodoc_hub.modules.access_controlling.presentation.http.middlewares.with_resolve_user import (
    with_resolve_user,
)
from taiwan_geodoc_hub.modules.access_controlling.presentation.http.middlewares.with_resolve_tenant import (
    with_resolve_tenant,
)
from taiwan_geodoc_hub.modules.access_controlling.presentation.http.middlewares.with_resolve_role import (
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
        with_resolve_trace_id(bff=str(Bff.Assets)),
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

starlette = Starlette(
    middleware=middleware,
    lifespan=lifespan,
    routes=routes,
    debug=False,
)

vellox = Vellox(
    app=starlette,
)


@on_request()
def assets(request):
    return ensure_event_loop().run_until_complete(vellox(request))
