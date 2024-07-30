from pydantic import BaseModel, Field
from typing import Literal, Union, Annotated, Optional


class NotificationAllMessageBase(BaseModel):
    username: Optional[str] = None
    pubsub_publisher: Optional[str] = None


class NotificationAllStatus(NotificationAllMessageBase):
    chat: Literal["notificationall"] = "notificationall"
    type: Literal["status"] = "status"
    status: str


NotificationAll = Annotated[
    Union[NotificationAllStatus], Field(..., discriminator="type")
]
