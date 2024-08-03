from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.websocket_server.websocket_managers.CentralWebsocketServerInterface import (
    central_ws_interface,
)
from app.core.oauth import get_websocket_user
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.websocket_server.schemas.websocket_connection import WebsocketConnection

websocket_router = APIRouter()


@websocket_router.websocket("/ws/server/{token}")
async def websocket_server(
    token: str,
    websocket: WebSocket,
    current_user: WebsocketConnection = Depends(get_websocket_user),
    db: AsyncSession = Depends(get_db),
):
    await central_ws_interface.connect(websocket, current_user, db)
    try:
        while True:
            data = await websocket.receive_json()
            await central_ws_interface.broadcast(data, current_user)
    except WebSocketDisconnect:
        await central_ws_interface.disconnect(current_user, db)
    except Exception as e:
        print(e)
        await central_ws_interface.disconnect(current_user, db)
