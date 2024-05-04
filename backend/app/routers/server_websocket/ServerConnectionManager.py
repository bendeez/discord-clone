from fastapi import WebSocket
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.server_websocket import save_message,send_notification

class ServerConnectionManager:
    def __init__(self):
        self.active_connections: list[dict[str, Union[list[int], str, WebSocket]]] = []

    async def connect(self, websocket: WebSocket, current_user: dict):
        await websocket.accept()
        self.active_connections.append(current_user)

    def disconnect(self, websocket: WebSocket, current_user: dict):
        self.active_connections.remove(current_user)

    async def broadcast(self, websocket: WebSocket, data: dict, current_user: dict,db:AsyncSession):
        try:
            chat = data.get("chat")
            if chat == "dm":
                dm = data.get("dm")
                if dm in current_user.get("dm_ids", []):
                    for connection in self.active_connections:
                        if dm in connection.get("dm_ids", []):
                            await connection.get("websocket").send_json(data)
                    await save_message(data=dict(data), db=db)
                    await send_notification(websocket=websocket, data=dict(data), current_user=current_user, db=db)
            elif chat == "server":
                server = data.get("server")
                if server in current_user.get("server_ids", []):
                    for connection in self.active_connections:
                        if server in connection.get("server_ids", []):
                            await connection.get("websocket").send_json(data)
                    await save_message(data=dict(data), db=db)
            elif chat == "notification":
                for connection in self.active_connections:
                    if data.get("receiver") == connection.get("username"):
                        await connection.get("websocket").send_json(data)
                await save_message(data=dict(data), db=db)
            elif chat == "notificationall":
                for connection in self.active_connections:
                    await connection.get("websocket").send_json(data)
                await save_message(data=dict(data), db=db)
        except Exception as e:
            print(e)

    async def broadcast_from_route(self, sender_username: str, message: dict, db: AsyncSession):
        for connection in self.active_connections:
            if connection.get("username") == sender_username:
                await server_manager.broadcast(connection.get("websocket"), message, connection,db)

    def add_valid_server_or_dm(self, usernames: list, type, id):
        for connection in self.active_connections:
            if connection.get("username") in usernames:
                if isinstance(connection.get(type), list):
                    connection.get(type).append(int(id))


server_manager = ServerConnectionManager()
