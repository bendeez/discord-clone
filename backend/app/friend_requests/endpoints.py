from fastapi import APIRouter, Depends, HTTPException, status
from app.friend_requests.schemas import (
    FriendRequestIn,
    FriendRequestOut,
    FriendRequestCreated,
)
from app.db.database import get_db
from app.friend_requests.service import (
    check_friend_request,
    create_friend_request,
    get_all_friend_requests,
    get_friend_request,
    delete_current_friend_request,
)
from app.friends.service import check_already_friends
from app.user.service import check_user_exists
from app.user.models import Users
from app.core.oauth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

friend_request_router = APIRouter()


@friend_request_router.post(
    "/friendrequest",
    status_code=status.HTTP_201_CREATED,
    response_model=FriendRequestCreated,
)
async def send_friend_request(
    friend_request: FriendRequestIn,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if friend_request.username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot send friend request to yourself",
        )
    user_exists = await check_user_exists(
        db=db, remote_user_username=friend_request.username
    )
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User does not exist"
        )
    already_friend_request = await check_friend_request(
        db=db, current_user=current_user, remote_user_username=friend_request.username
    )
    if already_friend_request:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Friend request already sent"
        )
    already_friends = await check_already_friends(
        db=db, current_user=current_user, remote_user_username=friend_request.username
    )
    if already_friends:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already friends with that user",
        )
    friend_request = await create_friend_request(
        db=db, current_user=current_user, remote_user_username=friend_request.username
    )
    return friend_request


@friend_request_router.get("/friendrequests", response_model=List[FriendRequestOut])
async def get_friend_requests(
    current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    friend_requests = await get_all_friend_requests(db=db, current_user=current_user)
    return friend_requests


@friend_request_router.delete("/friendrequest", status_code=status.HTTP_204_NO_CONTENT)
async def delete_friend_request(
    friend_request: FriendRequestIn,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_friend_request = await get_friend_request(
        db=db, current_user=current_user, remote_user_username=friend_request.username
    )
    if current_friend_request is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Friend request does not exist"
        )
    await delete_current_friend_request(db=db, friend_request=current_friend_request)
