from typing import TypedDict


class SnapshotCreated(TypedDict):
    userId: str
    tenantId: str
    snapshotId: str
    name: str
