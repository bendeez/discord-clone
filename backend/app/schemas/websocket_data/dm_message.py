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

    def make_json_compatible(self):
        """
            returns json version copy
            with compatible types
        """
        model_copy = self.copy()
        model_copy.date = str(model_copy.date)
        return model_copy.model_dump()

class DmWebsocketText(DmWebsocketMessageBase):
    chat: Literal['dm'] = "dm"
    type: Literal["text"] = "text"
    text: str

class DmWebsocketFile(DmWebsocketMessageBase):
    chat: Literal['dm'] = "dm"
    type: Literal["file"] = "file"
    file: str
    filetype: str

class DmWebsocketTextAndFile(DmWebsocketText,DmWebsocketFile):
    chat: Literal['dm'] = "dm"
    type: Literal["textandfile"] = "textandfile"

class DmWebsocketLink(DmWebsocketMessageBase):
    chat: Literal['dm'] = "dm"
    type: Literal["link"] = "link"
    serverinviteid: int
    servername: str
    serverprofile: str
    link: str = None

DmWebsocketMessage = Annotated[Union[DmWebsocketText,DmWebsocketFile,DmWebsocketTextAndFile,DmWebsocketLink] ,Field(...,discriminator='type')]
