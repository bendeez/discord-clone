from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from app.schemas.user import (
    UserCreate,
    UserIn,
    UserOut,
    UserCreated,
    UserUpdateProfile,
)
from app.services.user import (
    check_user_exists,
    create_new_user,
    update_current_profile_picture,
    get_user,
)
from app.schemas.authentication import TokenCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.oauth import get_current_user, create_access_token
from app.utils import verify
from app.models.user import Users

router = APIRouter()


@router.post("/user", status_code=status.HTTP_201_CREATED, response_model=UserCreated)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await check_user_exists(db=db, remote_user_username=user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    user = await create_new_user(
        db=db, username=user.username, email=user.email, password=user.password
    )
    return user


@router.post("/login", response_model=TokenCreate)
async def login(user: UserIn, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user(db=db, remote_user_username=user.username)
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    verify_password = verify(user.password, existing_user.password)
    if not verify_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = create_access_token(data={"username": existing_user.username})
    return token


@router.get("/usercredentials", response_model=UserOut)
async def get_user_credentials(current_user: Users = Depends(get_current_user)):
    return current_user


@router.put("/profilepicture", response_model=UserUpdateProfile)
async def update_profile_picture(
    file: UploadFile,
    current_user: Users = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile_picture = await update_current_profile_picture(
        db=db, current_user=current_user, file=file
    )
    return profile_picture
