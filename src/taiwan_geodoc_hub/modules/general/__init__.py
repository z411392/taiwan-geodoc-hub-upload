from injector import Module, InstanceProvider, ClassProvider, Provider, CallableProvider
from google.cloud.firestore import AsyncClient
from firebase_admin.firestore_async import client
from taiwan_geodoc_hub.infrastructure.clients.pubsub.event_publisher import (
    EventPublisher,
)
from google.cloud.pubsub import PublisherClient
from taiwan_geodoc_hub.modules.general.domain.ports.driven.process_state_repository import (
    ProcessStateRepository,
)
from taiwan_geodoc_hub.adapters.firestore.process_state_firestore_adapter import (
    ProcessStateFirestoreAdapter,
)
from taiwan_geodoc_hub.infrastructure.hashers.bytes_hasher import BytesHasher
from taiwan_geodoc_hub.infrastructure.generators.trace_id_generator import (
    TraceIdGenerator,
)
from typing import Optional
from logging import Logger, LoggerAdapter, getLogger
from taiwan_geodoc_hub.modules.general.constants.tokens import (
    TraceId,
    UserId,
    TenantId,
)
from httpx import AsyncClient as HttpConnectionPool
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
    UnitOfWork,
)
from taiwan_geodoc_hub.infrastructure.transactions.firestore_unit_of_work import (
    FirestoreUnitOfWork,
)
from taiwan_geodoc_hub.infrastructure.hashers.hmac_signer import HMACSigner
from taiwan_geodoc_hub.utils.google_cloud.credentials_from_env import (
    credentials_from_env,
)
from os import getenv
from taiwan_geodoc_hub.modules.general.domain.ports.driven.wait_for_process_completion import (
    WaitForProcessCompletionPort,
)


class LoggerProvider(Provider[Logger]):
    def get(self, injector):
        trace_id: Optional[str] = None
        user_id: Optional[str] = None
        tenant_id: Optional[str] = None
        try:
            trace_id = injector.get(TraceId)
            user_id = injector.get(UserId)
            tenant_id = injector.get(TenantId)
        except Exception:
            pass
        logger = LoggerAdapter(
            getLogger(trace_id),
            dict(
                userId=user_id,
                tenantId=tenant_id,
            ),
        )
        return logger


pubsub: Optional[PublisherClient] = None


def provide_pubsub():
    global pubsub
    if pubsub is None:
        pubsub = PublisherClient(credentials=credentials_from_env())
    return pubsub


class GeneralModule(Module):
    def configure(self, binder):
        binder.bind(
            Logger,
            to=LoggerProvider(),
        )
        binder.bind(AsyncClient, to=InstanceProvider(client()))
        binder.bind(PublisherClient, to=CallableProvider(provide_pubsub))
        binder.bind(EventPublisher, to=ClassProvider(EventPublisher))
        binder.bind(TraceIdGenerator, to=ClassProvider(TraceIdGenerator))
        binder.bind(BytesHasher, to=ClassProvider(BytesHasher))
        binder.bind(HttpConnectionPool, to=InstanceProvider(HttpConnectionPool()))
        binder.bind(
            ProcessStateRepository, to=ClassProvider(ProcessStateFirestoreAdapter)
        )
        binder.bind(UnitOfWork, to=ClassProvider(FirestoreUnitOfWork))
        binder.bind(
            HMACSigner, to=InstanceProvider(HMACSigner(getenv("HMAC_SIGNING_KEY")))
        )
        binder.bind(
            WaitForProcessCompletionPort, to=ClassProvider(ProcessStateFirestoreAdapter)
        )


general_module = GeneralModule()
