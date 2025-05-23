from typer import Typer
from click.core import Context
from taiwan_geodoc_hub.utils.asyncio import ensure_event_loop
from taiwan_geodoc_hub.utils.lifespan import startup
from taiwan_geodoc_hub.utils.lifespan import shutdown
from atexit import register
from taiwan_geodoc_hub.entrypoints.cli.auth import auth
from taiwan_geodoc_hub.entrypoints.cli.topics import topics


def middleware(context: Context):
    loop = ensure_event_loop()
    context.obj = loop.run_until_complete(startup())
    register(lambda: loop.run_until_complete(shutdown()))


typer = Typer(callback=middleware)
typer.add_typer(auth)
typer.add_typer(topics)
