from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Messages(BaseModel):
    text: Optional[str] = None
    file: Optional[str] = None
    filetype: Optional[str] = None
    username: str
    profile: str
    date: datetime
