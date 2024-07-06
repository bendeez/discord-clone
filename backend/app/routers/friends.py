from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.friends import FriendsOut, FriendIn, FriendCreated
from app.db.database import get_db
from app.core.oauth import get_current_user
from app.models.user import Users
from app.crud.friend_requests import check_friend_request,get_friend_request
from app.crud.friends import create_friend, get_all_friends, check_already_friends, get_friend, delete_current_friend
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

router = APIRouter()


@router.post("/friend", status_code=status.HTTP_201_CREATED, response_model=FriendCreated)
async def accept_friend_request(friend: FriendIn, current_user: Users = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    current_friend_request = await get_friend_request(db=db, current_user=current_user,
                                                        remote_user_username=friend.username)
    if current_friend_request is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Friend request already deleted")
    if current_friend_request.sender == current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sender of friend request cannot accept it")
    friend = await create_friend(db=db, current_user=current_user,
                        remote_user_username=friend.username,current_friend_request=current_friend_request)
    return friend


@router.get("/friends", response_model=List[FriendsOut])
async def get_friends(current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    friends = await get_all_friends(db=db, current_user=current_user)
    return friends


@router.delete("/friend", status_code=status.HTTP_204_NO_CONTENT)
async def delete_friend(friend: FriendIn, current_user: Users = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    current_friend = await get_friend(db=db, current_user=current_user,
                                                  remote_user_username=friend.username)
    if current_friend is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not friends with this user")
    await delete_current_friend(db=db,friend=current_friend)