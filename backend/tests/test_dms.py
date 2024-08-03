from utils import RequestMethod
from app.dm.service import create_new_dm
from app.services.server_websocket import save_message
from app.websocket_server.schemas.dm_message import DmWebsocketText
from app.websocket_server.schemas.notification_message import NotificationNewDm
from app.dm.schemas import DmMessagesOut
from datetime import datetime


async def test_create_dm(
    http_request, current_user, current_user_token, websocket_connection, remote_user
):
    remote_user, remote_token = await remote_user()
    remote_ws, _ = await websocket_connection(token=remote_token)
    await websocket_connection(
        token=current_user_token
    )  # current_user websocket connection to send create dm message (application does that)
    response = await http_request(
        "/dm",
        method=RequestMethod.POST,
        json={"username": remote_user.username},
        token=current_user_token,
    )
    assert response.status_code == 201
    data = response.json()
    dm_id = data["id"]
    assert data == {
        "id": dm_id,
        "sender": current_user.username,
        "receiver": remote_user.username,
    }
    """
            first 2 are status update notification for each
            user
    """
    await remote_ws.recv()
    await remote_ws.recv()
    data = await remote_ws.recv()
    assert (
        data
        == NotificationNewDm(
            **{
                "sender": current_user.username,
                "profile": current_user.profile,
                "receiver": remote_user.username,
            }
        ).model_dump()
    )


async def test_invalid_post_dm(
    http_request, current_user, current_user_token, db, remote_user
):
    remote_user, _ = await remote_user()
    await create_new_dm(
        current_user=current_user, remote_user_username=remote_user.username, db=db
    )
    """
        create a dm that's already been created
    """
    response = await http_request(
        "/dm",
        method=RequestMethod.POST,
        json={"username": remote_user.username},
        token=current_user_token,
    )
    assert response.status_code == 409


async def test_get_dms(http_request, current_user, current_user_token, remote_user, db):
    remote_user, _ = await remote_user()
    dm = await create_new_dm(
        current_user=current_user, remote_user_username=remote_user.username, db=db
    )
    response = await http_request(
        "/dm", method=RequestMethod.GET, token=current_user_token
    )
    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            "status": remote_user.status,
            "id": dm.id,
            "username": remote_user.username,
            "profile": remote_user.profile,
        }
    ]


async def test_get_dm_user_by_id(
    http_request, current_user, current_user_token, remote_user, db
):
    remote_user, _ = await remote_user()
    dm = await create_new_dm(
        current_user=current_user, remote_user_username=remote_user.username, db=db
    )
    response = await http_request(
        f"/dm/{dm.id}", method=RequestMethod.GET, token=current_user_token
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "username": remote_user.username,
        "profile": remote_user.profile,
        "id": dm.id,
        "status": remote_user.status,
    }


async def test_get_dm_forbidden(http_request, current_user_token):
    response = await http_request(
        "/dm/4897", method=RequestMethod.GET, token=current_user_token
    )
    assert response.status_code == 403


async def test_get_dm_messages(
    http_request, current_user, current_user_token, remote_user, db
):
    remote_user, _ = await remote_user()
    dm = await create_new_dm(
        current_user=current_user, remote_user_username=remote_user.username, db=db
    )
    dm_message = DmWebsocketText(
        **{
            "dm": dm.id,
            "otheruser": remote_user.username,
            "username": current_user.username,
            "profile": current_user.profile,
            "date": datetime.now(),
            "text": "hello",
        }
    )
    await save_message(data=dm_message)
    response = await http_request(
        f"/dmmessages/{dm.id}", method=RequestMethod.GET, token=current_user_token
    )
    assert response.status_code == 200
    data = response.json()
    data[0]["date"] = datetime.strptime(
        data[0]["date"], "%Y-%m-%dT%H:%M:%S.%f"
    )  # to compare with datetime value
    assert data == [DmMessagesOut(**dm_message.model_dump()).model_dump()]
