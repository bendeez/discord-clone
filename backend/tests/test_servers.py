import asyncio
from app.servers.schemas import ServerMessagesOut, ServerIn
from app.websocket_server.schemas.server_message import (
    ServerWebsocketText,
    ServerWebsocketAnnouncement,
)
from app.servers.service import create_new_server
from app.services.server_websocket import save_message
from app.redis_client import redis_client
from uuid import uuid4
from utils import RequestMethod
import base64
from datetime import datetime


async def test_create_server(
    http_request, current_user, current_user_token, websocket_connection
):
    await websocket_connection(
        token=current_user_token
    )  # to send the create server message (application does that)
    with open("./tests/programming.jfif", "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode()
    json = {"name": f"{current_user.username} server", "profile": encoded_image}
    response = await http_request(
        "/server", method=RequestMethod.POST, json=json, token=current_user_token
    )
    assert response.status_code == 201
    data = response.json()
    server_id = data["id"]
    assert data["name"] == json["name"]
    assert data["owner"] == current_user.username
    assert data["profile"].startswith("https://firebasestorage.googleapis.com")
    await asyncio.sleep(1)
    response = await http_request(
        f"/servermessages/{server_id}",
        method=RequestMethod.GET,
        json=json,
        token=current_user_token,
    )
    assert response.status_code == 200
    data = response.json()
    del data[0]["date"]
    assert data == [
        ServerMessagesOut(
            **{
                "server": server_id,
                "announcement": f"{current_user.username} has created the server",
                "username": current_user.username,
                "profile": current_user.profile,
                "date": datetime.now(),
            }
        ).model_dump(exclude={"date"})
    ]


async def test_get_servers(http_request, current_user, current_user_token, db):
    server = await create_new_server(
        server=ServerIn(name=f"{current_user.username} server"),
        current_user=current_user,
        db=db,
    )
    response = await http_request(
        "/servers", method=RequestMethod.GET, token=current_user_token
    )
    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            "id": server.id,
            "profile": server.profile,
            "owner": server.owner,
            "name": f"{server.owner} server",
        }
    ]


async def test_get_server_information(
    http_request, current_user, current_user_token, db
):
    server = await create_new_server(
        server=ServerIn(name=f"{current_user.username} server"),
        current_user=current_user,
        db=db,
    )
    response = await http_request(
        f"/server/{server.id}", method=RequestMethod.GET, token=current_user_token
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "id": server.id,
        "profile": server.profile,
        "owner": server.owner,
        "name": f"{server.owner} server",
    }


async def test_get_server_information_forbidden(http_request, current_user_token):
    response = await http_request(
        "/server/77", method=RequestMethod.GET, token=current_user_token
    )
    assert response.status_code == 403


async def test_get_server_users(http_request, current_user, current_user_token, db):
    server = await create_new_server(
        server=ServerIn(name=f"{current_user.username} server"),
        current_user=current_user,
        db=db,
    )
    response = await http_request(
        f"/server/users/{server.id}", method=RequestMethod.GET, token=current_user_token
    )
    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            "username": current_user.username,
            "profile": current_user.profile,
            "status": current_user.status,
        }
    ]


async def test_join_server(
    http_request,
    current_user,
    current_user_token,
    remote_user,
    db,
    websocket_connection,
):
    """
    created the server before initializing the current user websocket connection
    so the current user is authorized to receive and send messages to the server
    """
    server = await create_new_server(
        server=ServerIn(name=f"{current_user.username} server"),
        current_user=current_user,
        db=db,
    )
    remote_user, remote_token = await remote_user()
    current_ws, _ = await websocket_connection(token=current_user_token)
    await websocket_connection(
        token=remote_token
    )  # to send the join server message (application does that)
    link = str(uuid4())
    await redis_client.set(link, server.id)
    response = await http_request(
        "/server/user",
        method=RequestMethod.POST,
        json={"link": link},
        token=remote_token,
    )
    assert response.status_code == 201
    data = response.json()
    assert data == {
        "id": data["id"],
        "username": remote_user.username,
        "server_id": server.id,
    }
    """
        first two are status notifications
    """
    await current_ws.recv()
    await current_ws.recv()
    data = await current_ws.recv()
    del data["date"]
    assert data == ServerWebsocketAnnouncement(
        **{
            "server": server.id,
            "announcement": f"{remote_user.username} has joined the server",
            "username": remote_user.username,
            "profile": remote_user.profile,
        }
    ).model_dump(exclude={"date"})


async def test_invalid_link(http_request, current_user_token):
    response = await http_request(
        "/server/user",
        method=RequestMethod.POST,
        json={"link": "invalidlink"},
        token=current_user_token,
    )
    assert response.status_code == 403


async def test_get_server_messages(http_request, current_user, current_user_token, db):
    server = await create_new_server(
        server=ServerIn(name=f"{current_user.username} server"),
        current_user=current_user,
        db=db,
    )
    server_message = ServerWebsocketText(
        **{
            "server": server.id,
            "username": current_user.username,
            "profile": current_user.profile,
            "date": datetime.now(),
            "text": "hello",
        }
    )
    await save_message(data=server_message)
    response = await http_request(
        f"/servermessages/{server.id}",
        method=RequestMethod.GET,
        token=current_user_token,
    )
    assert response.status_code == 200
    data = response.json()
    data[0]["date"] = datetime.strptime(
        data[0]["date"], "%Y-%m-%dT%H:%M:%S.%f"
    )  # to compare with datetime value
    assert data == [ServerMessagesOut(**server_message.model_dump()).model_dump()]
