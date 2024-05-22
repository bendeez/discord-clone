from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.servers import Server, Server_User, Server_Messages
from app.schemas.servers import ServerIn
from app.firebase.firebase_startup import firebase_storage
from app.models.user import Users
import uuid
import base64
import asyncio

async def create_new_server(db: AsyncSession, server: ServerIn, current_user_username: str):
    if server.profile:
        filename = f"{uuid.uuid4()}.jpg"
        encoded_image = base64.b64decode(server.profile.split(",")[1])
        await asyncio.to_thread(firebase_storage.child(filename).put, encoded_image)
        new_server = Server(name=server.name,
                            profile=f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8",
                            owner=current_user_username)
    else:
        new_server = Server(name=server.name, owner=current_user_username)
    new_server.server_users.append(Server_User(username=current_user_username))
    db.add(new_server)
    await db.flush()
    return {"server_id": new_server.id, "owner": current_user_username}


async def get_all_servers(db: AsyncSession, current_user_username: str):
    servers = await db.execute(
        select(Server_User.server_id, Server.owner, Server.profile, Server.id, Server.name)
        .join(Server,
              Server.id == Server_User.server_id
              )
        .filter(
            Server_User.username == current_user_username
        )
    )
    return servers.all()


async def check_user_in_server(db: AsyncSession, server_id: int, current_user_username: str):
    in_server = await db.execute(select(Server_User)
    .filter(
        and_(Server_User.server_id == server_id, Server_User.username == current_user_username)
    )
    )
    return in_server.scalars().first()


async def get_server_by_id(db: AsyncSession, server_id: int):
    server = await db.execute(select(Server).filter(Server.id == server_id))
    return server.scalars().first()


async def get_all_server_users(db: AsyncSession, server_id: int):
    users = await db.execute(
        select(Server_User.username, Users.username, Users.profile, Users.status)
        .join(
            Users, Server_User.username == Users.username
        )
        .filter(
            Server_User.server_id == server_id
        )
    )
    return users.all()


async def add_user_to_server(db: AsyncSession, server_id: int, current_user_username: str):
    server_user = Server_User(username=current_user_username, server_id=server_id)
    db.add(server_user)


async def get_all_server_messages(db: AsyncSession, server_id: int):
    server_messages = await db.execute(
        select(Server_Messages.announcement, Server_Messages.server, Server_Messages.username,
               Server_Messages.text, Server_Messages.file, Server_Messages.created_date.label("date"),
               Server_Messages.filetype, Users.profile)
        .join(Users,
              Server_Messages.username == Users.username
              )
        .filter(
            Server_Messages.server == server_id
        )
        .order_by(Server_Messages.id)
    )
    return server_messages.all()
