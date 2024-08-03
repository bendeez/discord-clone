import pytest
import httpx
from utils import http_request, RequestMethod
from app.app import app
from app.database import SessionLocal, engine
from app.base import BaseMixin
from app.user.service import create_new_user, delete_current_user
from app.core.oauth import create_access_token, get_websocket_user
from app.websocket_server.websocket_managers.CentralWebsocketServerInterface import (
    central_ws_interface,
)
from unittest.mock import AsyncMock
from uuid import uuid4
import asyncio


@pytest.fixture(autouse=True)
async def startup():
    await central_ws_interface.initialize_pubsub()


@pytest.fixture(name="db", scope="session", autouse=True)
async def create_db_session():
    async with SessionLocal() as db:
        yield db


@pytest.fixture(scope="session", autouse=True)
async def create_tables(db):
    async with engine.begin() as conn:
        await conn.run_sync(BaseMixin.metadata.drop_all)
        await conn.run_sync(BaseMixin.metadata.create_all)


@pytest.fixture()
async def current_user(db):
    user = await create_new_user(
        db=db, email="current_user@gmail.com", username="current_user", password="1234"
    )
    user.password = "1234"  # unhash the hashed password
    yield user
    """
        user entities will be deleted
        due to foreign key constraint
    """
    await delete_current_user(db=db, user=user)


@pytest.fixture()
def current_user_token(current_user):
    return create_access_token(data={"username": current_user.username})


@pytest.fixture()
async def remote_user(db):
    remote_users = []

    async def _remote_user():
        remote_username = str(uuid4())
        remote_user = await create_new_user(
            email=f"{remote_username}@gmail.com",
            username=remote_username,
            password="1234",
            db=db,
        )
        remote_users.append(remote_user)
        token = create_access_token(data={"username": remote_user.username})
        return remote_user, token

    yield _remote_user

    for remote_user in remote_users:
        """
            user entities will be deleted
            due to foreign key constraint
        """
        await db.delete(remote_user)
    await db.commit()


@pytest.fixture(scope="session", name="client", autouse=True)
async def create_web_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://127.0.0.1:8000"
    ) as client:
        yield client


@pytest.fixture(name="http_request")
async def make_http_request(client):
    async def _make_http_request(
        path, client=client, method=RequestMethod.GET, json=None, files=None, token=None
    ):
        data = await http_request(
            client=client, path=path, method=method, json=json, files=files, token=token
        )
        return data

    return _make_http_request


@pytest.fixture()
async def websocket_connection(startup, db):
    message_inbox: dict[str, asyncio.Queue] = {}

    async def _websocket_connection(token: str):
        websocket = AsyncMock()
        websocket.path_params = {"token": token}
        current_user = await get_websocket_user(websocket=websocket, db=db)
        message_inbox[current_user["username"]] = asyncio.Queue()

        async def send_message(data):
            await message_inbox[current_user["username"]].put(data)

        async def receive_message():
            return await message_inbox[current_user["username"]].get()

        websocket.send_json.side_effect = send_message
        websocket.recv.side_effect = receive_message

        await central_ws_interface.connect(
            websocket=websocket, current_user=current_user, db=db
        )

        return websocket, current_user

    yield _websocket_connection

    for connection in central_ws_interface.server_manager.active_connections:
        await central_ws_interface.disconnect(current_user=connection, db=db)


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"
