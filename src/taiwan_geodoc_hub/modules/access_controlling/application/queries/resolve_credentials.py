from operator import itemgetter
from injector import inject
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driven.credential_repository import (
    CredentialRepository,
)
from taiwan_geodoc_hub.modules.access_controlling.dtos.credentials import (
    Credentials,
)
from taiwan_geodoc_hub.infrastructure.clients.http.google_securetoken_api import (
    GoogleSecureTokenApi,
)
from taiwan_geodoc_hub.modules.access_controlling.domain.services.is_token_valid import (
    is_token_valid,
)
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driving.login_port import (
    LoginPort,
)


class ResolveCredentials:
    _google_secure_token_api: GoogleSecureTokenApi
    _credential_repository: CredentialRepository
    _login: LoginPort

    @inject
    def __init__(
        self,
        /,
        google_secure_token_api: GoogleSecureTokenApi,
        credential_repository: CredentialRepository,
        login: LoginPort,
    ):
        self._google_secure_token_api = google_secure_token_api
        self._credential_repository = credential_repository
        self._login = login

    async def __call__(self) -> Credentials:
        existing_one = await self._credential_repository.load()
        if existing_one:
            id_token, refresh_token = itemgetter("idToken", "refreshToken")(
                existing_one
            )
            if is_token_valid(id_token):
                return existing_one
            refreshed_one = await self._google_secure_token_api.refresh_token(
                refresh_token
            )
            if refreshed_one:
                await self._credential_repository.save(refreshed_one)
                return refreshed_one
        new_one = await self._login()
        if new_one:
            await self._credential_repository.save(new_one)
        return new_one
