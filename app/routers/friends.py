from fastapi import APIRouter,Depends,HTTPException,status
from schemas import FriendRequest
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_,and_,select
import models,oauth
import redis

router = APIRouter()
redis_client = redis.Redis(host="redis",port=6379,db=0,decode_responses=True)


@router.post("/friend")
async def accept_friend_request(friend_request:FriendRequest, current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    already_friend_request = await db.execute(select(models.FriendRequests).filter(or_(
        models.FriendRequests.sender == current_user.username and models.FriendRequests.receiver == friend_request.username,
        models.FriendRequests.receiver == current_user.username and models.FriendRequests.sender == friend_request.username)))
    already_friend_request = already_friend_request.scalars().first()
    if not already_friend_request:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already deleted")
    await db.delete(already_friend_request)
    friend = models.Friends(sender=friend_request.username, receiver=current_user.username)
    db.add(friend)
    await db.commit()
@router.get("/friends")
async def get_friends(current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    friends = await db.execute(select(models.Users.profile, models.Users.username,models.Dms.id).join(models.Friends, or_(and_(
        models.Friends.receiver == current_user.username, models.Friends.sender == models.Users.username), and_(
        models.Friends.sender == current_user.username, models.Friends.receiver == models.Users.username))).outerjoin(models.Dms,or_(and_(models.Dms.sender == current_user.username,models.Dms.receiver == models.Users.username),
                                                                                                            and_(models.Dms.receiver == current_user.username,models.Dms.sender == models.Users.username))))
    friends = friends.all()
    friends_json = [{"username":friend.username,"profile":friend.profile,"dmid":friend.id,"status":redis_client.get(f"{friend.username}-status") if redis_client.get(f"{friend.username}-status") else "offline"} for friend in friends]
    return friends_json
@router.delete("/friend")
async def accept_friend_request(friend_request:FriendRequest, current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    already_friends = await db.execute(select(models.Friends).filter(or_(and_(models.Friends.sender == current_user.username,
                                                               models.Friends.receiver == friend_request.username),
                                                          and_(models.Friends.receiver == current_user.username,
                                                               models.Friends.sender == friend_request.username))))
    already_friends = already_friends.scalars().first()
    if not already_friends:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You are not friends with this user")
    await db.delete(already_friends)
    await db.commit()
