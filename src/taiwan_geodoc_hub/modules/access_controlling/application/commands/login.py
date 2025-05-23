from injector import inject
from taiwan_geodoc_hub.modules.access_controlling.domain.ports.driving.login_port import (
    LoginPort,
)
from os import getenv
from json import dumps
from typing import List, Any
from starlette.routing import Route
from starlette.responses import HTMLResponse
from taiwan_geodoc_hub.utils.starlette.launch_server import launch_server
from taiwan_geodoc_hub.utils.playwright.launch_playwright import launch_playwright
from asyncio import get_running_loop, gather, wait_for
from taiwan_geodoc_hub.modules.access_controlling.dtos.credentials import (
    Credentials,
)


class Login(LoginPort):
    @inject
    def __init__(self):
        pass

    def _redner_login_page(self):
        firebase_config = dumps(
            dict(
                apiKey=getenv("API_KEY"),
                authDomain=getenv("AUTH_DOMAIN"),
                projectId=getenv("PROJECT_ID"),
                storageBucket=getenv("STORAGE_BUCKET"),
                messagingSenderId=getenv("MESSAGING_SENDER_ID"),
                appId=getenv("APP_ID"),
                measurementId=getenv("MEASUREMENT_ID"),
            )
        )
        return f"""
        <!DOCTYPE html>
            <html>
            <head>
              <title>Login</title>
              <meta name="viewport" content="width=device-width, initial-scale=1">
              <style>
                html, body {{
                  height: 100%;
                  margin: 0;
                }}
              </style>
              <script src="https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js"></script>
              <script src="https://www.gstatic.com/firebasejs/10.12.0/firebase-auth-compat.js"></script>
            </head>
            <body>
              <script type="module">
                try {{
                  firebase.initializeApp({firebase_config})
                  const {{ user }} = await firebase.auth().signInWithPopup(new firebase.auth.GoogleAuthProvider())
                  const idToken = await user.getIdToken()
                  const refreshToken = user.refreshToken
                  resolve({{ idToken, refreshToken }})
                }} catch (thrown) {{
                  reject(thrown instanceof Error ? thrown.message : String(thrown))
                }}
              </script>
            </body>
            </html>
        """.strip()

    URI = "/auth/sign-in"

    async def __call__(self):
        routes: List[Route] = [
            Route(
                self.URI,
                lambda request: HTMLResponse(self._redner_login_page()),
            )
        ]
        async with launch_server(routes) as endpoint:
            async with launch_playwright() as page:
                future = get_running_loop().create_future()

                def resolve(credentials_data: dict):
                    nonlocal future
                    if not future.done():
                        future.set_result(Credentials(**credentials_data))

                def reject(error: str):
                    nonlocal future
                    if not future.done():
                        future.set_exception(Exception(error))

                def on_error(error: Any):
                    reject(str(error))

                def on_close():
                    reject("Playwright closed")

                page.on("pageerror", on_error)
                page.on("close", on_close)
                await page.expose_function("resolve", resolve)
                await page.expose_function("reject", reject)
                await page.goto(f"{endpoint}{self.URI}")
                credentials = await wait_for(future, timeout=300)
                return credentials
