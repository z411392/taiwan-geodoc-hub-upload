from enum import Enum


class Collection(str, Enum):
    ocrResults = "ocrResults"
    tenants = "tenants"
    roles = "tenants/:tenantId/roles"
    snapshots = "snapshots"
    registrations = "snapshots/:snapshotId/registrations"

    def __str__(self):
        return self.value
