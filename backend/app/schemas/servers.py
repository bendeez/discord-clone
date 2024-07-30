from app.schemas.user import UserOut
from app.schemas.messages import Messages
from pydantic import BaseModel
from typing import Optional


class ServerUserOut(UserOut):
    status: str


class ServerUserCreated(BaseModel):
    id: int
    username: str
    server_id: int


class ServerIn(BaseModel):
    name: str
    profile: Optional[str] = None  # base64


class ServerCreated(BaseModel):
    id: int
    name: str
    profile: Optional[str] = None
    owner: str


class ServersOut(BaseModel):
    id: int
    owner: str
    profile: str
    name: str


class UserServer(BaseModel):
    link: str


class ServerMessagesOut(Messages):
    server: int
    announcement: Optional[str] = None
