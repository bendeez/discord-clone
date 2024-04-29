from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import Users


async def check_user_exists(db: AsyncSession, remote_user_username: str):
    user_exists = await db.execute(select(Users).filter(Users.username == remote_user_username))
    return user_exists.scalars().first()


async def create_new_user(db: AsyncSession, username: str, email: str, password: str):
    new_user = Users(username=username, email=email, password=password)
    db.add(new_user)
    await db.commit()


async def update_current_profile_picture(db: AsyncSession, current_user: Users, filename: str):
    current_user.profile = f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"
    await db.commit()
