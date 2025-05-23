from injector import inject
from taiwan_geodoc_hub.modules.registration_managing.domain.services.validate_snapshot import (
    validate_snapshot,
)
from google.cloud.firestore import AsyncClient, AsyncTransaction, async_transactional
from taiwan_geodoc_hub.infrastructure.adapters.firestore.ocr_result_adapter import (
    OCRResultAdapter as OCRResultAdapter,
)
from taiwan_geodoc_hub.infrastructure.adapters.firestore.registration_adapter import (
    RegistrationAdapter as RegistrationAdapter,
)
from logging import Logger
from taiwan_geodoc_hub.modules.registration_managing.domain.services.rip_text import (
    RipText,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.services.split_registrations import (
    SplitRegistrations,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.registration_repository import (
    RegistrationRepository,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.snapshot_repository import (
    SnapshotRepository,
)
from taiwan_geodoc_hub.modules.registration_managing.dtos.snapshot import (
    Snapshot,
)
from taiwan_geodoc_hub.infrastructure.constants.tokens import (
    UserId,
    TenantId,
    SnapshotId,
)
from time import perf_counter
from taiwan_geodoc_hub.infrastructure.adapters.pubsub.event_publisher import (
    EventPublisher,
)
from taiwan_geodoc_hub.infrastructure.types.topic import Topic
from taiwan_geodoc_hub.modules.registration_managing.events.snapshot_created import (
    SnapshotCreated,
)


class UploadPDF:
    _db: AsyncClient
    _split_registrations: SplitRegistrations
    _rip_text: RipText
    _registration_repository: RegistrationRepository
    _snapshot_repository: SnapshotRepository
    _event_publisher: EventPublisher
    _logger: Logger
    _user_id: str
    _tenant_id: str
    _snapshot_id: str

    @inject
    def __init__(
        self,
        /,
        db: AsyncClient,
        split_registrations: SplitRegistrations,
        rip_text: RipText,
        registration_repository: RegistrationRepository,
        snapshot_repository: SnapshotRepository,
        event_publisher: EventPublisher,
        logger: Logger,
        user_id: UserId,
        tenant_id: TenantId,
        snapshot_id: SnapshotId,
    ):
        self._db = db
        self._split_registrations = split_registrations
        self._rip_text = rip_text
        self._registration_repository = registration_repository
        self._snapshot_repository = snapshot_repository
        self._event_publisher = event_publisher
        self._logger = logger
        self._user_id = user_id
        self._tenant_id = tenant_id
        self._snapshot_id = snapshot_id

    async def __call__(
        self,
        name: str,
        pdf: bytes,
    ):
        start = perf_counter()
        try:
            validate_snapshot(pdf)

            @async_transactional
            async def run_in_transaction(transaction: AsyncTransaction):
                existing = await self._snapshot_repository.exists(
                    self._snapshot_id,
                    uow=transaction,
                )
                await self._snapshot_repository.save(
                    self._snapshot_id,
                    Snapshot(
                        id=self._snapshot_id,
                    ),
                    uow=transaction,
                )
                message_id = await self._event_publisher.publish(
                    Topic.SnapshotCreated,
                    SnapshotCreated(
                        userId=self._user_id,
                        tenantId=self._tenant_id,
                        snapshotId=self._snapshot_id,
                        name=name,
                    ),
                )
                if existing:
                    return message_id
                full_text = await self._rip_text(pdf=pdf)
                for registration in self._split_registrations(full_text):
                    await self._registration_repository.save(
                        registration.get("id"),
                        registration,
                        uow=transaction,
                    )
                return message_id

            message_id = await run_in_transaction(self._db.transaction())
            self._logger.info(
                "UploadPDF finished", extra=dict(elapsed=perf_counter() - start)
            )
            return message_id
        except Exception:
            self._logger.exception(
                "UploadPDF failed",
            )
            raise
