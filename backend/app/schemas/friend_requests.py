from pydantic import BaseModel


class FriendRequestIn(BaseModel):
    username: str


class FriendRequestOut(BaseModel):
    sender: str
    senderprofile: str
    receiver: str
    receiverprofile: str

class FriendRequestCreated(BaseModel):
    id: int
    sender: str
    receiver: str
