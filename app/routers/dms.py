from fastapi import APIRouter,Depends,HTTPException,status
from app.schemas import FriendRequest
from app.database import get_db
from app.ServerConnectionManager import server_manager
from sqlalchemy.orm import Session
from sqlalchemy import or_,and_
from app import models,oauth
from kafka import KafkaProducer
import redis
import json

router = APIRouter()
redis_client = redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)
producer = KafkaProducer(bootstrap_servers="localhost:29092")

@router.post("/dm")
def create_dm(friend_request:FriendRequest, current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    already_dm = db.query(models.Dms).filter(or_(and_(models.Dms.sender == current_user.username,
                                                      models.Dms.receiver == friend_request.username),
                                                      and_(models.Dms.receiver == current_user.username,
                                                      models.Dms.sender == friend_request.username))).first()
    if already_dm:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Already a dm")
    dm = models.Dms(sender=current_user.username, receiver=friend_request.username)
    db.add(dm)
    db.commit()
    db.refresh(dm)
    server_manager.add_valid_server_or_dm([dm.sender,dm.receiver], "dm_ids", dm.id)
    dm_json = {"type":"newdm","otheruser":friend_request.username,"username":current_user.username}
    producer.send("notifications",json.dumps(dm_json).encode("utf-8"))

@router.get("/dms")
def get_dms(current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    dms = db.query(models.Users.profile, models.Users.username, models.Dms.id).join(models.Dms, or_(and_(
        models.Dms.receiver == current_user.username, models.Dms.sender == models.Users.username), and_(
        models.Dms.sender == current_user.username, models.Dms.receiver == models.Users.username))).filter(
        models.Users.username != current_user.username).all()
    dms_json = [{"id":dm.id,"username": dm.username,"profile":dm.profile,"status":redis_client.get(f"{dm.username}-status")
    if redis_client.get(f"{dm.username}-status") is not None else "offline"} for dm in dms]
    return dms_json

@router.get("/dm/{dm}")
def get_dm_information(dm:int, current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    in_dm = db.query(models.Dms).filter(or_(and_(models.Dms.sender == current_user.username,models.Dms.id == dm),
                                            and_(models.Dms.receiver == current_user.username,models.Dms.id == dm))).first()
    if not in_dm:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not a part of this dm")
    dm = db.query(models.Users.profile, models.Users.username, models.Dms.id).join(models.Dms, and_(models.Dms.id == dm, or_(and_(
        models.Dms.receiver == current_user.username, models.Dms.sender == models.Users.username), and_(
        models.Dms.sender == current_user.username, models.Dms.receiver == models.Users.username)))).filter(
        models.Users.username != current_user.username).first()
    dm_json = {"id":dm.id,"username":dm.username,"profile":dm.profile,"status":redis_client.get(f"{dm.username}-status")
                if redis_client.get(f"{dm.username}-status") is not None else "offline"}
    return dm_json

@router.get("/dmmessages/{dm}")
def get_dm_messages(dm:int, current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    in_dm = db.query(models.Dms).filter(or_(and_(models.Dms.sender == current_user.username, models.Dms.id == dm),
                                            and_(models.Dms.receiver == current_user.username,models.Dms.id == dm))).first()
    if not in_dm:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this dm")
    dm_messages = db.query(models.Dm_Messages.dm, models.Dm_Messages.username, models.Dm_Messages.link,models.Dm_Messages.text, models.Dm_Messages.file,
                        models.Dm_Messages.created_date, models.Dm_Messages.filetype,models.Dm_Messages.serverinviteid,models.Server.name,
                        models.Server.profile.label("serverprofile"),models.Users.profile)\
                        .outerjoin(models.Server,models.Server.id == models.Dm_Messages.serverinviteid).join\
                        (models.Users,models.Dm_Messages.username == models.Users.username)\
                        .filter(models.Dm_Messages.dm == dm).order_by(models.Dm_Messages.id).all()
    dm_messages_json = [{"dm":message.dm,"username":message.username,"link":message.link,"text":message.text,"file":message.file,"filetype":message.filetype,
                         "date":message.created_date,"profile":message.profile,"servername":message.name,"serverprofile":message.serverprofile}
                        for message in dm_messages]
    return dm_messages_json
