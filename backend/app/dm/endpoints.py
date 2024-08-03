from fastapi import APIRouter, Depends, HTTPException, status
from app.dm.schemas import (
    DmsOut,
    DmMessagesOut,
    DmInformationOut,
    DmCreated,
    DmUsernameIn,
)
from app.database import get_db
from app.auth.service import get_current_user
from app.user.models import Users
from sqlalchemy.ext.asyncio import AsyncSession
from app.dm.service import DmService
from app.friend.service import FriendService
from app.user.service import UserService
from typing import List

dm_router = APIRouter()


@dm_router.post("/dm", status_code=status.HTTP_201_CREATED, response_model=DmCreated)
async def create_dm(
    dm_user: DmUsernameIn,
    current_user: Users = Depends(get_current_user),
    dm_service: DmService = Depends(DmService),
    user_service: UserService = Depends(UserService),
    friend_service: FriendService = Depends(FriendService),
):
    if dm_user.username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot create a dm with yourself",
        )
    user_exists = await user_service.get_user_by_username(
        remote_user_username=dm_user.username
    )
    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exists"
        )
    already_dm = await dm_service.get_dm_by_users(
        current_user=current_user, remote_user_username=dm_user.username
    )
    if already_dm:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="There is already a dm"
        )
    friend = await friend_service.get_friend_by_users(
        current_user=current_user, remote_user_username=dm_user.username
    )
    dm = await dm_service.create_new_dm(
        current_user=current_user, remote_user_username=dm_user.username, friend=friend
    )
    await dm_service.send_new_dm_notification(current_user=current_user, dm=dm)
    return dm


@dm_router.get("/dm", response_model=List[DmsOut])
async def get_dms(
    current_user: Users = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    dms = await get_all_dms(db=db, current_user=current_user)
    return dms


@dm_router.get("/dm/{dm_id}", response_model=DmInformationOut)
async def get_dm_information(
    dm_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    dm_information = await get_all_dm_information(
        db=db, current_user=current_user, dm_id=dm_id
    )
    if dm_information is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a part of this dm",
        )
    return dm_information


@dm_router.get("/dmmessages/{dm_id}", response_model=List[DmMessagesOut])
async def get_dm_messages(
    dm_id: int,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    in_dm = await check_user_in_dm(db=db, current_user=current_user, dm_id=dm_id)
    if not in_dm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a part of this dm",
        )
    dm_messages = await get_all_dm_messages(db=db, dm_id=dm_id)
    return dm_messages
