from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.notifications import Notifications
from app.models.user import Users


async def get_all_notifications(db: AsyncSession, current_user_username: str):
    notifications = await db.execute(
        select(Notifications.id, Notifications.dm, Notifications.count,
               Notifications.receiver, Users.username.label("sender"), Users.profile)
        .join(Users,
              Users.username == Notifications.sender
              )
        .filter(
            Notifications.receiver == current_user_username
        )
    )
    return notifications.all()


async def get_notification_by_id(db: AsyncSession, notification_id: int):
    notification = await db.execute(select(Notifications).filter(Notifications.dm == notification_id))
    return notification.scalars().first()
