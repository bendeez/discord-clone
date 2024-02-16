from app.database import Base
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from sqlalchemy import ForeignKey


class Users(Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    profile: Mapped[str] = mapped_column(default="https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/default.png?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8")

# class Users(Base):
#     __tablename__ = "users"
#     username = Column(String, primary_key=True)
#     email = Column(String,nullable=False)
#     password = Column(String,nullable=False)
#     profile = Column(String,default="https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/default.png?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8")

class FriendRequests(Base):
    __tablename__ = "friend-requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[str] = mapped_column(ForeignKey("users.username",ondelete="CASCADE"))
    receiver: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
# class FriendRequests(Base):
#     __tablename__ = "friend-requests"
#     id = Column(Integer,primary_key=True)
#     sender = Column(ForeignKey("users.username",ondelete="CASCADE"))
#     receiver = Column(ForeignKey("users.username",ondelete="CASCADE"))

class Friends(Base):
    __tablename__ = "friends"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    receiver: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
# class Friends(Base):
#     __tablename__ = "friends"
#     id = Column(Integer,primary_key=True)
#     sender = Column(ForeignKey("users.username",ondelete="CASCADE"))
#     receiver = Column(ForeignKey("users.username",ondelete="CASCADE"))

class Dms(Base):
    __tablename__ = "dms"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    receiver: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
# class Dms(Base):
#     __tablename__ = "dms"
#     id = Column(Integer,primary_key=True)
#     sender = Column(ForeignKey("users.username", ondelete="CASCADE"))
#     receiver = Column(ForeignKey("users.username", ondelete="CASCADE"))

class Dm_Messages(Base):
    __tablename__ = "dm_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str] = mapped_column()
    text: Mapped[str] = mapped_column()
    file: Mapped[str] = mapped_column()
    filetype: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(ForeignKey("users.username",ondelete="CASCADE"))
    dm: Mapped[int] = mapped_column(ForeignKey("dms.id",ondelete="CASCADE"))
    serverinviteid: Mapped[int] = mapped_column(ForeignKey("server.id"))
    created_date: Mapped[datetime] = mapped_column(nullable=False)

# class Dm_Messages(Base):
#     __tablename__ = "dm_messages"
#     id = Column(Integer, primary_key=True)
#     link = Column(String)
#     text = Column(String)
#     file = Column(String)
#     filetype = Column(String)
#     username = Column(ForeignKey("users.username",ondelete="CASCADE"))
#     dm = Column(ForeignKey("dms.id",ondelete="CASCADE"))
#     serverinviteid = Column(ForeignKey("server.id"))
#     created_date = Column(DateTime,nullable=False)

class Server_Messages(Base):
    __tablename__ = "server_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    announcement: Mapped[str] = mapped_column()
    text: Mapped[str] = mapped_column()
    file: Mapped[str] = mapped_column()
    filetype: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(ForeignKey("users.username",ondelete="CASCADE"))
    server: Mapped[int] = mapped_column(ForeignKey("server.id",ondelete="CASCADE"))
    created_date: Mapped[datetime] = mapped_column(nullable=False)
# class Server_Messages(Base):
#     __tablename__ = "server_messages"
#     id = Column(Integer, primary_key=True)
#     announcement = Column(String)
#     text = Column(String)
#     file = Column(String)
#     filetype = Column(String)
#     username = Column(ForeignKey("users.username", ondelete="CASCADE"))
#     server = Column(ForeignKey("server.id", ondelete="CASCADE"))
#     created_date = Column(DateTime, nullable=False)

class Notifications(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    receiver: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    dm: Mapped[int] = mapped_column(ForeignKey("dms.id", ondelete="CASCADE"))
    count: Mapped[int] = mapped_column(default=1)
# class Notifications(Base):
#     __tablename__ = "notifications"
#     id = Column(Integer, primary_key=True)
#     sender = Column(ForeignKey("users.username",ondelete="CASCADE"))
#     receiver = Column(ForeignKey("users.username", ondelete="CASCADE"))
#     dm = Column(ForeignKey("dms.id",ondelete="CASCADE"))
#     count = Column(Integer,default=1)

class Server(Base):
    __tablename__ = "server"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(nullable=False)
    profile: Mapped[str] = mapped_column(default="https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/default.png?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8")

# class Server(Base):
#     __tablename__ = "server"
#     id = Column(Integer,primary_key=True)
#     owner = Column(ForeignKey("users.username",ondelete="CASCADE"))
#     name = Column(String,nullable=False)
#     profile = Column(String,default="https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/defaultserver.png?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8")

class Server_User(Base):
    __tablename__ = "server_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    server_id: Mapped[int] = mapped_column(ForeignKey("server.id"))
# class Server_User(Base):
#     __tablename__ = "server_user"
#     id = Column(Integer, primary_key=True)
#     username = Column(ForeignKey("users.username",ondelete="CASCADE"))
#     server_id = Column(ForeignKey("server.id",ondelete="CASCADE"))
