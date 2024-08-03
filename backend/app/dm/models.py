from app.base_models import Message, SelfRelationship
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from typing import Optional


class Dm(SelfRelationship):
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    receiver_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )

    sender: Mapped["Users"] = relationship(foreign_keys=[sender_id])
    receiver: Mapped["Users"] = relationship(foreign_keys=[receiver_id])
    friend: Mapped["Friends"] = relationship(back_populates="dm")
    dm_messages: Mapped[list["Dm_Messages"]] = relationship(
        back_populates="parent_dm", cascade="all", passive_deletes=True
    )

class Dm_Message(Message):
    type: Mapped[str]
    username: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE")
    )
    dm_id: Mapped[int] = mapped_column(ForeignKey("dm.id", ondelete="CASCADE"))
    date: Mapped[datetime] = mapped_column(default=datetime.now())

    dm: Mapped["Dms"] = relationship(back_populates="dm_messages")
    user: Mapped["Users"] = relationship(back_populates="dm_messages")
    server_invite_info: Mapped["Server"] = relationship()

    __mapper_args__ = {
        "polymorphic_identity": "dm_message",
        "polymorphic_on": "type"
    }

class Dm_Link(Dm_Message):
    link: Mapped[Optional[str]] = mapped_column()
    serverinviteid: Mapped[Optional[int]] = mapped_column(ForeignKey("server.id"))

    __mapper_args__ = {
        "polymorphic_identity": "dm_link",
    }

class Dm_Text(Dm_Message):
    text: Mapped[Optional[str]]

    __mapper_args__ = {
        "polymorphic_identity": "dm_text",
    }

class Dm_File(Dm_Message):
    file_url: Mapped[Optional[str]]
    filetype: Mapped[Optional[str]]

    __mapper_args__ = {
        "polymorphic_identity": "dm_file",
    }

class Dm_Text_File(Dm_Text,Dm_File):

    __mapper_args__ = {
        "polymorphic_identity": "dm_text_file",
    }
