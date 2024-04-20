from fastapi import APIRouter,Depends,HTTPException,status
from app.schemas.friend_requests import FriendRequestIn,FriendRequestOut
from app.db.database import get_db
from app.crud.friend_requests import check_friend_request,create_friend_request,get_all_friend_requests
from app.crud.friends import check_already_friends
from app.crud.user import check_user_exists
from app.models.user import Users
from app.core.oauth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

router = APIRouter()

@router.post("/friendrequest")
async def send_friend_request(friend_request:FriendRequestIn, current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    if friend_request.username == current_user.username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Cannot send friend request to yourself")
    user_exists = await check_user_exists(db=db,remote_user_username=friend_request.username)
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User does not exist")
    already_friend_request = await check_friend_request(db=db,current_user_username=current_user.username,remote_user_username=friend_request.username)
    if already_friend_request:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already sent")
    already_friends = await check_already_friends(db=db, current_user_username=current_user.username,remote_user_username=friend_request.username)
    if already_friends:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You are already friends with that user")
    await create_friend_request(db=db, current_user_username=current_user.username,remote_user_username=friend_request.username)

@router.get("/friendrequests",response_model=List[FriendRequestOut])
async def get_friend_requests(current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    friend_requests = await get_all_friend_requests(db=db,current_user_username=current_user.username)
    return friend_requests
@router.delete("/friendrequest")
async def delete_friend_request(friend_request:FriendRequestIn, current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    friend_request = await check_friend_request(db=db,current_user_username=current_user.username,remote_user_username=friend_request.username)
    if not friend_request:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already deleted")
    await db.delete(friend_request)
    await db.commit()