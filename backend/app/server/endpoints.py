from fastapi import APIRouter, Depends, HTTPException, status
from app.server.schemas import (
    UserServer,
    ServersOut,
    ServerUserOut,
    ServerMessagesOut,
    ServerUserCreated,
    ServerCreated,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.server.schemas import ServerIn
from app.database import get_db
from app.core.oauth import get_current_user
from app.user.models import Users
from app.server.service import (
    create_new_server,
    get_all_servers,
    check_user_in_server,
    get_server_by_id,
    get_all_server_users,
    add_user_to_server,
    get_all_server_messages,
    send_create_server_message,
    send_join_server_message,
)
from typing import List
from app.redis import redis_client

server_router = APIRouter()


@server_router.post(
    "/server", status_code=status.HTTP_201_CREATED, response_model=ServerCreated
)
async def create_server(
    server: ServerIn,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_server = await create_new_server(
        db=db, server=server, current_user=current_user
    )
    await send_create_server_message(current_user=current_user, new_server=new_server)
    return new_server


@server_router.get("/server", response_model=List[ServersOut])
async def get_servers(
    current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    servers = await get_all_servers(db=db, current_user=current_user)
    return servers


@server_router.get("/server/{server_id}", response_model=ServersOut)
async def get_server_information(
    server_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    in_server = await check_user_in_server(
        db=db, server_id=server_id, current_user=current_user
    )
    if not in_server:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a part of this server",
        )
    server = await get_server_by_id(db=db, server_id=server_id)
    return server


@server_router.get("/server/users/{server_id}", response_model=List[ServerUserOut])
async def get_server_users(
    server_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    in_server = await check_user_in_server(
        db=db, server_id=server_id, current_user=current_user
    )
    if not in_server:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a part of this server",
        )
    users = await get_all_server_users(db=db, server_id=server_id)
    return users


@server_router.post(
    "/server/user",
    status_code=status.HTTP_201_CREATED,
    response_model=ServerUserCreated,
)
async def join_server(
    user_server: UserServer,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    server_id = await redis_client.get(user_server.link)
    if server_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invite link is invalid"
        )
    server_id = int(server_id)
    in_server = await check_user_in_server(
        db=db, server_id=server_id, current_user=current_user
    )
    if in_server:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already joined the server",
        )
    server_user = await add_user_to_server(
        db=db, server_id=server_id, current_user=current_user
    )
    await send_join_server_message(current_user=current_user, server_user=server_user)
    return server_user


@server_router.get(
    "/servermessages/{server_id}", response_model=List[ServerMessagesOut]
)
async def get_server_messages(
    server_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    in_server = await check_user_in_server(
        db=db, server_id=server_id, current_user=current_user
    )
    if not in_server:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a part of this server",
        )
    server_messages = await get_all_server_messages(db=db, server_id=server_id)
    return server_messages
