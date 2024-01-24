from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    email:str
    username:str
    password:str
class Login(BaseModel):
    username:str
    password:str
class FriendRequest(BaseModel):
    username:str
class Notification(BaseModel):
    id:int
class Status(BaseModel):
    status:str
class Server(BaseModel):
    name:str
    profile: Optional[str]
class UserServer(BaseModel):
    link:str