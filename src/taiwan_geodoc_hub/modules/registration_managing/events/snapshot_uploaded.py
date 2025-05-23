from typing import TypedDict


class SnapshotUploaded(TypedDict):
    userId: str
    tenantId: str
    snapshotId: str
    name: str
