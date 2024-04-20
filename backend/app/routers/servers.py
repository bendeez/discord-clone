from fastapi import APIRouter,Depends,HTTPException,status
from app.schemas.servers import UserServer,ServersOut,ServerUserOut,ServerMessagesOut
from app.routers.server_websocket.ServerConnectionManager import server_manager
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.servers import ServerIn
from app.db.database import get_db
from app.core.oauth import get_current_user
from app.models.user import Users
from app.crud.servers import create_new_server,get_all_servers,check_user_in_server,get_server_by_id,get_all_server_users,add_user_to_server,get_all_server_messages
from datetime import datetime
from typing import List
import redis

router = APIRouter()
redis_client = redis.Redis(host="redis",port=6379,db=0,decode_responses=True)

@router.post("/server")
async def create_server(server:ServerIn,current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    new_server = await create_new_server(db=db,server=server,current_user_username=current_user.username)
    server_owner = new_server["owner"]
    server_id = new_server["server_id"]
    server_manager.add_valid_server_or_dm(usernames=[server_owner],type="server_ids",id=server_id)
    created_message = {"chat": "server", "server": server_id, "type": "announcement",
                    "announcement": f"{server_owner} has created the server", "username": server_owner,
                    "date": datetime.now().isoformat()}
    server_manager.broadcast_from_route(sender_username=current_user.username,message=created_message,db=db)
    await db.commit()
@router.get("/servers",response_model=List[ServersOut])
async def get_servers(current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    servers = await get_all_servers(db=db,current_user_username=current_user.username)
    return servers
@router.get("/server/{server_id}")
async def get_server_information(server_id:int,current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    in_server = await check_user_in_server(db=db,server_id=server_id,current_user_username=current_user.username)
    if not in_server:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this server")
    server = await get_server_by_id(db=db,server_id=server_id)
    return server
@router.get("/server/users/{server_id}",response_model=List[ServerUserOut])
async def get_server_users(server_id:int,current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    in_server = await check_user_in_server(db=db, server_id=server_id, current_user_username=current_user.username)
    if not in_server:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this server")
    users = await get_all_server_users(db=db,server_id=server_id)
    return users
@router.post("/server/user")
async def join_server(user_server:UserServer,current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    server_id = redis_client.get(user_server.link)
    if server_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invite link is invalid")
    server_id = int(server_id)
    in_server = await check_user_in_server(db=db, server_id=server_id, current_user_username=current_user.username)
    if in_server:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already joined the server")
    await add_user_to_server(db=db,server_id=server_id,current_user_username=current_user.username)
    join_message = {"chat":"server","server":server_id,"type":"announcement","announcement":f"{current_user.username} has joined the server","username":current_user.username,"date":datetime.now().isoformat()}
    server_manager.add_valid_server_or_dm(current_user.username,"server_ids",server_id)
    await server_manager.broadcast_from_route(sender_username=current_user.username,message=join_message,db=db)
    await db.commit()
    return {"serverid":server_id}
@router.get("/servermessages/{server_id}",response_model=List[ServerMessagesOut])
async def get_server_messages(server_id:int, current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    in_server = await check_user_in_server(db=db, server_id=server_id, current_user_username=current_user.username)
    if not in_server:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this server")
    server_messages = await get_all_server_messages(db=db,server_id=server_id)
    return server_messages