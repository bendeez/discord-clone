from fastapi import APIRouter,Depends,HTTPException,status
from app.schemas.friends import FriendsOut
from app.schemas.friend_requests import FriendRequestIn
from app.db.database import get_db
from app.core.oauth import get_current_user
from app.models.user import Users
from app.crud.friend_requests import check_friend_request
from app.crud.friends import create_friend,get_all_friends,check_already_friends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

router = APIRouter()


@router.post("/friend")
async def accept_friend_request(friend_request:FriendRequestIn, current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    already_friend_request = await check_friend_request(db=db,current_user_username=current_user.username,remote_user_username=friend_request.username)
    if not already_friend_request:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already deleted")
    await db.delete(already_friend_request)
    await create_friend(db=db,current_user_username=current_user.username,remote_user_username=friend_request.username)

@router.get("/friends",response_model=List[FriendsOut])
async def get_friends(current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    friends = await get_all_friends(db=db,current_user_username=current_user.username)
    return friends
@router.delete("/friend")
async def accept_friend_request(friend_request:FriendRequestIn, current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    already_friends = await check_already_friends(db=db,current_user_username=current_user.username,remote_user_username=friend_request.username)
    if not already_friends:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You are not friends with this user")
    await db.delete(already_friends)
    await db.commit()
