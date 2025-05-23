from injector import inject, Injector, InstanceProvider
from taiwan_geodoc_hub.modules.registration_managing.domain.services.pdf_validator import (
    PDFValidator,
)
from logging import Logger
from taiwan_geodoc_hub.modules.registration_managing.domain.services.text_ripper import (
    TextRipper,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.services.registration_splitter import (
    RegistrationSplitter,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.registration_repository import (
    RegistrationRepository,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.snapshot_repository import (
    SnapshotRepository,
)
from taiwan_geodoc_hub.modules.system_maintaining.constants.tokens import (
    UserId,
    TenantId,
    SnapshotId,
)
from time import perf_counter
from taiwan_geodoc_hub.adapters.pubsub.event_publisher import (
    EventPublisher,
)
from taiwan_geodoc_hub.modules.system_maintaining.types.topic import Topic
from taiwan_geodoc_hub.modules.registration_managing.events.snapshot_uploaded import (
    SnapshotUploaded,
)
from taiwan_geodoc_hub.modules.registration_managing.domain.ports.tenant_daily_usage_repository import (
    TenantDailyUsageRepository,
)
from taiwan_geodoc_hub.modules.registration_managing.dtos.tenant_daily_usage import (
    TenantDailyUsage,
)
from datetime import datetime
from taiwan_geodoc_hub.infrastructure.generators.trace_id_generator import (
    TraceIdGenerator,
)
from taiwan_geodoc_hub.infrastructure.transactions.unit_of_work import (
    UnitOfWork,
)
from prefect import flow, task
from prefect.cache_policies import NO_CACHE
from taiwan_geodoc_hub.infrastructure.hashers.bytes_hasher import BytesHasher
from taiwan_geodoc_hub.modules.registration_managing.domain.services.tenant_daily_usage_checker import (
    TenantDailyUsageChecker,
)


class UploadPDF:
    _rip_text: TextRipper
    _snapshot_repository: SnapshotRepository
    _event_publisher: EventPublisher
    _logger: Logger
    _user_id: str
    _tenant_id: str
    _validate_pdf: PDFValidator
    _tenant_daily_usage_repository: TenantDailyUsageRepository
    _next_trace_id: TraceIdGenerator
    _unit_of_work: UnitOfWork
    _bytes_hasher: BytesHasher
    _injector: Injector
    _check_tenant_daily_usage: TenantDailyUsageChecker

    @inject
    def __init__(
        self,
        /,
        rip_text: TextRipper,
        snapshot_repository: SnapshotRepository,
        tenant_daily_usage_repository: TenantDailyUsageRepository,
        event_publisher: EventPublisher,
        logger: Logger,
        user_id: UserId,
        tenant_id: TenantId,
        validate_pdf: PDFValidator,
        nextTraceId: TraceIdGenerator,
        unit_of_work: UnitOfWork,
        bytes_hasher: BytesHasher,
        injector: Injector,
        check_tenant_daily_usage: TenantDailyUsageChecker,
    ):
        self._rip_text = rip_text
        self._snapshot_repository = snapshot_repository
        self._tenant_daily_usage_repository = tenant_daily_usage_repository
        self._event_publisher = event_publisher
        self._logger = logger
        self._user_id = user_id
        self._tenant_id = tenant_id
        self._validate_pdf = validate_pdf
        self._next_trace_id = nextTraceId
        self._unit_of_work = unit_of_work
        self._bytes_hasher = bytes_hasher
        self._injector = injector
        self._check_tenant_daily_usage = check_tenant_daily_usage

    @task(name="更新服務使用情形", cache_policy=NO_CACHE)
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

    @task(name="解析 PDF", cache_policy=NO_CACHE)
    async def _parse_pdf(
        self,
        pdf: bytes,
        snapshot_id: str,
        /,
        unit_of_work: UnitOfWork,
    ):
        full_text = await self._rip_text(pdf=pdf)
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

    @task(name="未曾建檔時解析並儲存謄本", cache_policy=NO_CACHE)
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

    @task(name="檢查是否符合每日上傳限制", cache_policy=NO_CACHE)
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
                trace_id = await self._event_publisher.publish(
                    Topic.SnapshotUploaded,
                    SnapshotUploaded(
                        userId=self._user_id,
                        tenantId=self._tenant_id,
                        snapshotId=snapshot_id,
                        name=name,
                    ),
                )
                self._logger.info(
                    "UploadPDF finished", extra=dict(elapsed=perf_counter() - start)
                )
                return snapshot_id, trace_id
        except Exception:
            self._logger.exception(
                "UploadPDF failed",
            )
            raise
