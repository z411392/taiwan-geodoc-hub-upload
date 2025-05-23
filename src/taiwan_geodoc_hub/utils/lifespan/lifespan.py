from contextlib import asynccontextmanager
from starlette.applications import Starlette
from .startup import startup
from .shutdown import shutdown


@asynccontextmanager
async def lifespan(app=None):
    injector = await startup()
    if app:
        if isinstance(app, Starlette):
            app.state.injector = injector
        yield
    else:
        yield injector
    await shutdown()
