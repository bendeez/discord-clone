import asyncio
from utils import RequestMethod
from app.models.user import Users
from app.models.notifications import Notifications

async def test_get_notification(http_request,websocket_connection,get_user_by_username_index,tokens,
                                clean_up_data):
    """
        users with usernames of usernames[0] and usernames[1] have
        a dm
    """
    async def send_notification(current_user: Users,remote_user: Users, remote_user_ws):
        """
            remote user (usernames[1]) sends a dm message which
            in turn sends a notification to the current user
        """
        await remote_user_ws.send_json({"chat":"dm","dm":remote_user.received_dms[0].id,
                            "type":"text","text":"hi","otheruser":current_user.username})

    async def receive_notification(current_user: Users,remote_user: Users, current_user_ws):
        """
            current user receives the dm message notification
        """
        dm_message_notification = {"chat": "dm", "dm": remote_user.received_dms[0].id,
                                   "type": "text", "text": "hi", "otheruser": current_user.username,
                                   "username": remote_user.username, "profile": remote_user.profile}
        while True:
            data = await current_user_ws.receive_json()
            data.pop("date", None)
            if data == dm_message_notification:
                return data



    current_user = await get_user_by_username_index(0)
    current_user_ws = await websocket_connection(path=f"/ws/server/{tokens[current_user.username]}")
    remote_user = await get_user_by_username_index(1,load_attributes=[(Users.received_dms,)])
    remote_user_ws = await websocket_connection(path=f"/ws/server/{tokens[remote_user.username]}")
    tasks = []
    tasks.append(asyncio.create_task(send_notification(current_user,remote_user,remote_user_ws)))
    tasks.append(asyncio.wait_for(asyncio.create_task(receive_notification(current_user,remote_user,current_user_ws)),2)) # wait two seconds for the notification
    await asyncio.gather(*tasks)
    """
        current_user requesting saved dm message received notification message
    """
    await asyncio.sleep(1) # wait for dm message notification to be saved
    response = await http_request("/notifications",method=RequestMethod.GET,token=tokens[current_user.username])
    data = await response.json()
    assert response.status == 200
    assert data == [{"id":data[0]["id"],"dm":remote_user.received_dms[0].id,"count":1,
                       "sender":remote_user.username,"profile":remote_user.profile,"receiver":current_user.username}]
    await clean_up_data(Notifications,id=data[0]["id"])

async def test_delete_notfication(http_request,get_user_by_username_index,tokens,undelete_data):
    """
         user with username of usernames[0] sent a notification to
         user with username of usernames[1]
         both also have a dm
    """
    current_user = await get_user_by_username_index(0)
    remote_user = await get_user_by_username_index(1,load_attributes=[(Users.received_notifications,),(Users.received_dms,)])
    json = {"id":remote_user.received_notifications[0].id}
    response = await http_request(path="/notification", method=RequestMethod.DELETE, json=json,
                                  token=tokens[remote_user.username])
    assert response.status == 204
    await undelete_data(Notifications,sender=current_user.username,receiver=remote_user.username,parent_dm=remote_user.received_dms[0])



