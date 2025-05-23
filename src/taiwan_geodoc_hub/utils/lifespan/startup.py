from injector import Injector
from google.cloud.pubsub import PublisherClient
from time import tzset
from taiwan_geodoc_hub.utils.firebase.boot_firebase import (
    boot_firebase,
)
from taiwan_geodoc_hub.utils.firebase.ensure_topics import ensure_topics
from taiwan_geodoc_hub.utils.logging.setup_logging import setup_logging
from taiwan_geodoc_hub.utils.environments import is_cli
from .context import context  # noqa: F401


async def startup():
    global context
    tzset()
    boot_firebase()
    setup_logging()
    from taiwan_geodoc_hub.modules.general import (
        general_module,
    )
    from taiwan_geodoc_hub.modules.access_managing import (
        access_managing_module,
    )
    from taiwan_geodoc_hub.modules.registration_managing import (
        registration_managing_module,
    )
    from taiwan_geodoc_hub.modules.auditing import (
        auditing_module,
    )

    injector = Injector(
        [
            general_module,
            access_managing_module,
            registration_managing_module,
            auditing_module,
        ]
    )
    if not is_cli():
        await ensure_topics(injector.get(PublisherClient))
    context["injector"] = injector
    return injector
