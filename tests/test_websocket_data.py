from pydantic import BaseModel, Base64Str, model_validator, Field
from typing import Optional, Literal, Union
from uuid import uuid4
import base64


class DmWebsocketMessage(BaseModel):
    chat: Literal['dm']
    type: str
    dm: int
    link: Optional[str] = None
    serverinviteid: Optional[int] = None
    text: Optional[str] = None
    file: Optional[str] = None # will convert into bytes
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
            else:
                self.file = base64.b64decode(self.file.split(",")[1])
        elif self.type == "textandfile":
            if self.text is None or self.file is None or self.filetype is None:
                raise Exception("Either a file or/and filetype or/and text was not sent")
            else:
                self.file = base64.b64decode(self.file.split(",")[1])
        else:
            raise Exception("invalid message type")
        return self


class ServerWebsocketMessage(BaseModel):
    chat: Literal['server']
    type: str
    server: int
    announcement: Optional[str] = None
    text: Optional[str] = None
    file: Optional[str] = None # will convert into bytes
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
            else:
                self.file = base64.b64decode(self.file.split(",")[1])
        elif self.type == "textandfile":
            if self.text is None or self.file is None or self.filetype is None:
                raise Exception("Either a file or/and filetype or/and text was not sent")
            else:
                self.file = base64.b64decode(self.file.split(",")[1])
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
    data: Union[DmWebsocketMessage, ServerWebsocketMessage, Notification, NotificationAll] = Field(...,discriminator='chat')

data = WebsocketData(data={'chat': 'dm', 'dm': '2', 'type': 'file', 'file': '''data:image/jpeg;base64,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''', 'filetype': 'jfif', 'otheruser': 'bill', 'username': 'Blaziken', 'profile': 'https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/0c0333d6-57d7-4bc3-8907-2efa36ca95ea.jpg?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8', 'date': '2024-05-04T15:19:20.119Z'})
