from enum import Enum


class Collection(str, Enum):
    OCRResults = "ocrResults"
    Tenants = "tenants"
    Roles = "tenants/:tenantId/roles"
    Snapshots = "snapshots"
    Registrations = "snapshots/:snapshotId/registrations"
    TenantDailyUsage = "stats/usage/tenants/:tenantId/daily"
    Processes = "users/:userId/processes"
    TenantSnapshotOwnerships = "tenants/:tenantId/snapshots"

    def __str__(self):
        return self.value
