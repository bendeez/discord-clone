from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.routers.server_websocket.ServerConnectionManager import server_manager
from app.core.oauth import get_websocket_user
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.websocket("/ws/server/{token}")
async def server(token: str, websocket: WebSocket, current_user: dict = Depends(get_websocket_user), db: AsyncSession = Depends(get_db)):
    await server_manager.connect(websocket, current_user,db)
    try:
        while True:
            data = await websocket.receive_json()
            await server_manager.broadcast(data, current_user)
    except WebSocketDisconnect:
        await server_manager.disconnect(current_user,db)
    except Exception as e:
        print(e)
        await server_manager.disconnect(current_user,db)
