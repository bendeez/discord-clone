from app.db.base_class import BaseMixin
from sqlalchemy.orm import Mapped,mapped_column,relationship
from datetime import datetime
from sqlalchemy import ForeignKey
from typing import Optional,List




class Server_Messages(BaseMixin):
    announcement: Mapped[Optional[str]] = mapped_column()
    text: Mapped[Optional[str]] = mapped_column()
    file: Mapped[Optional[str]] = mapped_column()
    filetype: Mapped[Optional[str]] = mapped_column()
    username: Mapped[str] = mapped_column(ForeignKey("users.username",ondelete="CASCADE"))
    server: Mapped[int] = mapped_column(ForeignKey("server.id",ondelete="CASCADE"))
    created_date: Mapped[datetime] = mapped_column()

    def __repr__(self):
        return f"Server_Messages(id={self.id},announcement={self.announcement},text={self.text},file={self.file},filetype={self.filetype},username={self.username},server={self.server},created_date={self.created_date})"


class Server(BaseMixin):
    owner: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column()
    profile: Mapped[str] = mapped_column(default="https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/default.png?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8")
    server_users: Mapped[List["Server_User"]] = relationship(back_populates="server")

    def __repr__(self):
        return f"Server(id={self.id},owner={self.owner},name={self.name},profile={self.profile})"

class Server_User(BaseMixin):
    username: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    server_id: Mapped[int] = mapped_column(ForeignKey("server.id"))
    server: Mapped["Server"] = relationship(back_populates="server_users")

    def __repr__(self):
        return f"Server_user(id={self.id},username={self.username},server_id={self.server_id})"
