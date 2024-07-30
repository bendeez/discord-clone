from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import aliased
from app.models.friend_requests import FriendRequests
from app.models.user import Users
from base import BaseService

class FriendRequestService(BaseService):
    async def check_friend_request(self, db: AsyncSession, current_user: Users, remote_user_username: str):
        friend_request = await self.get_friend_request(db=db,current_user=current_user,remote_user_username=remote_user_username)
        if friend_request is not None:
            return True
        return False

    async def get_friend_request(self, db: AsyncSession,current_user: Users,remote_user_username:str):
        friend_request = await db.execute(
            select(FriendRequests).filter(
                or_(
                    and_(FriendRequests.sender == remote_user_username, FriendRequests.receiver == current_user.username),
                    and_(FriendRequests.receiver == remote_user_username, FriendRequests.sender == current_user.username)
                )
            )
        )
        return friend_request.scalars().first()

    async def create_friend_request(self, current_user: Users, remote_user_username: str):
        request = await self.transaction.create(FriendRequests(sender=current_user.username, receiver=remote_user_username))
        return request


    async def get_all_friend_requests(self, db: AsyncSession, current_user: Users):
        receiver_user = aliased(Users, name="receiver_user")
        sender_user = aliased(Users, name="sender_user")
        friend_requests = await db.execute(select(FriendRequests.receiver, FriendRequests.sender,
                                                  receiver_user.profile.label("receiverprofile"),
                                                  sender_user.profile.label("senderprofile"))
                                            .join_from(FriendRequests,FriendRequests.receiver_user.of_type(receiver_user))
                                            .join_from(FriendRequests,FriendRequests.sender_user.of_type(sender_user))
                                            .where(
                                                or_(
                                                    FriendRequests.receiver == current_user.username,
                                                    FriendRequests.sender == current_user.username)
                                                )
                                            )
        return friend_requests.all()

    async def delete_current_friend_request(self, friend_request: FriendRequests):
        await self.transaction.delete(friend_request)

