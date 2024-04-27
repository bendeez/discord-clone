from fastapi import APIRouter,Depends,WebSocket,WebSocketDisconnect
import base64
from app.routers.server_websocket.ServerConnectionManager import server_manager
from app.core.oauth import get_websocket_user
from app.firebase.firebase_startup import firebase_storage
from app.db.database import get_db
from app.models.user import Users
from app.schemas.websocket_data import WebsocketData
from sqlalchemy import select
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio


router = APIRouter()

@router.websocket("/ws/server/{token}")
async def server(token:str,websocket:WebSocket,current_user:dict = Depends(get_websocket_user),db:AsyncSession = Depends(get_db)):
    await server_manager.connect(websocket,current_user)
    update_user_status = await db.execute(select(Users).filter(Users.username == current_user["username"]))
    update_user_status = update_user_status.scalars().first()
    if update_user_status:
        update_user_status.status = "online"
        await db.commit()
    try:
        while True:
            data = await websocket.receive_json()
            data = WebsocketData(data=data).data
            if data.type == "file" or data.type == "textandfile":
                file_type = data.filetype
                filename = f"{uuid.uuid4()}.{file_type}"
                encoded_image = base64.b64decode(data.file.split(",")[1])
                await asyncio.to_thread(firebase_storage.child(filename).put,encoded_image)
                data.file = f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"
            await server_manager.broadcast(websocket, dict(data), current_user,db)
    except WebSocketDisconnect:
        server_manager.disconnect(websocket,current_user)
    except Exception as e:
        print(e)
        if update_user_status:
            update_user_status.status = "offline"
            await db.commit()