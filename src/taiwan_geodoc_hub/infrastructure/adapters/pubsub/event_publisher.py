from injector import inject
from google.cloud.pubsub import PublisherClient
from asyncio import wrap_future
from typing import Literal, overload
from taiwan_geodoc_hub.infrastructure.types.topic import Topic
from taiwan_geodoc_hub.modules.registration_managing.events.snapshot_created import (
    SnapshotCreated,
)
from json import dumps


class EventPublisher:
    _pubsub: PublisherClient

    @inject
    def __init__(self, /, pubsub: PublisherClient):
        self._pubsub = pubsub

    @overload
    async def publish(
        self, topic: Literal[Topic.SnapshotCreated], event: SnapshotCreated
    ): ...

    async def publish(self, topic: Topic, event: dict):
        data = bytes(dumps(event), "utf-8")
        message_id: str = await wrap_future(self._pubsub.publish(str(topic), data))
        return message_id
