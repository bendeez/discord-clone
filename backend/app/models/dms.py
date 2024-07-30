from app.db.base_class import BaseMixin
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from typing import Optional


class Dms(BaseMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE")
    )
    receiver: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE")
    )
    UniqueConstraint(sender, receiver)

    friend: Mapped["Friends"] = relationship(back_populates="dm")
    sender_user: Mapped["Users"] = relationship(foreign_keys=[sender])
    receiver_user: Mapped["Users"] = relationship(foreign_keys=[receiver])
    dm_messages: Mapped[list["Dm_Messages"]] = relationship(
        back_populates="parent_dm", cascade="all", passive_deletes=True
    )

    def __repr__(self):
        return f"Dms(id={self.id},sender={self.sender},receiver={self.receiver})"


class Dm_Messages(BaseMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[Optional[str]] = mapped_column()
    text: Mapped[Optional[str]] = mapped_column()
    file: Mapped[Optional[str]] = mapped_column()
    filetype: Mapped[Optional[str]] = mapped_column()
    username: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE")
    )
    dm: Mapped[int] = mapped_column(ForeignKey("dms.id", ondelete="CASCADE"))
    serverinviteid: Mapped[Optional[int]] = mapped_column(ForeignKey("server.id"))
    date: Mapped[datetime] = mapped_column(default=datetime.now())

    parent_dm: Mapped["Dms"] = relationship(back_populates="dm_messages")
    user: Mapped["Users"] = relationship(back_populates="dm_messages")
    server_invite_info: Mapped["Server"] = relationship()

    @classmethod
    def save_dm_message(cls, data: dict):
        return cls(
            **{
                k: v
                for k, v in data.items()
                if k in [column.name for column in cls.__table__.columns]
            }
        )

    def __repr__(self):
        return f"Dm_Messages(id={self.id},link={self.link},text={self.text},file={self.file},filetype={self.filetype},username={self.username},dm={self.dm},serverinviteid={self.serverinviteid},date={self.date})"
