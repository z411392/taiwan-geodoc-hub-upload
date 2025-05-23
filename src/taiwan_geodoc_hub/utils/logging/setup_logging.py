from logging import basicConfig, INFO, WARNING, getLogger, StreamHandler, CRITICAL
from taiwan_geodoc_hub.infrastructure.formatters.cloud_logging_json_formatter import (
    CloudLoggingJSONFormatter,
)


def setup_logging():
    basicConfig(
        level=INFO,
        format="%(message)s",
        handlers=[StreamHandler()],
    )
    root_logger = getLogger()
    for handler in root_logger.handlers:
        handler.setFormatter(CloudLoggingJSONFormatter())
    getLogger("vellox.utils.lifespan").setLevel(WARNING)
    getLogger("vellox.http").setLevel(WARNING)
    getLogger("werkzeug").setLevel(WARNING)
    getLogger("httpx").setLevel(WARNING)
    getLogger("opentelemetry").setLevel(CRITICAL + 1)
    getLogger("prefect").setLevel(CRITICAL + 1)
