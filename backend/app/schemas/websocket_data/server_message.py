from pydantic import BaseModel, Field, computed_field
from typing import Literal, Union, Annotated
import base64


class ServerWebsocketMessageBase(BaseModel):
    server: int
    username: str
    profile: str
    date: str

class ServerWebsocketText(ServerWebsocketMessageBase):
    chat: Literal['server']
    type: Literal["text"]
    text: str

class ServerWebsocketFile(ServerWebsocketMessageBase):
    chat: Literal['server']
    type: Literal["file"]
    file: str
    filetype: str

    @computed_field()
    def encoded_file(self) -> Union[bytes, None]:
        return base64.b64decode(self.file.split(",")[1])

class ServerWebsocketTextAndFile(ServerWebsocketText,ServerWebsocketFile):
    chat: Literal['server']
    type: Literal["textandfile"]

class ServerWebsocketAnnouncement(ServerWebsocketMessageBase):
    chat: Literal['server']
    type: Literal["announcement"]
    announcement: str


ServerWebsocketMessage = Annotated[Union[ServerWebsocketText,ServerWebsocketFile,ServerWebsocketTextAndFile,ServerWebsocketAnnouncement],Field(...,discriminator='type')]
