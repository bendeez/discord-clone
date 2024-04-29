from app.db.base_class import BaseMixin
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import ForeignKey
from typing import Optional


class Dms(BaseMixin):
    sender: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    receiver: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))

    def __repr__(self):
        return f"Dms(id={self.id},sender={self.sender},receiver={self.receiver})"


class Dm_Messages(BaseMixin):
    link: Mapped[Optional[str]] = mapped_column()
    text: Mapped[Optional[str]] = mapped_column()
    file: Mapped[Optional[str]] = mapped_column()
    filetype: Mapped[Optional[str]] = mapped_column()
    username: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    dm: Mapped[int] = mapped_column(ForeignKey("dms.id", ondelete="CASCADE"))
    serverinviteid: Mapped[Optional[int]] = mapped_column(ForeignKey("server.id"))
    created_date: Mapped[datetime] = mapped_column()

    def __repr__(self):
        return f"Dm_Messages(id={self.id},link={self.link},text={self.text},file={self.file},filetype={self.filetype},username={self.username},dm={self.dm},serverinviteid={self.serverinviteid},created_date={self.created_date})"
