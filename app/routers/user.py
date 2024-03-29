from fastapi import APIRouter,Depends,HTTPException,status,UploadFile
from schemas import User,Login
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models,utils,oauth
import uuid
import firebase
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()
firebase_config = {
  "apiKey": os.environ.get("API_KEY"),
  "authDomain": "discord-83cd2.firebaseapp.com",
  "databaseURL": "https://discord-83cd2-default-rtdb.firebaseio.com",
  "projectId": "discord-83cd2",
  "storageBucket": "discord-83cd2.appspot.com",
  "messagingSenderId": "951586420649",
  "appId": "1:951586420649:web:c95ce57fdd3766492336b8",
  "measurementId": "G-GLYJ5PKYF7"
}
firebase_app = firebase.initialize_app(firebase_config)
firebase_storage = firebase_app.storage()

@router.post("/user")
async def create_user(user:User,db:AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(models.Users).filter(models.Users.username == user.username))
    existing_user = existing_user.scalars().first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists")
    password = utils.hash(user.password)
    new_user = models.Users(username=user.username, email=user.email, password=password)
    db.add(new_user)
    await db.commit()

@router.post("/login")
async def login(login:Login,db:AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(models.Users).filter(models.Users.username == login.username))
    existing_user = existing_user.scalars().first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    verify = utils.verify(login.password, existing_user.password)
    if not verify:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = oauth.create_access_token(data={"username":existing_user.username})
    return {"access_token":token}

@router.get("/usercredentials")
async def get_user_credentials(current_user: models.Users = Depends(oauth.get_current_user)):
    return {"username":current_user.username,"profile":current_user.profile}

@router.put("/profilepicture")
async def update_profile_picture(file:UploadFile, current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    file_type = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_type}"
    await asyncio.to_thread(firebase_storage.child(filename).put,file.file.read())
    current_user.profile = f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"
    await db.commit()
    return {"profile":f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"}