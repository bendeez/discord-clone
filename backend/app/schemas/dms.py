from app.schemas.user import UserOut
from app.schemas.base import Messages
from typing import Optional


class DmsOut(UserOut):
    id: int
    status: str


class DmMessagesOut(Messages):
    dm: int
    link: Optional[str] = None
    servername: Optional[str] = None
    serverprofile: Optional[str] = None
