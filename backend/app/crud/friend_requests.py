from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import aliased, selectinload
from app.models.friend_requests import FriendRequests
from app.models.user import Users


async def check_friend_request(db: AsyncSession, current_user: Users, remote_user_username: str):
    current_user_friend_requests = await db.execute(select(Users)
                                .where(Users.username == current_user.username)
                                .options(selectinload(Users.sent_friend_requests),
                                         selectinload(Users.received_friend_requests)))
    current_user_friend_requests = current_user_friend_requests.scalars().first()
    if current_user_friend_requests is not None:
        if remote_user_username in [friend_request.receiver for friend_request in current_user_friend_requests.sent_friend_requests] + \
                                   [friend_request.sender for friend_request in current_user_friend_requests.received_friend_requests]:
            return True
        return False


async def create_friend_request(db: AsyncSession, current_user: Users, remote_user_username: str):
    request = FriendRequests(sender=current_user.username, receiver=remote_user_username)
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return request


async def get_all_friend_requests(db: AsyncSession, current_user: Users):
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

async def get_friend_request(db: AsyncSession,current_user: Users,remote_user_username:str):
    friend_request = await db.execute(
        select(FriendRequests).filter(
            or_(
                and_(FriendRequests.sender == remote_user_username, FriendRequests.receiver == current_user.username),
                and_(FriendRequests.receiver == remote_user_username, FriendRequests.sender == current_user.username)
            )
        )
    )
    return friend_request.scalars().first()
