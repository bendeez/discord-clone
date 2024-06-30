from app.db.base_class import BaseMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import ForeignKey, UniqueConstraint
from typing import Optional

DEFAULT_SERVER_PROFILE = "https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/default.png?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"

class Server_Messages(BaseMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    announcement: Mapped[Optional[str]] = mapped_column()
    text: Mapped[Optional[str]] = mapped_column()
    file: Mapped[Optional[str]] = mapped_column()
    filetype: Mapped[Optional[str]] = mapped_column()
    username: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    server: Mapped[int] = mapped_column(ForeignKey("server.id", ondelete="CASCADE"))
    date: Mapped[datetime] = mapped_column(default=datetime.now())
    user: Mapped["Users"] = relationship(back_populates="server_messages")
    parent_server: Mapped["Server"] = relationship(back_populates="server_messages")

    @classmethod
    def save_server_message(cls, data: dict):
        return cls(**{k: v for k, v in data.items() if k in [column.name for column in cls.__table__.columns]})

    def __repr__(self):
        return f"Server_Messages(id={self.id},announcement={self.announcement},text={self.text},file={self.file},filetype={self.filetype},username={self.username},server={self.server},date={self.date})"


class Server(BaseMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column()
    profile: Mapped[str] = mapped_column(default=DEFAULT_SERVER_PROFILE)
    server_users: Mapped[list["Server_User"]] = relationship(back_populates="server",cascade="all",passive_deletes=True)
    server_messages: Mapped[list["Server_Messages"]] = relationship(back_populates="parent_server",cascade="all",passive_deletes=True)
    owner_user: Mapped["Users"] = relationship(back_populates="owned_servers")

    def __repr__(self):
        return f"Server(id={self.id},owner={self.owner},name={self.name},profile={self.profile})"


class Server_User(BaseMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    server_id: Mapped[int] = mapped_column(ForeignKey("server.id",ondelete="CASCADE"))
    UniqueConstraint(username, server_id)
    server: Mapped["Server"] = relationship(back_populates="server_users")
    user: Mapped["Users"] = relationship(back_populates="server_associations")

    def __repr__(self):
        return f"Server_user(id={self.id},username={self.username},server_id={self.server_id})"
