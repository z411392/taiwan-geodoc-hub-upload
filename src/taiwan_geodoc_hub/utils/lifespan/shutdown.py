from httpx import AsyncClient as HttpConnectionPool
from taiwan_geodoc_hub.utils.firebase.dispose_firebase import dispose_firebase
from .context import context  # noqa: F401


async def shutdown():
    global context
    if not context["injector"]:
        return
    try:
        httpx = context["injector"].get(HttpConnectionPool)
        if httpx:
            await httpx.aclose()
    except Exception:
        pass
    dispose_firebase()
    context["injector"] = None
