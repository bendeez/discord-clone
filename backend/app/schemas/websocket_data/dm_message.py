from pydantic import BaseModel, Field, computed_field
from typing import Literal, Union, Annotated
import base64
from uuid import uuid4


class DmWebsocketMessageBase(BaseModel):
    dm: int
    otheruser: str
    username: str
    profile: str
    date: str

class DmWebsocketText(DmWebsocketMessageBase):
    chat: Literal['dm']
    type: Literal["text"]
    text: str

class DmWebsocketFile(DmWebsocketMessageBase):
    chat: Literal['dm']
    type: Literal["file"]
    file: str
    filetype: str

    @computed_field()
    def encoded_file(self) -> Union[bytes, None]:
        return base64.b64decode(self.file.split(",")[1])

class DmWebsocketTextAndFile(DmWebsocketText,DmWebsocketFile):
    chat: Literal['dm']
    type: Literal["textandfile"]

class DmWebsocketLink(DmWebsocketMessageBase):
    chat: Literal['dm']
    type: Literal["link"]
    serverinviteid: int

    @computed_field()
    def link(self) -> str:
        return str(uuid4())

DmWebsocketMessage = Annotated[Union[DmWebsocketText,DmWebsocketFile,DmWebsocketTextAndFile,DmWebsocketLink] ,Field(...,discriminator='type')]