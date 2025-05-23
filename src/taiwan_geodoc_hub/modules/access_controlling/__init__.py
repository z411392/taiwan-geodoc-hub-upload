from injector import Module, ClassProvider
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.get_user_from_id_token_port import (
    GetUserFromIdTokenPort,
)
from taiwan_geodoc_hub.adapters.auth.user_auth_adapter import UserAuthAdapter
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.get_tenant_by_id_port import (
    GetTenantByIdPort,
)
from taiwan_geodoc_hub.adapters.firestore.tenant_firestore_adapter import (
    TenantFirestoreAdapter,
)
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.get_role_by_id_port import (
    GetRoleByIdPort,
)
from taiwan_geodoc_hub.adapters.firestore.role_firestore_adapter import (
    RoleFirestoreAdapter,
)
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.credential_repository import (
    CredentialRepository,
)
from taiwan_geodoc_hub.adapters.file_system.credential_file_system_adapter import (
    CredentialFileSystemAdapter,
)
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.tenant_snapshot_ownership_repository import (
    TenantSnapshotOwnershipRepository,
)
from taiwan_geodoc_hub.adapters.firestore.tenant_snapshot_ownership_firestore_adapter import (
    TenantSnapshotOwnershipFirestoreAdapter,
)
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driving.login_port import (
    LoginPort,
)
from taiwan_geodoc_hub.modules.access_controlling.application.commands.login import (
    Login,
)


class AccessManagingModule(Module):
    def configure(self, binder):
        binder.bind(GetUserFromIdTokenPort, to=ClassProvider(UserAuthAdapter))
        binder.bind(GetTenantByIdPort, to=ClassProvider(TenantFirestoreAdapter))
        binder.bind(GetRoleByIdPort, to=ClassProvider(RoleFirestoreAdapter))
        binder.bind(CredentialRepository, to=ClassProvider(CredentialFileSystemAdapter))
        binder.bind(LoginPort, to=ClassProvider(Login))
        binder.bind(
            TenantSnapshotOwnershipRepository,
            to=ClassProvider(TenantSnapshotOwnershipFirestoreAdapter),
        )


access_controlling_module = AccessManagingModule()
