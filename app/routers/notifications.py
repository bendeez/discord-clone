from fastapi import APIRouter,Depends
from app.schemas import Notification
from app.database import get_db
from sqlalchemy.orm import Session
from app import models,oauth


router = APIRouter()


@router.get("/notifications")
def get_notifications(current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    notifications = db.query(models.Notifications.id, models.Notifications.dm, models.Notifications.count,
                             models.Notifications.receiver, models.Users.username, models.Users.profile).join(
                             models.Users, models.Users.username == models.Notifications.sender).filter(
                             models.Notifications.receiver == current_user.username).all()
    notifications_json = [{"dm":notification.dm,"count":notification.count,"sender":notification.username,"profile":notification.profile} for notification in notifications]
    return notifications_json
@router.delete("/notification")
def delete_notification(notification:Notification, current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    notification = db.query(models.Notifications).filter(models.Notifications.dm == notification.id).first()
    if notification:
        db.delete(notification)
        db.commit()