from fastapi import APIRouter,Depends,HTTPException,status
from schemas import FriendRequestIn,FriendRequestOut
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy import or_,and_,select
import models,oauth
import redis
from typing import List

router = APIRouter()
redis_client = redis.Redis(host="redis",port=6379,db=0,decode_responses=True)

@router.post("/friendrequest")
async def send_friend_request(friend_request:FriendRequestIn, current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    if friend_request.username == current_user.username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Cannot send friend request to yourself")
    user_exists = await db.execute(select(models.Users).filter(models.Users.username == friend_request.username))
    user_exists = user_exists.scalars().first()
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User does not exist")
    already_sent = await db.execute(select(models.FriendRequests).filter(or_(and_(models.FriendRequests.sender == friend_request.username,
                                                                   models.FriendRequests.receiver == current_user.username),
                                                              and_(
                                                                  models.FriendRequests.receiver == friend_request.username,
                                                                  models.FriendRequests.sender == current_user.username))))
    already_sent = already_sent.scalars().first()
    if already_sent:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Friend request already sent")
    already_friends = await db.execute(select(models.Friends).filter(or_(and_(models.Friends.sender == current_user.username,
                                                               models.Friends.receiver == friend_request.username),
                                                          and_(models.Friends.receiver == current_user.username,
                                                               models.Friends.sender == friend_request.username))))
    already_friends = already_friends.scalars().all()
    if already_friends:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already friends with that user")
    request = models.FriendRequests(sender=current_user.username, receiver=friend_request.username)
    db.add(request)
    await db.commit()

@router.get("/friendrequests",response_model=List[FriendRequestOut])
async def get_friend_requests(current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    receiver_user = aliased(models.Users,name="receiver_user")
    sender_user = aliased(models.Users, name="sender_user")
    friend_requests = await db.execute(select(models.FriendRequests.receiver,models.FriendRequests.sender,receiver_user.profile.label("receiverprofile"),sender_user.profile.label("senderprofile"))\
                                .join(receiver_user,receiver_user.username == models.FriendRequests.receiver).join(sender_user,sender_user.username == models.FriendRequests.sender).filter(
                                or_(models.FriendRequests.receiver == current_user.username,models.FriendRequests.sender == current_user.username)))
    friend_requests = friend_requests.all()
    return friend_requests
@router.delete("/friendrequest")
async def delete_friend_request(friend_request:FriendRequestIn, current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    already_friend_request = await db.execute(select(models.FriendRequests).filter(or_(and_(models.FriendRequests.sender == current_user.username, models.FriendRequests.receiver == friend_request.username),
                                                                        and_(models.FriendRequests.receiver == current_user.username,models.FriendRequests.sender == friend_request.username))))
    already_friend_request = already_friend_request.scalars().first()
    if not already_friend_request:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already deleted")
    await db.delete(already_friend_request)
    await db.commit()