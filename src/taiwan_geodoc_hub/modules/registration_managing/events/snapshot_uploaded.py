from typing import TypedDict


class SnapshotUploaded(TypedDict):
    id: str
    userId: str
    tenantId: str
    snapshotId: str
