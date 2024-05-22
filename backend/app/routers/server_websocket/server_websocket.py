from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.routers.server_websocket.ServerConnectionManager import server_manager
from app.core.oauth import get_websocket_user
from app.firebase.firebase_startup import firebase_storage
from app.db.database import get_db
from app.schemas.websocket_data.websocket_data import websocket_data_adaptor
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

router = APIRouter()


@router.websocket("/ws/server/{token}")
async def server(token: str, websocket: WebSocket, current_user: dict = Depends(get_websocket_user), db: AsyncSession = Depends(get_db)):
    await server_manager.connect(websocket, current_user,db)
    try:
        while True:
            data = await websocket.receive_json()
            data = websocket_data_adaptor.validate_python(data)
            if data.type == "file" or data.type == "textandfile":
                file_type = data.filetype
                filename = f"{uuid.uuid4()}.{file_type}"
                await asyncio.to_thread(firebase_storage.child(filename).put, data.encoded_file)
                data.file = f"https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/{filename}?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"
            await server_manager.broadcast(websocket, data.dict(), current_user,db)
    except WebSocketDisconnect:
        await server_manager.disconnect(websocket, current_user,db)
    except Exception as e:
        print(e)
        await server_manager.disconnect(websocket, current_user,db)
