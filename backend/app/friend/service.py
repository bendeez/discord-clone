from sqlalchemy.ext.asyncio import AsyncSession
from app.friend.models import Friends
from app.friend_request.models import FriendRequests
from app.user.models import Users
from app.dm.models import Dms
from typing import Optional
from sqlalchemy import select, union, and_, or_
from app.base import BaseService


class FriendService(BaseService):
    async def get_friend_by_users(self, current_user: Users, remote_user_username):
        stmt = select(Friends).where(
            or_(
                and_(
                    Friends.sender == remote_user_username,
                    Friends.receiver == current_user.username,
                ),
                and_(
                    Friends.receiver == remote_user_username,
                    Friends.sender == current_user.username,
                ),
            )
        )
        friend_request = await self.transaction.execute(stmt)
        return friend_request.scalars().first()

    async def delete_current_friend(self, friend: Friends):
        await self.transaction.delete(friend)

    async def create_friend(
        self,
        db: AsyncSession,
        current_user: Users,
        remote_user_username: str,
        current_friend_request: FriendRequests,
        dm: Optional[Dms] = None,
    ):
        await db.delete(current_friend_request)
        friend = await self.transaction.create(
            model_instance=Friends(
                sender=remote_user_username, receiver=current_user.username
            ),
            relationship="dm",
            relationship_value=dm,
        )
        return friend

    async def get_all_friends(self, current_user: Users):
        received_friends = (
            select(
                Friends.dm_id.label("dmid"), Users.username, Users.profile, Users.status
            )
            .join_from(Friends, Friends.sender_user)
            .where(Friends.receiver == current_user.username)
        )
        sent_friends = (
            select(
                Friends.dm_id.label("dmid"), Users.username, Users.profile, Users.status
            )
            .join_from(Friends, Friends.receiver_user)
            .where(Friends.sender == current_user.username)
        )
        friends = await self.transaction.execute(union(received_friends, sent_friends))
        return friends.all()