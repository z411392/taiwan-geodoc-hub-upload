from injector import inject, Injector, InstanceProvider
from taiwan_geodoc_hub.modules.registration_managing.domain.services.pdf_validator import (
    PDFValidator,
)
from logging import Logger
from taiwan_geodoc_hub.modules.registration_managing.domain.services.registration_splitter import (
    RegistrationSplitter,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.registration_repository import (
    RegistrationRepository,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.snapshot_repository import (
    SnapshotRepository,
)
from taiwan_geodoc_hub.modules.general.constants.tokens import (
    TraceId,
    UserId,
    TenantId,
    SnapshotId,
)
from time import perf_counter
from taiwan_geodoc_hub.infrastructure.clients.pubsub.event_publisher import (
    EventPublisher,
)
from taiwan_geodoc_hub.modules.general.enums.topic import Topic
from taiwan_geodoc_hub.modules.registration_managing.events.snapshot_uploaded import (
    SnapshotUploaded,
)
from taiwan_geodoc_hub.modules.auditing.domain.ports.driven.tenant_daily_usage_repository import (
    TenantDailyUsageRepository,
)
from taiwan_geodoc_hub.modules.auditing.dtos.tenant_daily_usage import (
    TenantDailyUsage,
)
from datetime import datetime
from taiwan_geodoc_hub.modules.general.domain.ports.driven.unit_of_work import (
    UnitOfWork,
)
from prefect import flow, task
from prefect.cache_policies import NO_CACHE
from taiwan_geodoc_hub.infrastructure.hashers.bytes_hasher import BytesHasher
from taiwan_geodoc_hub.modules.registration_managing.domain.services.tenant_daily_usage_checker import (
    TenantDailyUsageChecker,
)
from taiwan_geodoc_hub.modules.general.domain.ports.driven.process_state_repository import (
    ProcessStateRepository,
)
from taiwan_geodoc_hub.modules.general.dtos.process_state import Pending
from taiwan_geodoc_hub.modules.general.enums.process_status import (
    ProcessStatus,
)
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.tenant_snapshot_ownership_repository import (
    TenantSnapshotOwnershipRepository,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driven.get_registration_ids_port import (
    GetRegistrationIdsPort,
)
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.tenant_snapshot_ownership_repository import (
    TenantSnapshotOwnership,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.driving.extract_text_port import (
    ExtractTextPort,
)


class UploadPDF:
    _extract_text: ExtractTextPort
    _snapshot_repository: SnapshotRepository
    _event_publisher: EventPublisher
    _logger: Logger
    _user_id: str
    _tenant_id: str
    _validate_pdf: PDFValidator
    _tenant_daily_usage_repository: TenantDailyUsageRepository
    _unit_of_work: UnitOfWork
    _bytes_hasher: BytesHasher
    _injector: Injector
    _check_tenant_daily_usage: TenantDailyUsageChecker
    _process_state_repository: ProcessStateRepository
    _trace_id: str
    _tenant_snapshot_ownership_repository: TenantSnapshotOwnershipRepository
    _get_registration_ids_port: GetRegistrationIdsPort

    @inject
    def __init__(
        self,
        /,
        extract_text: ExtractTextPort,
        snapshot_repository: SnapshotRepository,
        tenant_daily_usage_repository: TenantDailyUsageRepository,
        event_publisher: EventPublisher,
        logger: Logger,
        user_id: UserId,
        tenant_id: TenantId,
        validate_pdf: PDFValidator,
        unit_of_work: UnitOfWork,
        bytes_hasher: BytesHasher,
        injector: Injector,
        check_tenant_daily_usage: TenantDailyUsageChecker,
        process_state_repository: ProcessStateRepository,
        trace_id: TraceId,
        tenant_snapshot_ownership_repository: TenantSnapshotOwnershipRepository,
        get_registration_ids_port: GetRegistrationIdsPort,
    ):
        self._extract_text = extract_text
        self._snapshot_repository = snapshot_repository
        self._tenant_daily_usage_repository = tenant_daily_usage_repository
        self._event_publisher = event_publisher
        self._logger = logger
        self._user_id = user_id
        self._tenant_id = tenant_id
        self._validate_pdf = validate_pdf
        self._unit_of_work = unit_of_work
        self._bytes_hasher = bytes_hasher
        self._injector = injector
        self._check_tenant_daily_usage = check_tenant_daily_usage
        self._process_state_repository = process_state_repository
        self._trace_id = trace_id
        self._tenant_snapshot_ownership_repository = (
            tenant_snapshot_ownership_repository
        )
        self._get_registration_ids_port = get_registration_ids_port

    @task(name="Update Service Usage", cache_policy=NO_CACHE)
    async def _track_daily_upload_usage(
        self,
        date: str,
        tenant_daily_usage: TenantDailyUsage,
        /,
        unit_of_work: UnitOfWork,
    ):
        tenant_daily_usage["snapshots"] += 1
        await self._tenant_daily_usage_repository.save(
            date,
            tenant_daily_usage,
            unit_of_work=unit_of_work,
        )

    async def _check_snapshot_exists(
        self,
        snapshot_id: str,
        /,
        unit_of_work: UnitOfWork,
    ):
        snapshot_exists = await self._snapshot_repository.exists(
            snapshot_id,
            unit_of_work=unit_of_work,
        )
        return snapshot_exists

    @task(name="Parse PDF", cache_policy=NO_CACHE)
    async def _parse_pdf(
        self,
        pdf: bytes,
        snapshot_id: str,
        /,
        unit_of_work: UnitOfWork,
    ):
        full_text = await self._extract_text(pdf=pdf)
        child = self._injector.create_child_injector()
        child.binder.bind(SnapshotId, to=InstanceProvider(snapshot_id))
        registration_repository = child.get(RegistrationRepository)
        split_registrations = child.get(RegistrationSplitter)
        async for registration in split_registrations(full_text):
            await registration_repository.save(
                registration.get("id"),
                registration,
                unit_of_work=unit_of_work,
            )

    @task(name="Parse and Save Transcript If Not Exists", cache_policy=NO_CACHE)
    async def _create_snapshot_if_not_exists(
        self,
        pdf: bytes,
        snapshot_id: str,
        /,
        unit_of_work: UnitOfWork,
    ):
        snapshot_exists = await self._check_snapshot_exists(
            snapshot_id,
            unit_of_work=unit_of_work,
        )

        if snapshot_exists:
            return

        await self._parse_pdf(pdf, snapshot_id, unit_of_work=unit_of_work)

    @task(name="Validate Daily Upload Limit", cache_policy=NO_CACHE)
    async def _validate_tenant_daily_usage(
        self,
        date: str,
        /,
        unit_of_work: UnitOfWork,
    ):
        tenant_daily_usage = await self._tenant_daily_usage_repository.load(
            date,
            unit_of_work=unit_of_work,
        )
        if tenant_daily_usage is None:
            tenant_daily_usage = TenantDailyUsage(
                id=date,
                snapshots=0,
            )
        self._check_tenant_daily_usage(tenant_daily_usage)
        return tenant_daily_usage

    @task(name="Update Ownerships", cache_policy=NO_CACHE)
    async def _update_ownerships(
        self,
        snapshot_id: str,
        tenant_snapshot_ownership: TenantSnapshotOwnership,
        /,
        unit_of_work: UnitOfWork,
    ):
        registrations = tenant_snapshot_ownership["registrations"]
        registration_ids = await self._get_registration_ids_port.registration_ids(
            snapshot_id
        )
        for registration_id in registration_ids:
            if registration_id not in registrations:
                registrations[registration_id] = False
        tenant_snapshot_ownership["registrations"] = registrations
        await self._tenant_snapshot_ownership_repository.save(
            snapshot_id,
            tenant_snapshot_ownership,
            unit_of_work=unit_of_work,
        )

    @flow(name="Upload PDF", cache_result_in_memory=False)
    async def __call__(
        self,
        name: str,
        pdf: bytes,
    ):
        start = perf_counter()
        snapshot_id = self._bytes_hasher(pdf)
        try:
            self._validate_pdf(pdf)
            async with self._unit_of_work as unit_of_work:
                date = datetime.now().strftime("%Y-%m-%d")
                tenant_daily_usage = await self._validate_tenant_daily_usage(
                    date,
                    unit_of_work=unit_of_work,
                )
                tenant_snapshot_ownership = (
                    await self._tenant_snapshot_ownership_repository.load(
                        snapshot_id, unit_of_work=unit_of_work
                    )
                )
                if tenant_snapshot_ownership is None:
                    tenant_snapshot_ownership = TenantSnapshotOwnership(
                        id=snapshot_id,
                        name=name,
                        registrations=dict(),
                    )
                await self._create_snapshot_if_not_exists(
                    pdf,
                    snapshot_id,
                    unit_of_work=unit_of_work,
                )
                await self._track_daily_upload_usage(
                    date,
                    tenant_daily_usage,
                    unit_of_work=unit_of_work,
                )
                await self._process_state_repository.save(
                    self._trace_id,
                    Pending(
                        id=self._trace_id,
                        status=ProcessStatus.Pending,
                    ),
                    unit_of_work=unit_of_work,
                )
                await self._update_ownerships(
                    snapshot_id,
                    tenant_snapshot_ownership,
                    unit_of_work=unit_of_work,
                )
                await self._event_publisher.publish(
                    Topic.SnapshotUploaded,
                    SnapshotUploaded(
                        id=self._trace_id,
                        userId=self._user_id,
                        tenantId=self._tenant_id,
                        snapshotId=snapshot_id,
                    ),
                )
                self._logger.info(
                    "UploadPDF finished", extra=dict(elapsed=perf_counter() - start)
                )
                return snapshot_id
        except Exception:
            self._logger.exception(
                "UploadPDF failed",
            )
            raise
