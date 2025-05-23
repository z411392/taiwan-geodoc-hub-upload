from httpx import AsyncClient as HttpConnectionPool
from taiwan_geodoc_hub.utils.firebase.dispose_firebase import dispose_firebase
from .injector import injector  # noqa: F401


async def shutdown():
    global injector
    if not injector:
        return
    try:
        httpx = injector.get(HttpConnectionPool)
        if httpx:
            await httpx.aclose()
    except Exception:
        pass
    dispose_firebase()
    injector = None
