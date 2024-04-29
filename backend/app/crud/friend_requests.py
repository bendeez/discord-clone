from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import aliased
from app.models.friend_requests import FriendRequests
from app.models.user import Users


async def check_friend_request(db: AsyncSession, current_user_username: str, remote_user_username: str):
    friend_request = await db.execute(
        select(FriendRequests).filter(
            or_(
                and_(FriendRequests.sender == remote_user_username, FriendRequests.receiver == current_user_username),
                and_(FriendRequests.receiver == remote_user_username, FriendRequests.sender == current_user_username)
            )
        )
    )
    return friend_request.scalars().first()


async def create_friend_request(db: AsyncSession, current_user_username: str, remote_user_username: str):
    request = FriendRequests(sender=current_user_username, receiver=remote_user_username)
    db.add(request)
    await db.commit()


async def get_all_friend_requests(db: AsyncSession, current_user_username: str):
    receiver_user = aliased(Users, name="receiver_user")
    sender_user = aliased(Users, name="sender_user")
    friend_requests = await db.execute(
        select(FriendRequests.receiver, FriendRequests.sender,
               receiver_user.profile.label("receiverprofile"),
               sender_user.profile.label("senderprofile")
               )
        .join(receiver_user,
              receiver_user.username == FriendRequests.receiver
              )
        .join(sender_user,
              sender_user.username == FriendRequests.sender
              )
        .filter(
            or_(FriendRequests.receiver == current_user_username, FriendRequests.sender == current_user_username)
        )
    )
    return friend_requests.all()
