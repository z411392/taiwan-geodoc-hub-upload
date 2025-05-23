from typing import Optional, Union
from starlette.requests import Request
from click.core import Context
from taiwan_geodoc_hub.utils.lifespan import startup
from typing import cast
from injector import Injector


async def ensure_injector(context: Optional[Union[Request, Context]] = None):
    if context is None:
        return await startup()

    if isinstance(context, Request):
        if "injector" not in context.scope:
            injector = cast(Injector, context.app.state.injector)
            context.scope["injector"] = injector.create_child_injector()
        return context.scope["injector"]

    if isinstance(context, Context):
        return context.obj
