from fastapi import APIRouter,Depends,HTTPException,status
from app.schemas import FriendRequest
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_,and_
from app import models,oauth
import redis

router = APIRouter()
redis_client = redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)


@router.post("/friend")
def accept_friend_request(friend_request:FriendRequest, current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    already_friend_request = db.query(models.FriendRequests).filter(or_(
        models.FriendRequests.sender == current_user.username and models.FriendRequests.receiver == friend_request.username,
        models.FriendRequests.receiver == current_user.username and models.FriendRequests.sender == friend_request.username)).first()
    if not already_friend_request:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already deleted")
    db.delete(already_friend_request)
    friend = models.Friends(sender=friend_request.username, receiver=current_user.username)
    db.add(friend)
    db.commit()
@router.get("/friends")
def get_friends(current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    friends = db.query(models.Users.profile, models.Users.username,models.Dms.id).join(models.Friends, or_(and_(
        models.Friends.receiver == current_user.username, models.Friends.sender == models.Users.username), and_(
        models.Friends.sender == current_user.username, models.Friends.receiver == models.Users.username))).join(models.Dms,or_(and_(models.Dms.sender == current_user.username,models.Dms.receiver == models.Users.username),
                                                                                                            and_(models.Dms.receiver == current_user.username,models.Dms.sender == models.Users.username))).all()
    friends_json = [{"username":friend.username,"profile":friend.profile,"dmid":friend.id,"status":redis_client.get(f"{friend.username}-status") if redis_client.get(f"{friend.username}-status") else "offline"} for friend in friends]
    return friends_json
@router.delete("/friend")
def accept_friend_request(friend_request:FriendRequest, current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    already_friends = db.query(models.Friends).filter(or_(and_(models.Friends.sender == current_user.username,
                                                               models.Friends.receiver == friend_request.username),
                                                          and_(models.Friends.receiver == current_user.username,
                                                               models.Friends.sender == friend_request.username))).first()
    if not already_friends:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You are not friends with this user")
    db.delete(already_friends)
    db.commit()
