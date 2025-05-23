from typing import TypedDict, Dict


class TenantSnapshotOwnership(TypedDict):
    id: str
    name: str
    registrations: Dict[str, bool]
