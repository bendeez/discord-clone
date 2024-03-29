from fastapi import APIRouter,Depends,WebSocket,WebSocketDisconnect,HTTPException,status
from schemas import Server,UserServer
from database import get_db
from ServerConnectionManager import server_manager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_,select
import models,oauth
import redis
import uuid
import base64
import firebase
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()
redis_client = redis.Redis(host="redis",port=6379,db=0,decode_responses=True)
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


@router.websocket("/ws/server/{token}")
async def server(token:str,websocket:WebSocket,current_user:dict = Depends(oauth.get_websocket_user),db:AsyncSession = Depends(get_db)):
    await server_manager.connect(websocket,current_user)
    try:
        while True:
            data = await websocket.receive_json()
            if data["chat"] == "dm":
                data["dm"] = int(data["dm"])
                if "text" in data:
                    data["text"] = str(data["text"])
                if "serverinviteid" in data:
                    data["serverinviteid"] = int(data["serverinviteid"])
            if data["chat"] == "server":
                data["server"] = int(data["server"])
                if "text" in data:
                    data["text"] = str(data["text"])
            if data["type"] == "file" or data["type"] == "textandfile":
                file_type = data["filetype"]
                filename = f"{uuid.uuid4()}.{file_type}"
                encoded_image = base64.b64decode(data["file"].split(",")[1])
                await asyncio.to_thread(firebase_storage.child(filename).put,encoded_image)
                data["file"] = f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"
            elif data["type"] == "link":
                data["link"] = str(uuid.uuid4())
            elif data["type"] == "status":
                username = data["username"]
                status = data["status"]
                redis_client.set(f"{username}-status", status)
            await server_manager.broadcast(websocket, data, current_user,db)
    except WebSocketDisconnect:
        server_manager.disconnect(websocket,current_user)
    except Exception as e:
        print(e)
@router.post("/server")
async def create_server(server:Server,current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    if server.profile:
        filename = f"{uuid.uuid4()}.jpg"
        encoded_image = base64.b64decode(server.profile.split(",")[1])
        await asyncio.to_thread(firebase_storage.child(filename).put,encoded_image)
        new_server = models.Server(name=server.name,profile=f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8",owner=current_user.username)
        db.add(new_server)
    else:
        new_server = models.Server(name=server.name,owner=current_user.username)
        db.add(new_server)
    await db.flush()
    new_server_user = models.Server_User(server_id=new_server.id,username=current_user.username)
    db.add(new_server_user)
    server_manager.add_valid_server_or_dm([new_server_user.username],"server_ids",new_server_user.server_id)
    created_message = {"chat": "server", "server": new_server_user.server_id, "type": "announcement",
                    "announcement": f"{new_server_user.username} has created the server", "username": new_server_user.username,
                    "date": datetime.now().isoformat()}
    for connection in server_manager.active_connections:
        if connection.get("username") == current_user.username:
            await server_manager.broadcast(connection.get("websocket"), created_message, connection,db)
    await db.commit()
@router.get("/servers")
async def get_servers(current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    servers = await db.execute(select(models.Server_User.server_id,models.Server.owner,models.Server.profile,models.Server.id,models.Server.name)\
             .join(models.Server,models.Server.id == models.Server_User.server_id).filter(models.Server_User.username == current_user.username))
    servers = servers.all()
    servers_json = [{"id":server.id,"owner":server.owner,"profile":server.profile,"name":server.name} for server in servers]
    return servers_json
@router.get("/server/{id}")
async def get_server_information(id:int,current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    in_server = await db.execute(select(models.Server_User).filter(and_(models.Server_User.server_id == id,models.Server_User.username == current_user.username)))
    in_server = in_server.scalars().first()
    if not in_server:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this server")
    server = await db.execute(select(models.Server).filter(models.Server.id == id))
    server = server.scalars().first()
    return server
@router.get("/server/users/{id}")
async def get_server_users(id:int,current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    in_server = await db.execute(select(models.Server_User).filter(and_(models.Server_User.server_id == id, models.Server_User.username == current_user.username)))
    in_server = in_server.scalars().first()
    if not in_server:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this server")
    users = await db.execute(select(models.Server_User.username,models.Users.username,models.Users.profile).join(models.Users,models.Server_User.username == models.Users.username).filter(models.Server_User.server_id == id))
    users = users.all()
    users_json = [{"username":user.username,"profile":user.profile,"status":redis_client.get(f"{user.username}-status") if redis_client.get(f"{user.username}-status") is not None else "offline"} for user in users]
    return users_json
@router.post("/server/user")
async def join_server(user_server:UserServer,current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    server_id = redis_client.get(user_server.link)
    if server_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invite link has expired")
    already_in_server = await db.execute(select(models.Server_User).filter(and_(models.Server_User.username == current_user.username,models.Server_User.server_id == int(server_id))))
    already_in_server = already_in_server.scalars().first()
    if already_in_server:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="You are already a part of this server")
    server_user = models.Server_User(username=current_user.username,server_id=int(server_id))
    db.add(server_user)
    join_message = {"chat":"server","server":int(server_id),"type":"announcement","announcement":f"{current_user.username} has joined the server","username":current_user.username,"date":datetime.now().isoformat()}
    server_manager.add_valid_server_or_dm(current_user.username,"server_ids",server_id)
    for connection in server_manager.active_connections:
        if connection.get("username") == current_user.username:
            await server_manager.broadcast(connection.get("websocket"), join_message, connection,db)
    await db.commit()
    return {"serverid":server_id}
@router.get("/servermessages/{server}")
async def get_server_messages(server:int, current_user: models.Users = Depends(oauth.get_current_user), db:AsyncSession = Depends(get_db)):
    in_server = await db.execute(select(models.Server_User).filter(and_(models.Server_User.server_id == server,models.Server_User.username == current_user.username)))
    in_server = in_server.scalars().first()
    if not in_server:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a part of this server")
    server_messages = await db.execute(select(models.Server_Messages.announcement,models.Server_Messages.server,models.Server_Messages.username,
                        models.Server_Messages.text, models.Server_Messages.file,
                        models.Server_Messages.created_date, models.Server_Messages.filetype,
                        models.Users.profile).join(models.Users,models.Server_Messages.username == models.Users.username).filter(
                        models.Server_Messages.server == server).order_by(models.Server_Messages.id))
    server_messages = server_messages.all()
    server_messages_json = [{"announcement":message.announcement,"server":message.server,"username":message.username,"text":message.text,"file":message.file,"filetype":message.filetype,"date":message.created_date,"profile":message.profile} for message in server_messages]
    return server_messages_json