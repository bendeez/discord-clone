from app.db.base_class import BaseMixin
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from typing import Optional


class Dms(BaseMixin):
    sender_id: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE")
    )
    receiver_id: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE")
    )
    UniqueConstraint(sender_id, receiver_id)

    friend: Mapped["Friends"] = relationship(back_populates="dms")
    sender: Mapped["Users"] = relationship(foreign_keys=[sender_id])
    receiver: Mapped["Users"] = relationship(foreign_keys=[receiver_id])
    dm_messages: Mapped[list["Dm_Messages"]] = relationship(
        back_populates="parent_dm", cascade="all", passive_deletes=True
    )



class Dm_Messages(BaseMixin):
    link: Mapped[Optional[str]] = mapped_column()
    text: Mapped[Optional[str]] = mapped_column()
    file: Mapped[Optional[str]] = mapped_column()
    filetype: Mapped[Optional[str]] = mapped_column()
    username: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE")
    )
    dm_id: Mapped[int] = mapped_column(ForeignKey("dms.id", ondelete="CASCADE"))
    serverinviteid: Mapped[Optional[int]] = mapped_column(ForeignKey("server.id"))
    date: Mapped[datetime] = mapped_column(default=datetime.now())

    dm: Mapped["Dms"] = relationship(back_populates="dm_messages")
    user: Mapped["Users"] = relationship(back_populates="dm_messages")
    server_invite_info: Mapped["Server"] = relationship()


