from pydantic import BaseModel, Field
from typing import Literal, Union, Annotated, Optional
from datetime import datetime


class ServerWebsocketMessageBase(BaseModel):
    server: int
    username: Optional[str] = None
    profile: Optional[str] = None
    date: Optional[datetime] = None

class ServerWebsocketText(ServerWebsocketMessageBase):
    chat: Literal['server']
    type: Literal["text"]
    text: str

class ServerWebsocketFile(ServerWebsocketMessageBase):
    chat: Literal['server']
    type: Literal["file"]
    file: str
    filetype: str

class ServerWebsocketTextAndFile(ServerWebsocketText,ServerWebsocketFile):
    chat: Literal['server']
    type: Literal["textandfile"]

class ServerWebsocketAnnouncement(ServerWebsocketMessageBase):
    chat: Literal['server']
    type: Literal["announcement"]
    announcement: str


ServerWebsocketMessage = Annotated[Union[ServerWebsocketText,ServerWebsocketFile,ServerWebsocketTextAndFile,ServerWebsocketAnnouncement],Field(...,discriminator='type')]
