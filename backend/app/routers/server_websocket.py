from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.ConnectionManagers.CentralWebsocketServerInterface import central_ws_interface
from app.core.oauth import get_websocket_user
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.websocket("/ws/server/{token}")
async def server(token: str, websocket: WebSocket, current_user: dict = Depends(get_websocket_user), db: AsyncSession = Depends(get_db)):
    await central_ws_interface.connect(websocket, current_user,db)
    try:
        while True:
            data = await websocket.receive_json()
            await central_ws_interface.broadcast(data, current_user)
    except WebSocketDisconnect:
        await central_ws_interface.disconnect(current_user,db)
    except Exception as e:
        print(e)
        await central_ws_interface.disconnect(current_user,db)
