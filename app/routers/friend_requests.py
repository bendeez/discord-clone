from fastapi import APIRouter,Depends,HTTPException,status
from app.schemas import FriendRequest
from app.database import get_db
from sqlalchemy.orm import Session,aliased
from sqlalchemy import or_,and_
from app import models,oauth
from kafka import KafkaProducer
import redis

router = APIRouter()
redis_client = redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)
producer = KafkaProducer(bootstrap_servers="localhost:29092")

@router.post("/friendrequest")
def send_friend_request(friend_request:FriendRequest, current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    if friend_request.username == current_user.username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Cannot send friend request to yourself")
    user_exists = db.query(models.Users).filter(models.Users.username == friend_request.username).first()
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User does not exist")
    already_sent = db.query(models.FriendRequests).filter(or_(and_(models.FriendRequests.sender == friend_request.username,
                                                                   models.FriendRequests.receiver == current_user.username),
                                                              and_(
                                                                  models.FriendRequests.receiver == friend_request.username,
                                                                  models.FriendRequests.sender == current_user.username))).first()
    if already_sent:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Friend request already sent")
    already_friends = db.query(models.Friends).filter(or_(and_(models.Friends.sender == current_user.username,
                                                               models.Friends.receiver == friend_request.username),
                                                          and_(models.Friends.receiver == current_user.username,
                                                               models.Friends.sender == friend_request.username))).first()
    if already_friends:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already friends with that user")
    request = models.FriendRequests(sender=current_user.username, receiver=friend_request.username)
    db.add(request)
    db.commit()

@router.get("/friendrequests")
def get_friend_requests(current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    receiver_user = aliased(models.Users,name="receiver_user")
    sender_user = aliased(models.Users, name="sender_user")
    friend_requests = db.query(models.FriendRequests.receiver,models.FriendRequests.sender,models.Users.profile,receiver_user.profile.label("receiver_profile"),sender_user.profile.label("sender_profile"))\
                                .join(receiver_user,receiver_user.username == models.FriendRequests.receiver).join(sender_user,sender_user.username == models.FriendRequests.sender).filter(
                                or_(models.FriendRequests.receiver == current_user.username,models.FriendRequests.sender == current_user.username)).distinct(models.FriendRequests.receiver,models.FriendRequests.sender).all()
    friend_requests_json = [{"sender":friend_request.sender,"receiver":friend_request.receiver,"receiverprofile":friend_request.receiver_profile,"senderprofile":friend_request.sender_profile} for friend_request in friend_requests]
    return friend_requests_json
@router.delete("/friendrequest")
def delete_friend_request(friend_request:FriendRequest, current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    already_friend_request = db.query(models.FriendRequests).filter(or_(and_(models.FriendRequests.sender == current_user.username, models.FriendRequests.receiver == friend_request.username),
                                                                        and_(models.FriendRequests.receiver == current_user.username,models.FriendRequests.sender == friend_request.username))).first()
    if not already_friend_request:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already deleted")
    db.delete(already_friend_request)
    db.commit()