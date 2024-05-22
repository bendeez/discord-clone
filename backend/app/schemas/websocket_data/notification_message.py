from pydantic import BaseModel, Field
from typing import Literal, Union, Annotated


class NotificationMessage(BaseModel):
    chat: Literal['notification']
    type: Literal["message"]
    dm: int
    receiver: str

Notification = Annotated[Union[NotificationMessage],Field(...,discriminator='type')]
