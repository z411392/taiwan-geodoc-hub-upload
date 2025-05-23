from starlette.middleware.base import BaseHTTPMiddleware
from injector import InstanceProvider
from taiwan_geodoc_hub.modules.system_maintaining.constants.tokens import TraceId
from taiwan_geodoc_hub.infrastructure.generators.trace_id_generator import (
    TraceIdGenerator,
)
from taiwan_geodoc_hub.utils.lifespan import ensure_injector


class WithResolveTraceId(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        injector = await ensure_injector(request)
        next_trace_id = injector.get(TraceIdGenerator)
        trace_id = next_trace_id()
        request.scope["trace_id"] = trace_id
        injector.binder.bind(TraceId, to=InstanceProvider(trace_id))
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response
