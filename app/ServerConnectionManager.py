from fastapi import WebSocket
from typing import Union


class ServerConnectionManager:
    def __init__(self):
        self.active_connections: list[dict[str,Union[list[int],str,WebSocket]]] = []
    async def connect(self,websocket:WebSocket,current_user:dict):
        await websocket.accept()
        self.active_connections.append(current_user)
    def disconnect(self,websocket:WebSocket,current_user:dict):
        self.active_connections.remove(current_user)
    async def broadcast(self,websocket:WebSocket,data:dict,current_user:dict):
        chat = data.get("chat")
        if chat == "dm":
            id = data.get("id")
            if id is not None:
                id = int(id)
                if id in current_user.get("dm_ids",[]) or current_user == {"user":"server"}:
                    for connection in self.active_connections:
                        if id in connection.get("dm_ids",[]):
                            await connection.get("websocket").send_json(data)
        elif chat == "server":
            id = data.get("id")
            if id is not None:
                id = int(id)
                if id in current_user.get("server_ids",[]) or current_user == {"user":"server"}:
                    for connection in self.active_connections:
                        if id in connection.get("server_ids",[]):
                            await connection.get("websocket").send_json(data)
        elif chat == "notification" and current_user == {"user":"server"}:
            for connection in self.active_connections:
                if data.get("receiver") == connection.get("username"):
                    await connection.get("websocket").send_json(data)
        elif chat == "notificationall" and current_user == {"user":"server"}:
            for connection in self.active_connections:
                if connection != {"user":"server"}:
                    await connection.get("websocket").send_json(data)
    def add_valid_server_or_dm(self,usernames:list,type,id):
        for connection in self.active_connections:
            if connection.get("username") in usernames:
                if isinstance(connection.get(type),list):
                    connection.get(type).append(int(id))

server_manager = ServerConnectionManager()