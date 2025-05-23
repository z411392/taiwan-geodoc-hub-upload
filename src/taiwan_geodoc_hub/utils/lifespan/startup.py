from injector import Injector
from google.cloud.pubsub import PublisherClient
from time import tzset
from taiwan_geodoc_hub.utils.firebase.boot_firebase import (
    boot_firebase,
)
from taiwan_geodoc_hub.utils.firebase.ensure_topics import ensure_topics
from taiwan_geodoc_hub.utils.logging.setup_logging import setup_logging
from taiwan_geodoc_hub.utils.environments import is_cli
from .injector import injector  # noqa: F401


async def startup():
    global injector
    tzset()
    boot_firebase()
    setup_logging()
    from taiwan_geodoc_hub.modules.system_maintaining import (
        system_maintaining_module,
    )
    from taiwan_geodoc_hub.modules.access_managing import (
        access_managing_module,
    )
    from taiwan_geodoc_hub.modules.registration_managing import (
        registration_managing_module,
    )

    injector = Injector(
        [
            system_maintaining_module,
            access_managing_module,
            registration_managing_module,
        ]
    )
    if not is_cli():
        await ensure_topics(injector.get(PublisherClient))
    return injector
