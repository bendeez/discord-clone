from pydantic import BaseModel
from typing import Optional


class FriendsOut(BaseModel):
    username: str
    status: str
    profile: str
    dmid: Optional[int] = None


class FriendIn(BaseModel):
    username: str


class FriendCreated(BaseModel):
    id: int
    sender: str
    receiver: str
