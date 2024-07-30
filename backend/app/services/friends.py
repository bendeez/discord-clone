from sqlalchemy.ext.asyncio import AsyncSession
from app.models.friends import Friends
from app.models.friend_requests import FriendRequests
from app.models.user import Users
from sqlalchemy import select, union, and_, or_
from base import BaseService

class FriendService(BaseService):


    async def check_already_friends(self, db: AsyncSession, current_user: Users, remote_user_username: str):
        friend = await self.get_friend(db=db, current_user=current_user,
                                                  remote_user_username=remote_user_username)
        if friend is not None:
            return True
        return False
    async def get_friend(self, db: AsyncSession,current_user: Users,remote_user_username):
        friend_request = await db.execute(
            select(Friends).filter(
                or_(
                    and_(Friends.sender == remote_user_username, Friends.receiver == current_user.username),
                    and_(Friends.receiver == remote_user_username, Friends.sender == current_user.username)
                )
            )
        )
        return friend_request.scalars().first()

    async def delete_current_friend(self, friend: Friends):
        await self.transaction.delete(friend)

    async def create_friend(self, db: AsyncSession, current_user: Users, remote_user_username: str,current_friend_request: FriendRequests):
        from app.services.dms import get_dm
        await db.delete(current_friend_request)
        friend = Friends(sender=remote_user_username, receiver=current_user.username) # current_user received the friend request
        dm = await get_dm(db=db, current_user=current_user, remote_user_username=remote_user_username)
        if dm is not None:
            friend.dm = dm
        db.add(friend)
        await db.commit()
        await db.refresh(friend)
        return friend


    async def get_all_friends(self, db: AsyncSession, current_user: Users):
        received_friends = (select(Friends.dm_id.label("dmid"),
                                   Users.username, Users.profile,
                                   Users.status)
                            .join_from(Friends, Friends.sender_user)
                            .where(Friends.receiver == current_user.username))
        sent_friends = (select(Friends.dm_id.label("dmid"),
                               Users.username, Users.profile,
                               Users.status)
                        .join_from(Friends, Friends.receiver_user)
                        .where(Friends.sender == current_user.username))
        friends = await db.execute(union(received_friends, sent_friends))
        return friends.all()

