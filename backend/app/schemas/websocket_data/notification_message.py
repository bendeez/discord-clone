from pydantic import BaseModel, Field
from typing import Literal, Union, Annotated, Optional

class NotificationBase(BaseModel):
    sender: Optional[str] = None
    profile: Optional[str] = None
class NotificationMessage(NotificationBase):
    chat: Literal['notification']
    type: Literal["message"]
    dm: int
    receiver: str
    count: Optional[int] = None

class NotificationNewDm(NotificationBase):
    chat: Literal['notification']
    type: Literal["newdm"]
    receiver: str

Notification = Annotated[Union[NotificationMessage,NotificationNewDm],Field(...,discriminator='type')]
