from fastapi import WebSocket
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.server_websocket import save_message, send_notification
from app.crud.server_websocket import set_user_status
from datetime import datetime


class ServerConnectionManager:
    def __init__(self):
        self.active_connections: list[dict[str, Union[list[int], str, WebSocket]]] = []

    async def connect(self, websocket: WebSocket, current_user: dict,db: AsyncSession):
        await websocket.accept()
        self.active_connections.append(current_user)
        await set_user_status(db=db, status="online", current_user=current_user)
        await self.broadcast(websocket=websocket,
                             data={"chat": "notificationall", "type": "status", "status": "online",
                                   "username": current_user["username"]},
                             current_user=current_user, db=db)

    async def disconnect(self, websocket: WebSocket, current_user: dict,db: AsyncSession):
        self.active_connections.remove(current_user)
        await set_user_status(db=db, status="offline", current_user=current_user)
        await self.broadcast(websocket=websocket,
                             data={"chat": "notificationall", "type": "status", "status": "offline",
                                   "username": current_user["username"]},
                             current_user=current_user, db=db)

    async def broadcast(self, websocket: WebSocket, data: dict, current_user: dict, db: AsyncSession):
        try:
            chat = data.get("chat")
            if chat == "dm": # checks if the message is being sent to a dm
                data.update(
                    {"username": current_user["username"], "profile": current_user["profile"],
                     "date": str(datetime.now())})
                dm = data.get("dm") # get the dm id
                if dm in current_user.get("dm_ids", []):  # checks if the dm id is a part of the user's dms
                    for connection in self.active_connections: # loops through all connections
                        if dm in connection.get("dm_ids", []): # checks if the dm id is a part of the remote user's dms
                            await connection.get("websocket").send_json(data) # sends a message if it is
                    await save_message(data=data, db=db)
                    await send_notification(websocket=websocket, data=data, current_user=current_user, db=db)
            elif chat == "server":
                data.update(
                    {"username": current_user["username"], "profile": current_user["profile"],
                     "date": str(datetime.now())})
                server = data.get("server")
                if server in current_user.get("server_ids", []):
                    for connection in self.active_connections:
                        if server in connection.get("server_ids", []):
                            await connection.get("websocket").send_json(data)
                    await save_message(data=data, db=db)
            elif chat == "notification":
                data.update(
                    {"sender": current_user["username"], "profile": current_user["profile"]})
                for connection in self.active_connections:
                    if data.get("receiver") == connection.get("username"):
                        await connection.get("websocket").send_json(data)
                await save_message(data=data, db=db)
            elif chat == "notificationall":
                data.update({"username": current_user["username"]})
                for connection in self.active_connections:
                    await connection.get("websocket").send_json(data)
                await save_message(data=data, db=db)
        except Exception as e:
            print(e)

    async def broadcast_from_route(self, sender_username: str, message: dict, db: AsyncSession):
        for connection in self.active_connections:
            if connection.get("username") == sender_username:
                await server_manager.broadcast(connection.get("websocket"), message, connection, db)

    def add_valid_server_or_dm(self, usernames: list, type, id):
        for connection in self.active_connections:
            if connection.get("username") in usernames:
                if isinstance(connection.get(type), list):
                    connection.get(type).append(int(id))


server_manager = ServerConnectionManager()
