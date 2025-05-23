from injector import Injector
from time import tzset
from taiwan_geodoc_hub.utils.firebase.setup_firebase import (
    setup_firebase,
)
from taiwan_geodoc_hub.utils.logging.setup_logging import setup_logging
from .context import context  # noqa: F401


async def startup():
    global context
    tzset()
    setup_firebase()
    setup_logging()
    from taiwan_geodoc_hub.modules.general import (
        general_module,
    )
    from taiwan_geodoc_hub.modules.access_controlling import (
        access_controlling_module,
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
            access_controlling_module,
            registration_managing_module,
            auditing_module,
        ]
    )
    context["injector"] = injector
    return injector
