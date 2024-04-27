from pydantic import BaseModel,Base64Str,model_validator,Field
from typing import Optional,Literal,Union
from uuid import uuid4


class DmWebsocketMessage(BaseModel):
    chat: Literal['dm']
    type: str
    dm: int
    link: Optional[str] = None
    serverinviteid: Optional[int] = None
    text: Optional[str] = None
    file: Optional[Base64Str] = None
    filetype: Optional[str] = None
    otheruser: str
    username: str
    profile: str
    date: str

    @model_validator(mode="after")
    def check_sent_right_data(self):
        if self.type == "link":
            if self.serverinviteid is None:
                raise Exception("No serverinviteid was sent to match with the link")
            self.link = str(uuid4())
        elif self.type == "text":
            if self.text is None:
                raise Exception("No text was sent")
        elif self.type == "file":
            if self.file is None or self.filetype is None:
                raise Exception("Either a file or/and filetype was not sent")
        elif self.type == "textandfile":
            if self.text is None or self.file is None or self.filetype is None:
                raise Exception("Either a file or/and filetype or/and text was not sent")
        else:
            raise Exception("invalid message type")
        return self


class ServerWebsocketMessage(BaseModel):
    chat: Literal['server']
    type: str
    server: int
    announcement: Optional[str] = None
    text: Optional[str] = None
    file: Optional[Base64Str] = None
    filetype: Optional[str] = None
    username: str
    profile: str
    date: str

    @model_validator(mode="after")
    def check_sent_right_data(self):
        if self.type == "announcement":
            if self.announcement is None:
                raise Exception("No announcement was sent")
        elif self.type == "text":
            if self.text is None:
                raise Exception("No text was sent")
        elif self.type == "file":
            if self.file is None or self.filetype is None:
                raise Exception("Either a file or/and filetype was not sent")
        elif self.type == "textandfile":
            if self.text is None or self.file is None or self.filetype is None:
                raise Exception("Either a file or/and filetype or/and text was not sent")
        else:
            raise Exception("invalid message type")
        return self


class Notification(BaseModel):
    chat: Literal['notification']
    type: str
    dm: int
    sender: str
    receiver: str
    profile: str

    @model_validator(mode="after")
    def check_notification(self):
        if self.type == "message":
            pass
        else:
            raise Exception("invalid message type")
        return self


class NotificationAll(BaseModel):
    chat: Literal['notificationall']
    type: str
    status: str
    username: str

    @model_validator(mode="after")
    def check_notification(self):
        if self.type == "status":
            pass
        else:
            raise Exception("invalid message type")
        return self


class WebsocketData(BaseModel):
    data: Union[DmWebsocketMessage,ServerWebsocketMessage,Notification,NotificationAll] = Field(...,discriminator='chat')
