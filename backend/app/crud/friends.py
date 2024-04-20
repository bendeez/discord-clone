from sqlalchemy.ext.asyncio import AsyncSession
from app.models.friends import Friends
from app.models.dms import Dms
from app.models.user import Users
from sqlalchemy import select,or_,and_

async def check_already_friends(db:AsyncSession,current_user_username:str,remote_user_username:str):
    already_friends = await db.execute(
                                select(Friends).filter(
                                    or_(
                                        and_(Friends.sender == current_user_username,Friends.receiver == remote_user_username),
                                        and_(Friends.receiver == current_user_username,Friends.sender == remote_user_username)
                                        )
                                )
                            )
    return already_friends.scalars().first()

async def create_friend(db:AsyncSession,current_user_username:str,remote_user_username:str):
    friend = Friends(sender=remote_user_username, receiver=current_user_username)
    db.add(friend)
    await db.commit()

async def get_all_friends(db:AsyncSession,current_user_username:str):
    friends = await db.execute(
                        select(Users.profile, Users.username, Users.status, Dms.id.label("dmid"))
                        .join(Friends,
                            or_(
                                and_(Friends.receiver == current_user_username, Friends.sender == Users.username),
                                and_(Friends.sender == current_user_username,Friends.receiver == Users.username)
                            )
                        )
                        .outerjoin(Dms,
                            or_(
                                and_(Dms.sender == current_user_username, Dms.receiver == Users.username),
                                and_(Dms.receiver == current_user_username,Dms.sender == Users.username)
                            )
                        )
                    )
    return friends.all()