from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Coroutine, Optional
from taiwan_geodoc_hub.modules.access_controlling.application.queries.resolve_user import (
    ResolveUser,
)
from injector import InstanceProvider, Injector
from taiwan_geodoc_hub.modules.access_controlling.exceptions.unauthorized import (
    Unauthorized,
)
from taiwan_geodoc_hub.modules.general.constants.tokens import UserId
from re import split, IGNORECASE
from firebase_admin.auth import UserRecord


def with_resolve_user(enforce: bool):
    class Middleware(BaseHTTPMiddleware):
        def _extract_id_token(self, authorization: Optional[str]):
            if authorization is None:
                return None
            segments = split(r"bearer\s+", authorization, flags=IGNORECASE)
            if len(segments) < 2:
                return None
            _, token = segments
            if token is None:
                return None
            stripped = str.strip(token)
            return stripped

        async def dispatch(
            self,
            request: Request,
            call_next: Callable[[Request], Coroutine[None, None, Response]],
        ):
            injector: Injector = request.scope["injector"]
            id_token = self._extract_id_token(request.headers.get("Authorization"))
            user: Optional[UserRecord] = None
            if id_token:
                handler = injector.get(ResolveUser)
                user = await handler(id_token)
            if user is None and enforce:
                raise Unauthorized()
            if user:
                request.scope["user"] = user
                injector.binder.bind(UserId, to=InstanceProvider(user.uid))
            return await call_next(request)

    return Middleware
