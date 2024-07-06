from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import aliased
from app.models.notifications import Notifications
from app.models.user import Users


async def get_all_notifications(db: AsyncSession, current_user: Users):
    sender_user = aliased(Users,name="sender_user")
    notifications = await db.execute(select(sender_user.username.label("sender"),
                                            sender_user.profile,Notifications.id,
                                            Notifications.dm,Notifications.count,
                                            Notifications.receiver)
                                     .join_from(Users,Users.received_notifications)
                                     .join_from(Notifications,Notifications.sender_user.of_type(sender_user))
                                     .where(Users.username == current_user.username))
    return notifications.all()


async def get_notification_by_id(db: AsyncSession, notification_id: int):
    notification = await db.execute(select(Notifications).where(Notifications.dm == notification_id))
    return notification.scalars().first()

async def delete_current_notification(db: AsyncSession, notification: Notifications):
    await db.delete(notification)
    await db.commit()