from fastapi import APIRouter,Depends
from schemas import NotificationIn,NotificationOut
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models,oauth
from typing import List


router = APIRouter()


@router.get("/notifications",response_model=List[NotificationOut])
async def get_notifications(current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    notifications = await db.execute(select(models.Notifications.id, models.Notifications.dm, models.Notifications.count,
                             models.Notifications.receiver, models.Users.username.label("sender"), models.Users.profile).join(
                             models.Users, models.Users.username == models.Notifications.sender).filter(
                             models.Notifications.receiver == current_user.username))
    notifications = notifications.all()
    return notifications
@router.delete("/notification")
async def delete_notification(notification:NotificationIn, current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    notification = await db.execute(select(models.Notifications).filter(models.Notifications.dm == notification.id))
    notification = notification.scalars().first()
    if notification:
        await db.delete(notification)
        await db.commit()