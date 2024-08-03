from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, union, case, func, or_, and_
from app.websocket_server.schemas.notification_message import NotificationNewDm
from app.dm.models import Dms, Dm_Messages
from app.server.models import Server
from app.friend.models import Friends
from app.websocket_server.websocket_managers.CentralWebsocketServerInterface import (
    central_ws_interface,
)
from app.redis import redis_client
from typing import Optional
from app.base_service import BaseService


class DmService(BaseService):

    async def get_dm_by_users(self, current_user_id: int, remote_user_id: int) -> Dms:
        dm = await self.transaction.get_by_user_ids(model=Dms, current_user_id=current_user_id,
                                                    remote_id=remote_user_id)
        return dm

    async def check_user_in_dm(self, current_user_id: int, dm_id: int) -> bool:
        user_in_dm = await self.transaction.check_user_in_entity(model=Dms,current_user_id=current_user_id,
                                                                 entity_id=dm_id)
        return user_in_dm

    async def create_new_dm(
        self,
        current_user_id: int,
        remote_user_username: str,
        friend: Optional[Friends] = None,
    ):
        dm = await self.transaction.create(
            model_instance=Dms(
                sender=current_user_id, receiver=remote_user_username
            ),
            relationship="friend",
            relationship_value=friend,
        )
        return dm

    async def save_dm_message(self, data: dict):
        if "link" in data:
            await redis_client.set(data["link"], data["serverinviteid"])
        dm_message = await Dm_Messages.save_dm_message(data=data)
        dm_message = await self.transaction.create(dm_message)
        return dm_message

    async def get_all_dms(self, current_user: Users):
        received_dms = (
            select(Dms.id, Users.username, Users.profile, Users.status)
            .join_from(Dms, Dms.sender_user)
            .where(Dms.receiver == current_user.username)
        )
        sent_dms = (
            select(Dms.id, Users.username, Users.profile, Users.status)
            .join_from(Dms, Dms.receiver_user)
            .where(Dms.sender == current_user.username)
        )
        dms = await self.transaction.execute(union(received_dms, sent_dms))
        return dms.all()

    async def get_all_dm_information(self, current_user: Users, dm_id: int):
        user_in_dm = await self.check_user_in_dm(current_user=current_user, dm_id=dm_id)
        if not user_in_dm:
            return None
        stmt = select(
            case(
                (
                    Dms.sender == current_user.username,
                    (
                        select(
                            func.row(
                                Users.username, Users.profile, Users.status, Dms.id
                            )
                        ).where(Users.username == Dms.receiver)
                    ).scalar_subquery(),
                ),
                (
                    Dms.receiver == current_user.username,
                    (
                        select(
                            func.row(
                                Users.username, Users.profile, Users.status, Dms.id
                            )
                        ).where(Users.username == Dms.sender)
                    ).scalar_subquery(),
                ),
            ).label("information")
        ).where(Dms.id == dm_id)
        dm_user = await self.transaction.execute(stmt)
        return dm_user.first()

    async def get_all_dm_messages(self, db: AsyncSession, dm_id: int):
        dm_messages = await db.execute(
            select(
                Dm_Messages.dm,
                Dm_Messages.link,
                Dm_Messages.text,
                Dm_Messages.file,
                Dm_Messages.filetype,
                Dm_Messages.serverinviteid,
                Dm_Messages.date,
                Users.username,
                Users.profile,
                Users.status,
                Server.name.label("servername"),
                Server.profile.label("serverprofile"),
            )
            .join_from(Dm_Messages, Dm_Messages.user)
            .outerjoin_from(Dm_Messages, Dm_Messages.server_invite_info)
            .where(Dm_Messages.dm == dm_id)
            .order_by(Dm_Messages.id)
        )
        return dm_messages.all()

    async def delete_current_dm(self, dm: Dms):
        await self.transaction.delete(dm)

    async def delete_current_dm_message(self, dm_message: Dm_Messages):
        await self.transaction.delete(dm_message)

    async def send_new_dm_notification(self, current_user: Users, dm: Dms):
        """
        add the dm id to the users' dm_ids list so they can
        send messages in that dm
        """
        central_ws_interface.add_valid_server_or_dm(
            usernames=[dm.sender, dm.receiver], type="dm_ids", id=dm.id
        )
        create_dm_notification = NotificationNewDm(
            **{"sender": dm.sender, "receiver": dm.receiver}
        )
        await central_ws_interface.broadcast_from_route(
            sender_username=current_user.username, message=create_dm_notification
        )
