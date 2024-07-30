from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.servers import Server, Server_User, Server_Messages
from app.schemas.servers import ServerIn
from app.firebase_startup import firebase_storage
from app.models.user import Users
from app.schemas.websocket_data.server_message import ServerWebsocketAnnouncement
import uuid
import base64
import asyncio
from app.WebsocketManagers.CentralWebsocketServerInterface import central_ws_interface
from base import BaseService

class ServerService(BaseService):

    async def upload_server_profile(self, server: ServerIn):
        filename = f"{uuid.uuid4()}.jpg"
        if "," in server.profile:
            server_profile = server.profile.split(",")[1]
        else:
            server_profile = server.profile
        encoded_image = base64.b64decode(server_profile)
        await asyncio.to_thread(firebase_storage.child(filename).put, encoded_image)
        return filename

    async def create_new_server(self, db: AsyncSession, server: ServerIn, current_user: Users):
        if server.profile:
            filename = await self.upload_server_profile(server=server)
            new_server = Server(name=server.name,
                                profile=f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8",
                                owner=current_user.username)
        else:
            new_server = Server(name=server.name, owner=current_user.username)
        new_server.server_users.append(Server_User(username=current_user.username))
        db.add(new_server)
        await db.commit()
        await db.refresh(new_server)
        return new_server


    async def get_all_servers(self, db: AsyncSession, current_user: Users):
        servers = await db.execute(select(Server.owner,Server.profile,
                                          Server.id,Server.name)
                                        .join_from(Users,Users.server_associations)
                                        .join_from(Server_User,Server)
                                        .where(Users.username == current_user.username))
        return servers.all()


    async def check_user_in_server(self, db: AsyncSession, server_id: int, current_user: Users):
        server = await db.execute(select(Server)
                              .where(Server.id == server_id)
                              .options(selectinload(Server.server_users)
                                       .selectinload(Server_User.user)))
        server = server.scalars().first()
        if server is not None:
            if current_user in [server_user.user for server_user in server.server_users]:
                return True
        return False


    async def get_server_by_id(self, db: AsyncSession, server_id: int):
        server = await db.execute(select(Server).where(Server.id == server_id))
        return server.scalars().first()


    async def get_all_server_users(self, db: AsyncSession, server_id: int):
        users = await db.execute(select(Users.username,Users.profile,
                                        Users.status)
                                    .join_from(Server_User,Server_User.user)
                                    .where(Server_User.server_id == server_id))
        return users.all()


    async def add_user_to_server(self, db: AsyncSession, server_id: int, current_user: Users):
        server_user = Server_User(username=current_user.username, server_id=server_id)
        db.add(server_user)
        await db.commit()
        await db.refresh(server_user)
        return server_user


    async def get_all_server_messages(self, db: AsyncSession, server_id: int):
        server_messages = await db.execute(select(Server_Messages.server,
                                                  Server_Messages.announcement,
                                                  Server_Messages.text,Server_Messages.file,
                                                  Server_Messages.filetype,
                                                  Server_Messages.date,
                                                  Users.username,Users.profile)
                                                .join_from(Server_Messages,Server_Messages.user)
                                                .where(Server_Messages.server == server_id)
                                                .order_by(Server_Messages.id))

        return server_messages.all()

    async def delete_current_server(self, server: Server):
        await self.transaction.delete(server)

    async def delete_current_server_user(self, server_user: Server_User):
        await self.transaction.delete(server_user)

    async def delete_current_server_message(self, server_message: Server_Messages):
        await self.transaction.delete(server_message)

    async def send_create_server_message(self, current_user: Users, new_server: Server):
        """
                add the server id to the users' server_ids list so they can
                send messages in that server
        """
        central_ws_interface.add_valid_server_or_dm(usernames=[new_server.owner], type="server_ids", id=new_server.id)
        create_server_message = ServerWebsocketAnnouncement(**{"server": new_server.id,
                                                             "announcement": f"{new_server.owner} has created the server", "username": new_server.owner})
        await central_ws_interface.broadcast_from_route(sender_username=current_user.username, message=create_server_message)

    async def send_join_server_message(self, current_user: Users,server_user: Server_User):
        """
                add the server id to the users' server_ids list so they can
                send messages in that server
        """
        join_server_message = ServerWebsocketAnnouncement(**{"server": server_user.server_id,
                               "announcement": f"{current_user.username} has joined the server",
                               "username": server_user.username})
        central_ws_interface.add_valid_server_or_dm(usernames=[server_user.username],type="server_ids",id=server_user.server_id)
        await central_ws_interface.broadcast_from_route(sender_username=current_user.username, message=join_server_message)