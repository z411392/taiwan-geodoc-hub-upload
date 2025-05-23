from operator import itemgetter
from taiwan_geodoc_hub.modules.access_controlling.application.queries.resolve_credentials import (
    ResolveCredentials,
)
from taiwan_geodoc_hub.infrastructure.generators.trace_id_generator import (
    TraceIdGenerator,
)
from injector import InstanceProvider, Injector
from taiwan_geodoc_hub.modules.general.constants.tokens import TraceId
from click.core import Context
from taiwan_geodoc_hub.utils.asyncio import ensure_event_loop


async def handle_login_async(context: Context):
    injector: Injector = context.obj
    next_trace_id = injector.get(TraceIdGenerator)
    trace_id = next_trace_id()
    injector.binder.bind(TraceId, to=InstanceProvider(trace_id))
    handler = injector.get(ResolveCredentials)
    credentials = await handler()
    id_token = itemgetter("idToken")(credentials)
    print(id_token)


def handle_login(context: Context):
    loop = ensure_event_loop()
    return loop.run_until_complete(handle_login_async(context))
