import asyncio
from app.models.user import Users
from app.models.dms import Dms, Dm_Messages
from utils import RequestMethod


async def test_create_dm(http_request,websocket_connection,tokens,get_user_by_username_index,clean_up_data):

    async def create_dm(current_user: Users, remote_user: Users, current_user_ws):
        """
            connect to websocket to send create dm notification
            create dm current_user -> remote_user
            users with usernames of usernames[0] and usernames[2] don't have a created dm
        """
        json = {"username": remote_user.username}
        response = await http_request("/dm",method=RequestMethod.POST,
                                      json=json,token=tokens[current_user.username])
        assert response.status == 201
        data = await response.json()
        assert data == {"id": data["id"], "sender": current_user.username, "receiver": remote_user.username}
        await clean_up_data(Dms, id=data["id"])

    async def check_for_new_dm(current_user:Users, remote_user: Users, remote_user_ws):
        """
            listen for create dm notification
            remote user perspective
        """
        new_dm_notification = {"sender": current_user.username, "profile": current_user.profile, "receiver": remote_user.username,
                               "chat": "notification", "type": "newdm"}
        while True:
            data = await remote_user_ws.receive_json()
            if data == new_dm_notification:
                return data

    current_user = await get_user_by_username_index(0)
    current_user_ws = await websocket_connection(path=f"/ws/server/{tokens[current_user.username]}")
    remote_user = await get_user_by_username_index(2)
    remote_user_ws = await websocket_connection(path=f"/ws/server/{tokens[remote_user.username]}")
    tasks = []
    tasks.append(asyncio.create_task(create_dm(current_user,remote_user,current_user_ws)))
    tasks.append(asyncio.wait_for(asyncio.create_task(check_for_new_dm(current_user,remote_user,remote_user_ws)),2)) # wait max 2 seconds for the notification to be sent
    await asyncio.gather(*tasks)

async def test_invalid_post_dm(http_request,usernames,tokens):
    """
        usernames[0] and usernames[1] already have a created dm
    """
    json = {"username": usernames[1]}
    response = await http_request("/dm", method=RequestMethod.POST,
                                  json=json, token=tokens[usernames[0]])
    assert response.status == 409

async def test_get_dms(http_request,usernames,get_user_by_username_index,tokens):
    """
        user with username of usernames[0] has one dm that it sent to
        usernames[1]

        returns the user of the dm that's not the current user
    """
    current_user = await get_user_by_username_index(0,load_attributes=[(Users.sent_dms,)])
    remote_user = await get_user_by_username_index(1)
    dm = current_user.sent_dms[0]
    response = await http_request("/dms", method=RequestMethod.GET,
                                  token=tokens[current_user.username])
    data = await response.json()
    assert response.status == 200
    assert data == [{"status":remote_user.status,"id":dm.id,
                     "username":remote_user.username,"profile":remote_user.profile}]


async def test_get_dm_user_by_id(http_request,get_user_by_username_index,tokens):
    """
        user with username of usernames[0] has one dm that it sent to
        usernames[1]

        returns the user of the dm that's not the current user
    """
    current_user = await get_user_by_username_index(0, load_attributes=[(Users.sent_dms,)])
    remote_user = await get_user_by_username_index(1)
    dm = current_user.sent_dms[0]
    response = await http_request(f"/dm/{dm.id}", method=RequestMethod.GET,
                                  token=tokens[current_user.username])
    data = await response.json()
    assert response.status == 200
    assert data == {"username":remote_user.username,"profile":remote_user.profile,
                    "id":dm.id,"status":remote_user.status}

async def test_get_dm_forbidden(http_request,usernames,tokens):
    """
        current_user does not have a dm with that id
    """
    response = await http_request(f"/dm/4897", method=RequestMethod.GET,
                                  token=tokens[usernames[0]])
    assert response.status == 403

async def test_get_dm_messages(http_request,get_user_by_username_index,tokens):
    """
        dm only has one dm message
        Dm_Messages(text="hi", user=user_models[0], date=datetime.now())
        user_models[0] = current_user
    """
    current_user = await get_user_by_username_index(0, load_attributes=[(Users.sent_dms, Dms.dm_messages)])
    dm = current_user.sent_dms[0]
    response = await http_request(f"/dmmessages/{dm.id}", method=RequestMethod.GET,
                                  token=tokens[current_user.username])
    data = await response.json()
    dm_messages = [{key:value for key,value in message.items() if value is not None}
                  for message in data] # filter out None values
    assert response.status == 200
    assert dm_messages == [{"dm":dm.id,"text":"hi","username":current_user.username,
                          "profile":current_user.profile,"date":dm_messages[0]["date"]}]




