from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username:str
class UserIn(UserBase):
    password: str

class UserOut(UserBase):
    profile: str
class UserCreate(UserIn):
    email: str

class ServerUserOut(UserOut):
    status: str

class FriendRequestIn(BaseModel):
    username:str

class FriendRequestOut(BaseModel):
    sender:str
    senderprofile:str
    receiver:str
    receiverprofile:str
class NotificationIn(BaseModel):
    id:int

class NotificationOut(NotificationIn):
    dm: int
    count: int
    sender: str
    receiver:str
    profile:str

class Server(BaseModel):
    name:str
    profile: Optional[str] = None
class ServersOut(BaseModel):
    id: int
    owner: str
    profile: str
    name: str
class UserServer(BaseModel):
    link:str
class FriendsOut(BaseModel):
    username: str
    status: str
    profile: str
    dmid: Optional[int]

class DmsOut(UserOut):
    id: int
    status: str

class Messages(UserOut):
    text: Optional[str] = None
    file: Optional[str] = None
    filetype: Optional[str] = None
    date: datetime
class DmMessagesOut(Messages):
    dm: int
    link: Optional[str] = None
    servername: Optional[str] = None
    serverprofile: Optional[str] = None

class ServerMessagesOut(Messages):
    server: int
    announcement: Optional[str] = None


