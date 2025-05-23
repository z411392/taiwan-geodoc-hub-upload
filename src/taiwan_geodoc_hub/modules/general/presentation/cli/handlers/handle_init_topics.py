from click.core import Context
from taiwan_geodoc_hub.utils.asyncio import ensure_event_loop
from typer import Option
from google.cloud.pubsub import PublisherClient
from injector import Injector
from asyncio import get_running_loop
from taiwan_geodoc_hub.modules.general.enums.topic import Topic
from google.api_core.exceptions import AlreadyExists
from os import environ


async def handle_init_topics_async(context: Context, dev: bool):
    injector: Injector = context.obj
    if not dev:
        environ.pop("PUBSUB_EMULATOR_HOST")
    pubsub = injector.get(PublisherClient)
    for topic in Topic:
        try:
            await get_running_loop().run_in_executor(
                None,
                lambda: pubsub.create_topic(
                    request=dict(name=str(topic)),
                ),
            )
        except AlreadyExists:
            continue


def handle_init_topics(context: Context, dev: bool = Option(False)):
    loop = ensure_event_loop()
    return loop.run_until_complete(handle_init_topics_async(context, dev))
