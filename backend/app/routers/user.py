from fastapi import APIRouter,Depends,HTTPException,status,UploadFile
from app.schemas.user import UserCreate,UserIn,UserOut
from app.crud.user import check_user_exists,create_new_user,update_current_profile_picture
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.oauth import get_current_user,create_access_token
from app.core.utils import hash,verify
from app.models.user import Users
from app.firebase.firebase_startup import firebase_storage
import uuid
import asyncio


router = APIRouter()

@router.post("/user")
async def create_user(user:UserCreate,db:AsyncSession = Depends(get_db)):
    existing_user = await check_user_exists(db=db,remote_user_username=user.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists")
    password = hash(user.password)
    await create_new_user(db=db,username=user.username,email=user.email,password=password)

@router.post("/login")
async def login(user:UserIn,db:AsyncSession = Depends(get_db)):
    existing_user = await check_user_exists(db=db,remote_user_username=user.username)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    verify_password = verify(user.password, existing_user.password)
    if not verify_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(data={"username":existing_user.username})
    return {"access_token":token}

@router.get("/usercredentials",response_model=UserOut)
async def get_user_credentials(current_user: Users = Depends(get_current_user)):
    return current_user

@router.put("/profilepicture")
async def update_profile_picture(file:UploadFile, current_user: Users = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    file_type = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_type}"
    await asyncio.to_thread(firebase_storage.child(filename).put,file.file.read())
    await update_current_profile_picture(db=db,current_user=current_user,filename=filename)
    return {"profile":f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"}