from pydantic import BaseModel
from typing import Dict
import socket

class ConnectionConfig(BaseModel):
    client: socket.socket
    channels: Dict[str, list[str]]

class Message(BaseModel):
    channels: Dict[str, list[str]]