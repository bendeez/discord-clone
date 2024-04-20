from pydantic import BaseModel

class NotificationIn(BaseModel):
    id:int

class NotificationOut(NotificationIn):
    dm: int
    count: int
    sender: str
    receiver:str
    profile:str