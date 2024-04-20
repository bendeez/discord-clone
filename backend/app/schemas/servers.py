from app.schemas.user import UserOut
from app.schemas.base import Messages
from pydantic import BaseModel
from typing import Optional


class ServerUserOut(UserOut):
    status: str

class ServerIn(BaseModel):
    name:str
    profile: Optional[str] = None

class ServersOut(BaseModel):
    id: int
    owner: str
    profile: str
    name: str

class UserServer(BaseModel):
    link:str

class ServerMessagesOut(Messages):
    server: int
    announcement: Optional[str] = None