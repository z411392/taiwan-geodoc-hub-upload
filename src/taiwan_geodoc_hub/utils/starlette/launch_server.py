from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware
from uvicorn import Config, Server
from contextlib import asynccontextmanager
from asyncio import create_task, CancelledError
from socket import socket as Socket
from typing import List


@asynccontextmanager
async def launch_server(
    routes: List[Route],
    *,
    host: str = "localhost",
    port: int = 3000,
):
    starlette = Starlette(
        debug=False,
        routes=routes,
    )
    starlette.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    server = Server(
        Config(
            app=starlette,
            lifespan="off",
            host=host,
            port=port,
            log_level="error",
        )
    )
    server_task = create_task(server.serve())
    try:
        yield f"http://{host}:{port}"
    finally:
        server.should_exit = True
        try:
            server_task.cancel()
            await server_task
        except CancelledError:
            pass
