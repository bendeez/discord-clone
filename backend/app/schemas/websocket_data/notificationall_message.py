from pydantic import BaseModel, Field
from typing import Literal, Union, Annotated


class NotificationAllStatus(BaseModel):
    chat: Literal['notificationall']
    type: Literal["status"]
    status: str

NotificationAll = Annotated[Union[NotificationAllStatus],Field(...,discriminator='type')]