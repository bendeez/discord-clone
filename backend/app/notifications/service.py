from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import aliased, selectinload
from sqlalchemy import and_
from app.notifications.models import Notifications
from app.user.models import Users
from app.websocket_server.schemas.notification_message import Notification
from base import BaseService


class NotificationService(BaseService):
    async def get_all_notifications(self, current_user: Users):
        sender_user = aliased(Users, name="sender_user")
        notifications = await self.transaction.execute(
                            select(
                                Notifications, sender_user
                            )
                            .where(Notifications.receiver_user == current_user)
                            .options(selectinload(Notifications.sender_user))
                        )
        return notifications.all()

    async def get_notification_by_dm_id(
        self, db: AsyncSession, notification_dm_id: int
    ):
        notification = await db.execute(
            select(Notifications).where(Notifications.dm == notification_dm_id)
        )
        return notification.scalars().first()

    async def save_notification_message(self, notification: Notification):
        stmt = select(Notifications).where(
            and_(
                Notifications.dm == notification.dm,
                Notifications.receiver == notification.receiver,
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
            notification = Notifications(**notification.model_dump(include={column.name for column in Notifications.columns}))
            notification = await self.transaction.create(model_instance=notification)
            return notification

    async def delete_current_notification(self, notification: Notifications):
        await self.transaction.delete(notification)
