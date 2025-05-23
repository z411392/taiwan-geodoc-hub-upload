from typing import TypedDict
from taiwan_geodoc_hub.modules.access_controlling.enums.role_type import RoleType


class Role(TypedDict):
    id: str
    type: RoleType
    status: str
