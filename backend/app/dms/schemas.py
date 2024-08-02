from app.user.schemas import UserOut
from app.base_schemas import Messages
from typing import Optional
from pydantic import BaseModel, Field, AliasPath


class DmsOut(UserOut):
    id: int
    status: str


class DmUsernameIn(BaseModel):
    username: str


class DmInformationOut(BaseModel):
    username: str = Field(validation_alias=AliasPath("information", 0))
    profile: str = Field(validation_alias=AliasPath("information", 1))
    status: str = Field(validation_alias=AliasPath("information", 2))
    id: int = Field(validation_alias=AliasPath("information", 3))


class DmMessagesOut(Messages):
    dm: int
    link: Optional[str] = None
    servername: Optional[str] = None
    serverprofile: Optional[str] = None


class DmCreated(BaseModel):
    id: int
    sender: str
    receiver: str
