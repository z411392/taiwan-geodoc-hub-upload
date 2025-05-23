import pytest
from injector import Injector
from taiwan_geodoc_hub.infrastructure.clients.pubsub.event_publisher import (
    EventPublisher,
)
from taiwan_geodoc_hub.modules.general.enums.topic import Topic
from taiwan_geodoc_hub.modules.registration_managing.events.snapshot_uploaded import (
    SnapshotUploaded,
)
from os import getenv
from taiwan_geodoc_hub.infrastructure.generators.trace_id_generator import (
    TraceIdGenerator,
)


# @pytest.mark.skip(reason="")
class TestEventPublisher:
    @pytest.fixture
    def event_publisher(self, injector: Injector):
        return injector.get(EventPublisher)

    @pytest.fixture
    def next_trace_id(self, injector: Injector):
        return injector.get(TraceIdGenerator)

    @pytest.mark.describe("要能夠發布事件")
    @pytest.mark.asyncio
    async def test_publish_event(
        self,
        event_publisher: EventPublisher,
        next_trace_id: TraceIdGenerator,
    ):
        trace_id = next_trace_id()
        user_id = getenv("USER_ID")
        tenant_id = getenv("TENANT_ID")
        snapshot_id = getenv("SNAPSHOT_ID")
        await event_publisher.publish(
            Topic.SnapshotUploaded,
            SnapshotUploaded(
                id=trace_id,
                userId=user_id,
                tenantId=tenant_id,
                snapshotId=snapshot_id,
            ),
        )
        assert trace_id is not None
