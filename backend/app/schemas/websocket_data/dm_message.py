from pydantic import BaseModel, Field
from typing import Literal, Union, Annotated
from typing import Optional
from datetime import datetime


class DmWebsocketMessageBase(BaseModel):
    dm: int
    otheruser: str
    username: Optional[str] = None
    profile: Optional[str] = None
    date: Optional[datetime] = None

class DmWebsocketText(DmWebsocketMessageBase):
    chat: Literal['dm']
    type: Literal["text"]
    text: str

class DmWebsocketFile(DmWebsocketMessageBase):
    chat: Literal['dm']
    type: Literal["file"]
    file: str
    filetype: str

class DmWebsocketTextAndFile(DmWebsocketText,DmWebsocketFile):
    chat: Literal['dm']
    type: Literal["textandfile"]

class DmWebsocketLink(DmWebsocketMessageBase):
    chat: Literal['dm']
    type: Literal["link"]
    serverinviteid: int
    servername: str
    serverprofile: str
    link: str = None

DmWebsocketMessage = Annotated[Union[DmWebsocketText,DmWebsocketFile,DmWebsocketTextAndFile,DmWebsocketLink] ,Field(...,discriminator='type')]