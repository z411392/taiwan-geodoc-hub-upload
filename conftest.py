import pytest
from base64 import b64decode
from taiwan_geodoc_hub.utils.lifespan import lifespan
from os.path import exists
from json import loads
from operator import itemgetter
from os import environ
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
import jwt
import pytest_asyncio
from asgi_lifespan import LifespanManager
from tracemalloc import start, stop
from injector import Injector
from taiwan_geodoc_hub.infrastructure.generators.trace_id_generator import (
    TraceIdGenerator,
)


@pytest.fixture(autouse=True)
def enable_tracemalloc():
    start()
    yield
    stop()


@pytest.fixture(scope="session", autouse=True)
async def setup_environment_variables():
    if exists("src/.env"):
        load_dotenv("src/.env", override=True)
    if exists("src/.env.local"):
        load_dotenv("src/.env.local", override=True)
    if exists(".env.test"):
        load_dotenv(".env.test", override=True)
    if exists("credentials.json"):
        with open("credentials.json", encoding="utf-8") as file:
            id_token = itemgetter("idToken")(loads(file.read()))
            environ["ID_TOKEN"] = id_token
            decoded_token = jwt.decode(id_token, options=dict(verify_signature=False))
            user_id = decoded_token["user_id"]
            environ["USER_ID"] = user_id


@pytest_asyncio.fixture
async def injector():
    async with lifespan() as injector:
        yield injector


@pytest_asyncio.fixture
async def client():
    from taiwan_geodoc_hub.entrypoints.http.assets import starlette

    async with LifespanManager(starlette) as manager:
        transport = ASGITransport(app=manager.app)
        async with AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            yield client


@pytest.fixture
def sample_image():
    with open("assets/sample_image.dat", encoding="utf-8") as file:
        return b64decode(file.read())


@pytest.fixture
def sample_image_hash():
    with open("assets/sample_image_hash.dat", encoding="utf-8") as file:
        return file.read()


@pytest.fixture
def sample_ocr_result():
    with open("assets/sample_ocr_result.txt", encoding="utf-8") as file:
        return file.read()


@pytest.fixture
def sample_pdf():
    with open("assets/sample_pdf.dat", encoding="utf-8") as file:
        return file.read()


@pytest.fixture
def trace_id(injector: Injector):
    next_trace_id = injector.get(TraceIdGenerator)
    trace_id = next_trace_id()
    return trace_id
