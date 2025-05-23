from typing import TypedDict
from taiwan_geodoc_hub.modules.registration_managing.types.registration_type import (
    RegistrationType,
)
from taiwan_geodoc_hub.modules.registration_managing.types.registration_status import (
    RegistrationStatus,
)


class Registration(TypedDict):
    id: str
    type: RegistrationType
    text: str
    status: RegistrationStatus
    userId: str
