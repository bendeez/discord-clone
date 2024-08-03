from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from app.user.schemas import (
    UserCreate,
    UserIn,
    UserOut,
    UserCreated,
    UserUpdateProfile,
)
from app.user.service import (
    check_user_exists,
    create_new_user,
    update_current_profile_picture,
)
from app.auth.schemas import TokenCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.oauth import get_current_user, create_access_token
from app.user.models import Users

user_router = APIRouter()


@user_router.post(
    "/user", status_code=status.HTTP_201_CREATED, response_model=UserCreated
)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):

    user = await create_new_user(
        db=db, user=UserCreate
    )
    return user


@user_router.post("/login", response_model=TokenCreate)
async def login(user: UserIn, db: AsyncSession = Depends(get_db)):

    token = create_access_token(data={"username": existing_user.username})
    return token


@user_router.get("/usercredentials", response_model=UserOut)
async def get_user_credentials(current_user: Users = Depends(get_current_user)):
    return current_user


@user_router.put("/profilepicture", response_model=UserUpdateProfile)
async def update_profile_picture(
    file: UploadFile,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile_picture = await update_current_profile_picture(
        db=db, current_user=current_user, file=file
    )
    return profile_picture
