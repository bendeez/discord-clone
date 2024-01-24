from fastapi import APIRouter,Depends,WebSocket,WebSocketDisconnect,HTTPException,status
from app.schemas import Server,UserServer
from app.database import get_db
from app.ServerConnectionManager import server_manager
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app import models,oauth
from kafka import KafkaProducer
import redis
import uuid
import base64
import firebase
import json


router = APIRouter()
redis_client = redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)
producer = KafkaProducer(bootstrap_servers="localhost:29092")
firebase_config = FIREBASE_CONFIG
firebase_app = firebase.initialize_app(firebase_config)
firebase_storage = firebase_app.storage()


@router.websocket("/ws/server/{token}")
async def server(token:str,websocket:WebSocket,current_user:models.Users = Depends(oauth.get_websocket_user),db:Session = Depends(get_db)):
    await server_manager.connect(websocket,current_user)
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "file" or data["type"] == "textandfile":
                file_type = data["filetype"]
                filename = f"{uuid.uuid4()}.{file_type}"
                encoded_image = base64.b64decode(data["file"].split(",")[1])
                firebase_storage.child(filename).put(encoded_image)
                data["file"] = f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"
                data["filetype"] = file_type
                await server_manager.broadcast(websocket, data, current_user)
            elif data["type"] == "link":
                data["link"] = str(uuid.uuid4())
                await server_manager.broadcast(websocket, data, current_user)
            else:
                await server_manager.broadcast(websocket, data, current_user)
            producer.send("messages",json.dumps(data).encode("utf-8"))
            if data["type"] != "announcement" and token != "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c":
                producer.send("notifications",json.dumps(data).encode("utf-8"))
    except WebSocketDisconnect:
        server_manager.disconnect(websocket,current_user)

@router.post("/server")
def create_server(server:Server,current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    if server.profile:
        filename = f"{uuid.uuid4()}.jpg"
        encoded_image = base64.b64decode(server.profile.split(",")[1])
        firebase_storage.child(filename).put(encoded_image)
        new_server = models.Server(name=server.name,profile=f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8",owner=current_user.username)
        db.add(new_server)
        db.commit()
    else:
        new_server = models.Server(name=server.name,owner=current_user.username)
        db.add(new_server)
        db.commit()
    db.refresh(new_server)
    new_server_user = models.Server_User(server_id=new_server.id,username=current_user.username)
    db.add(new_server_user)
    db.commit()
    server_manager.add_valid_server_or_dm([new_server_user.username],"server_ids",new_server_user.server_id)
@router.get("/servers")
def get_servers(current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    servers = db.query(models.Server_User.server_id,models.Server.owner,models.Server.profile,models.Server.id,models.Server.name)\
             .join(models.Server,models.Server.id == models.Server_User.server_id).filter(models.Server_User.username == current_user.username).all()
    servers_json = [{"id":server.id,"owner":server.owner,"profile":server.profile,"name":server.name} for server in servers]
    return servers_json
@router.get("/server/{id}")
def get_server_information(id:int,current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    in_server = db.query(models.Server_User).filter(and_(models.Server_User.server_id == id,models.Server_User.username == current_user.username)).first()
    if not in_server:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this server")
    server = db.query(models.Server).filter(models.Server.id == id).first()
    return server
@router.get("/server/users/{id}")
def get_server_users(id:int,current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    in_server = db.query(models.Server_User).filter(and_(models.Server_User.server_id == id, models.Server_User.username == current_user.username)).first()
    if not in_server:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this server")
    users = db.query(models.Server_User.username,models.Users.username,models.Users.profile).join(models.Users,models.Server_User.username == models.Users.username).filter(models.Server_User.server_id == id).all()
    users_json = [{"username":user.username,"profile":user.profile,"status":redis_client.get(f"{user.username}-status") if redis_client.get(f"{user.username}-status") is not None else "offline"} for user in users]
    return users_json
@router.post("/server/user")
def join_server(user_server:UserServer,current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    server_id = redis_client.get(user_server.link)
    if server_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invite link has expired")
    already_in_server = db.query(models.Server_User).filter(and_(models.Server_User.username == current_user.username,models.Server_User.server_id == server_id)).first()
    if already_in_server:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="You are already a part of this server")
    server_user = models.Server_User(username=current_user.username,server_id=server_id)
    db.add(server_user)
    db.commit()
    server_user_json = {"type":"announcement","serverid":server_id,"username":current_user.username}
    server_manager.add_valid_server_or_dm(current_user.username,"server_ids",server_id)
    producer.send("notifications", json.dumps(server_user_json).encode("utf-8"))
    return {"serverid":server_id}
@router.get("/servermessages/{server}")
def get_server_messages(server:int, current_user: models.Users = Depends(oauth.get_current_user), db:Session = Depends(get_db)):
    in_server = db.query(models.Server_User).filter(and_(models.Server_User.server_id == server,models.Server_User.username == current_user.username)).first()
    if not in_server:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this server")
    server_messages = db.query(models.Server_Messages.announcement,models.Server_Messages.server,models.Server_Messages.username,
                        models.Server_Messages.text, models.Server_Messages.file,
                        models.Server_Messages.created_date, models.Server_Messages.filetype,
                        models.Users.profile).join(models.Users,models.Server_Messages.username == models.Users.username).filter(
                        models.Server_Messages.server == server).order_by(models.Server_Messages.id).all()
    server_messages_json = [{"announcement":message.announcement,"server":message.server,"username":message.username,"text":message.text,"file":message.file,"filetype":message.filetype,"date":message.created_date,"profile":message.profile} for message in server_messages]
    return server_messages_json