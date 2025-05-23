from prefect import flow, get_run_logger
from taiwan_geodoc_hub.utils.lifespan import startup, shutdown
from traceback import format_exc
from taiwan_geodoc_hub.modules.registration_managing.events.snapshot_uploaded import (
    SnapshotUploaded,
)
from logging import Logger


@flow
async def handle_project_to_ownerships_on_snapshot_uploaded(event: SnapshotUploaded):
    logger = get_run_logger()
    try:
        injector = await startup()
        injector.binder.bind(Logger, logger)
        logger.info(event)
    except Exception:
        logger.error(format_exc())
    finally:
        await shutdown()
