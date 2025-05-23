from injector import inject
from google.cloud.pubsub import PublisherClient
from asyncio import wrap_future
from taiwan_geodoc_hub.modules.general.enums.topic import Topic
from json import dumps
from taiwan_geodoc_hub.infrastructure.hashers.hmac_signer import HMACSigner


class EventPublisher:
    _pubsub: PublisherClient
    _compute_hmac: HMACSigner

    @inject
    def __init__(
        self,
        /,
        pubsub: PublisherClient,
        compute_hmac: HMACSigner,
    ):
        self._pubsub = pubsub
        self._compute_hmac = compute_hmac

    async def publish(self, topic: Topic, payload: dict):
        data = bytes(dumps(payload), "utf-8")
        signature = self._compute_hmac(data)
        attrs = {
            "X-Signature": signature,
        }
        await wrap_future(self._pubsub.publish(str(topic), data, **attrs))
        return signature
