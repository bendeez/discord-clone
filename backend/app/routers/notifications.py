from fastapi import APIRouter, Depends, status
from app.schemas.notifications import NotificationIn, NotificationOut
from app.db.database import get_db
from app.core.oauth import get_current_user
from app.crud.notifications import get_all_notifications, get_notification_by_id
from app.models.user import Users
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

router = APIRouter()


@router.get("/notifications", response_model=List[NotificationOut])
async def get_notifications(current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
        only dm message notifications
    """
    notifications = await get_all_notifications(db=db, current_user=current_user)
    return notifications


@router.delete("/notification", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification: NotificationIn, current_user: Users = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)):
    """
        only dm message notifications
    """
    notification = await get_notification_by_id(db=db, notification_id=notification.id)
    if notification:
        await db.delete(notification)
        await db.commit()
