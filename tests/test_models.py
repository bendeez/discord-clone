from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from sqlalchemy import ForeignKey,Column,Integer
from typing import Optional

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    profile: Mapped[str] = mapped_column(default="https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/default.png?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8")
    def __repr__(self):
        return f"Users(username={self.username},email={self.email},profile={self.profile})"
class FriendRequests(Base):
    __tablename__ = "friend-requests"
    id = Column(Integer,primary_key=True)
    sender = Column(ForeignKey("users.username",ondelete="CASCADE"))
    receiver = Column(ForeignKey("users.username",ondelete="CASCADE"))

    def __repr__(self):
        return f"FriendRequests(id={self.id},sender={self.sender},receiver={self.receiver})"

class Friends(Base):
    __tablename__ = "friends"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    receiver: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    def __repr__(self):
        return f"Friends(id={self.id},sender={self.sender},receiver={self.receiver})"
class Dms(Base):
    __tablename__ = "dms"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    receiver: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    def __repr__(self):
        return f"Dms(id={self.id},sender={self.sender},receiver={self.receiver})"
class Dm_Messages(Base):
    __tablename__ = "dm_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[Optional[str]] = mapped_column()
    text: Mapped[Optional[str]] = mapped_column()
    file: Mapped[Optional[str]] = mapped_column()
    filetype: Mapped[Optional[str]] = mapped_column()
    username: Mapped[str] = mapped_column(ForeignKey("users.username",ondelete="CASCADE"))
    dm: Mapped[int] = mapped_column(ForeignKey("dms.id",ondelete="CASCADE"))
    serverinviteid: Mapped[Optional[int]] = mapped_column(ForeignKey("server.id"))
    created_date: Mapped[datetime] = mapped_column()

    def __repr__(self):
        return f"Dm_Messages(id={self.id},link={self.link},text={self.text},file={self.file},filetype={self.filetype},username={self.username},dm={self.dm},serverinviteid={self.serverinviteid},created_date={self.created_date})"
class Server_Messages(Base):
    __tablename__ = "server_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    announcement: Mapped[Optional[str]] = mapped_column()
    text: Mapped[Optional[str]] = mapped_column()
    file: Mapped[Optional[str]] = mapped_column()
    filetype: Mapped[Optional[str]] = mapped_column()
    username: Mapped[str] = mapped_column(ForeignKey("users.username",ondelete="CASCADE"))
    server: Mapped[int] = mapped_column(ForeignKey("server.id",ondelete="CASCADE"))
    created_date: Mapped[datetime] = mapped_column()

    def __repr__(self):
        return f"Server_Messages(id={self.id},announcement={self.announcement},text={self.text},file={self.file},filetype={self.filetype},username={self.username},server={self.server},created_date={self.created_date})"

class Notifications(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    receiver: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    dm: Mapped[int] = mapped_column(ForeignKey("dms.id", ondelete="CASCADE"))
    count: Mapped[int] = mapped_column(default=1)
    def __repr__(self):
        return f"Notifications(id={self.id},sender={self.sender},receiver={self.receiver},dm={self.dm},count={self.count})"
class Server(Base):
    __tablename__ = "server"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column()
    profile: Mapped[str] = mapped_column(default="https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/default.png?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8")
    def __repr__(self):
        return f"Server(id={self.id},owner={self.owner},name={self.name},profile={self.profile})"
class Server_User(Base):
    __tablename__ = "server_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    server_id: Mapped[int] = mapped_column(ForeignKey("server.id"))

    def __repr__(self):
        return f"Server_user(id={self.id},username={self.username},server_id={self.server_id})"