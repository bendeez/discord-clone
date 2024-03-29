from fastapi import APIRouter,Depends
from schemas import Notification
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models,oauth


router = APIRouter()


@router.get("/notifications")
async def get_notifications(current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    notifications = await db.execute(select(models.Notifications.id, models.Notifications.dm, models.Notifications.count,
                             models.Notifications.receiver, models.Users.username, models.Users.profile).join(
                             models.Users, models.Users.username == models.Notifications.sender).filter(
                             models.Notifications.receiver == current_user.username))
    notifications = notifications.all()
    notifications_json = [{"dm":notification.dm,"count":notification.count,"sender":notification.username,"profile":notification.profile} for notification in notifications]
    return notifications_json
@router.delete("/notification")
async def delete_notification(notification:Notification, current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    notification = await db.execute(select(models.Notifications).filter(models.Notifications.dm == notification.id))
    notification = notification.scalars().first()
    if notification:
        await db.delete(notification)
        await db.commit()