from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.servers import UserServer, ServersOut, ServerUserOut, ServerMessagesOut, \
                                ServerUserCreated, ServerCreated
from app.routers.server_websocket.ServerConnectionManager import server_manager
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.servers import ServerIn
from app.db.database import get_db
from app.core.oauth import get_current_user
from app.models.user import Users
from app.crud.servers import create_new_server, get_all_servers, check_user_in_server, get_server_by_id, \
    get_all_server_users, add_user_to_server, get_all_server_messages
from datetime import datetime
from typing import List
from app.redis.redis_client import redis_client

router = APIRouter()



@router.post("/server", status_code=status.HTTP_201_CREATED, response_model=ServerCreated)
async def create_server(server: ServerIn, current_user: Users = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    new_server = await create_new_server(db=db, server=server, current_user=current_user)
    server_manager.add_valid_server_or_dm(usernames=[new_server.owner], type="server_ids", id=new_server.id)
    created_message = {"chat": "server", "server": new_server.id, "type": "announcement",
                       "announcement": f"{new_server.owner} has created the server", "username": new_server.owner,
                       "date": datetime.now().isoformat()}
    await server_manager.broadcast_from_route(sender_username=current_user.username, message=created_message, db=db)
    return new_server



@router.get("/servers", response_model=List[ServersOut])
async def get_servers(current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    servers = await get_all_servers(db=db, current_user=current_user)
    return servers


@router.get("/server/{server_id}", response_model=ServersOut)
async def get_server_information(server_id: int, current_user: Users = Depends(get_current_user),
                                 db: AsyncSession = Depends(get_db)):
    in_server = await check_user_in_server(db=db, server_id=server_id, current_user=current_user)
    if not in_server:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this server")
    server = await get_server_by_id(db=db, server_id=server_id)
    return server


@router.get("/server/users/{server_id}", response_model=List[ServerUserOut])
async def get_server_users(server_id: int, current_user: Users = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    in_server = await check_user_in_server(db=db, server_id=server_id, current_user=current_user)
    if not in_server:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this server")
    users = await get_all_server_users(db=db, server_id=server_id)
    return users


@router.post("/server/user", status_code=status.HTTP_201_CREATED, response_model=ServerUserCreated)
async def join_server(user_server: UserServer, current_user: Users = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    server_id = redis_client.get(user_server.link)
    if server_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invite link is invalid")
    server_id = int(server_id)
    in_server = await check_user_in_server(db=db, server_id=server_id, current_user=current_user)
    if in_server:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already joined the server")
    server_user = await add_user_to_server(db=db, server_id=server_id, current_user=current_user)
    join_message = {"chat": "server", "server": server_user.server_id, "type": "announcement",
                    "announcement": f"{current_user.username} has joined the server", "username": server_user.username,
                    "date": datetime.now().isoformat()}
    server_manager.add_valid_server_or_dm(server_user.username, "server_ids", server_user.server_id)
    await server_manager.broadcast_from_route(sender_username=current_user.username, message=join_message, db=db)
    return server_user


@router.get("/servermessages/{server_id}", response_model=List[ServerMessagesOut])
async def get_server_messages(server_id: int, current_user: Users = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)):
    in_server = await check_user_in_server(db=db, server_id=server_id, current_user=current_user)
    if not in_server:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this server")
    server_messages = await get_all_server_messages(db=db, server_id=server_id)
    return server_messages
