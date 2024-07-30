from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import aliased
from sqlalchemy import and_
from app.models.notifications import Notifications
from app.models.user import Users
from app.schemas.websocket_data.notification_message import Notification
from base import BaseService


class NotificationService(BaseService):

    async def get_all_notifications(self, db: AsyncSession, current_user: Users):
        sender_user = aliased(Users, name="sender_user")
        notifications = await db.execute(
            select(
                sender_user.username.label("sender"),
                sender_user.profile,
                Notifications.id,
                Notifications.dm,
                Notifications.count,
                Notifications.receiver,
            )
            .join_from(Users, Users.received_notifications)
            .join_from(Notifications, Notifications.sender_user.of_type(sender_user))
            .where(Users.username == current_user.username)
        )
        return notifications.all()

    async def get_notification_by_dm_id(
        self, db: AsyncSession, notification_dm_id: int
    ):
        notification = await db.execute(
            select(Notifications).where(Notifications.dm == notification_dm_id)
        )
        return notification.scalars().first()

    async def save_message_notification(self, notification: Notification):
        stmt = select(Notifications).where(
                    and_(
                        Notifications.dm == notification.dm, Notifications.receiver == notification.receiver
                    )
                )
        receiver_notifications = await self.transaction.execute(stmt)
        receiver_notifications = receiver_notifications.scalars().first()
        if receiver_notifications is not None:
            count = receiver_notifications.count + 1
            receiver_notifications.count = count
            return receiver_notifications
        else:
            count = 1
            notification.count = count
            notification = Notifications.save_notification(notification.model_dump())
            notification = await self.transaction.create(model_instance=notification)
            return notification

    async def delete_current_notification(self, notification: Notifications):
        await self.transaction.delete(notification)
