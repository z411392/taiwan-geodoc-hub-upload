from starlette.middleware.base import BaseHTTPMiddleware
from injector import InstanceProvider, Injector
from taiwan_geodoc_hub.modules.general.constants.tokens import TraceId
from taiwan_geodoc_hub.infrastructure.generators.trace_id_generator import (
    TraceIdGenerator,
)


class WithResolveTraceId(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        parent_injector: Injector = request.app.state.injector
        injector = parent_injector.create_child_injector()
        next_trace_id = injector.get(TraceIdGenerator)
        trace_id = next_trace_id()
        request.scope["trace_id"] = trace_id
        injector.binder.bind(TraceId, to=InstanceProvider(trace_id))
        request.scope["injector"] = injector
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response
