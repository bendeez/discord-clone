from sqlalchemy.ext.asyncio import AsyncSession
from app.models.friends import Friends
from app.models.user import Users
from sqlalchemy import select, union, and_, or_
from sqlalchemy.orm import selectinload


async def check_already_friends(db: AsyncSession, current_user: Users, remote_user_username: str):
    current_user_friends = await db.execute(select(Users)
                                            .where(Users.username == current_user.username)
                                            .options(selectinload(Users.sent_friends),
                                                     selectinload(Users.received_friends)))
    current_user_friends = current_user_friends.scalars().first()
    if current_user_friends is not None:
        if remote_user_username in [friend.receiver for friend in current_user_friends.sent_friends] + \
                                   [friend.sender for friend in current_user_friends.received_friends]:
            return True
        return False


async def create_friend(db: AsyncSession, current_user: Users, remote_user_username: str):
    from app.crud.dms import get_dm
    friend = Friends(sender=remote_user_username, receiver=current_user.username) # current_user received the friend request
    dm = await get_dm(db=db, current_user=current_user, remote_user_username=remote_user_username)
    if dm is not None:
        friend.dm = dm
    db.add(friend)
    await db.commit()
    await db.refresh(friend)
    return friend


async def get_all_friends(db: AsyncSession, current_user: Users):
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

async def get_friend(db: AsyncSession,current_user: Users,remote_user_username):
    friend_request = await db.execute(
        select(Friends).filter(
            or_(
                and_(Friends.sender == remote_user_username, Friends.receiver == current_user.username),
                and_(Friends.receiver == remote_user_username, Friends.sender == current_user.username)
            )
        )
    )
    return friend_request.scalars().first()
