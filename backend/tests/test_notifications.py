from app.crud.dms import create_new_dm
from app.crud.server_websocket import save_message
from app.crud.notifications import get_notification_by_dm_id
from app.schemas.websocket_data.notification_message import NotificationMessage
from app.schemas.websocket_data.dm_message import DmWebsocketText
from app.routers.server_websocket.ServerConnectionManager import server_manager
import asyncio
from utils import RequestMethod

async def test_get_notification(http_request,current_user,current_user_token,websocket_connection,remote_user,db):
    remote_user,remote_token = await remote_user()
    dm = await create_new_dm(db=db,current_user=current_user,remote_user_username=remote_user.username)
    current_ws,current_ws_user = await websocket_connection(token=current_user_token)
    remote_ws, remote_ws_user = await websocket_connection(token=remote_token)
    await server_manager.broadcast(data=DmWebsocketText(**{"dm":dm.id,"text":"hi",
                                  "otheruser":current_user.username}).model_dump(),
                                   current_user=remote_ws_user)
    await current_ws.recv() # status notification
    await current_ws.recv() # status notification
    await current_ws.recv() # dm message
    data = await current_ws.recv()
    assert data == NotificationMessage(**{"sender":remote_user.username,"profile":remote_user.profile,
                                          "dm":dm.id,"receiver":current_user.username,"count":None}).model_dump()
    await asyncio.sleep(1)
    response = await http_request("/notifications",method=RequestMethod.GET,token=current_user_token)
    assert response.status_code == 200
    data = response.json()
    assert data == [{"id":data[0]["id"],"dm":dm.id,"count":1,
                    "sender":remote_user.username,"profile":remote_user.profile,
                     "receiver":current_user.username}]

async def test_delete_notfication(http_request,current_user,current_user_token,websocket_connection,remote_user,db):
    remote_user,_ = await remote_user()
    dm = await create_new_dm(db=db, current_user=current_user, remote_user_username=remote_user.username)
    await save_message(data=NotificationMessage(**{"dm": dm.id,"sender": remote_user.username,
                                                   "receiver": current_user.username,"profile": remote_user.profile}))
    response = await http_request(path="/notification",
                                  method=RequestMethod.DELETE,
                                  json={"id":dm.id},
                                  token=current_user_token)
    assert response.status_code == 204
    notification = await get_notification_by_dm_id(db=db,notification_dm_id=dm.id)



