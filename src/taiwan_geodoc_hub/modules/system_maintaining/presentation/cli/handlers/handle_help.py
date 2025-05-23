from click.core import Context
from taiwan_geodoc_hub.utils.asyncio import ensure_event_loop
from taiwan_geodoc_hub.utils.lifespan import ensure_injector
from prefect import flow, get_run_logger
from logging import Logger
from os import environ


async def handle_help_async(context: Context):
    logger = get_run_logger()
    logger.info(dict(environ))
    injector = await ensure_injector(context)
    injector.binder.bind(Logger, logger)
    logger.info("-----------hello world----------------")


@flow
def handle_help(context: Context):
    loop = ensure_event_loop()
    return loop.run_until_complete(handle_help_async(context))
