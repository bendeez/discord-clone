from fastapi import APIRouter,Depends,HTTPException,status,UploadFile,Request
from app.schemas import User,Login,Status
from app.database import get_db
from sqlalchemy.orm import Session
from app import models,utils,oauth
from kafka import KafkaProducer
import json
import uuid
import firebase


router = APIRouter()
producer = KafkaProducer(bootstrap_servers="localhost:29092")
firebase_config = FIREBASE_CONFIG
firebase_app = firebase.initialize_app(firebase_config)
firebase_storage = firebase_app.storage()

@router.post("/user")
def create_user(user:User,db:Session = Depends(get_db)):
    existing_user = db.query(models.Users).filter(models.Users.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists")
    password = utils.hash(user.password)
    new_user = models.Users(username=user.username, email=user.email, password=password)
    db.add(new_user)
    db.commit()

@router.post("/login")
def login(login:Login,db:Session = Depends(get_db)):
    existing_user = db.query(models.Users).filter(models.Users.username == login.username).first()
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    verify = utils.verify(login.password, existing_user.password)
    if not verify:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = oauth.create_access_token(data={"username":existing_user.username})
    return {"access_token":token}

@router.get("/usercredentials")
def get_user_credentials(current_user: models.Users = Depends(oauth.get_current_user)):
    return {"username":current_user.username,"profile":current_user.profile}

@router.put("/status")
def change_status(status:Status, current_user: models.Users = Depends(oauth.get_current_user)):
    status_json = {"type":"status","status":status.status,"username":current_user.username}
    producer.send("notifications", json.dumps(status_json).encode("utf-8"))

@router.put("/profilepicture")
def update_profile_picture(file:UploadFile, current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    file_type = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_type}"
    firebase_storage.child(filename).put(file.file.read())
    current_user.profile = f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"
    db.commit()
    return {"profile":f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"}