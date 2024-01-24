from app.database import Base
from sqlalchemy import Column,String,ForeignKey,Integer,DateTime


class Users(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True)
    email = Column(String,nullable=False)
    password = Column(String,nullable=False)
    profile = Column(String,default="https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/default.png?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8")
class FriendRequests(Base):
    __tablename__ = "friend-requests"
    id = Column(Integer,primary_key=True)
    sender = Column(ForeignKey("users.username",ondelete="CASCADE"))
    receiver = Column(ForeignKey("users.username",ondelete="CASCADE"))
class Friends(Base):
    __tablename__ = "friends"
    id = Column(Integer,primary_key=True)
    sender = Column(ForeignKey("users.username",ondelete="CASCADE"))
    receiver = Column(ForeignKey("users.username",ondelete="CASCADE"))
class Dms(Base):
    __tablename__ = "dms"
    id = Column(Integer,primary_key=True)
    sender = Column(ForeignKey("users.username", ondelete="CASCADE"))
    receiver = Column(ForeignKey("users.username", ondelete="CASCADE"))
class Dm_Messages(Base):
    __tablename__ = "dm_messages"
    id = Column(Integer, primary_key=True)
    link = Column(String)
    text = Column(String)
    file = Column(String)
    filetype = Column(String)
    username = Column(ForeignKey("users.username",ondelete="CASCADE"))
    dm = Column(ForeignKey("dms.id",ondelete="CASCADE"))
    serverinviteid = Column(ForeignKey("server.id"))
    created_date = Column(DateTime,nullable=False)
class Server_Messages(Base):
    __tablename__ = "server_messages"
    id = Column(Integer, primary_key=True)
    announcement = Column(String)
    text = Column(String)
    file = Column(String)
    filetype = Column(String)
    username = Column(ForeignKey("users.username", ondelete="CASCADE"))
    server = Column(ForeignKey("server.id", ondelete="CASCADE"))
    created_date = Column(DateTime, nullable=False)
class Notifications(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    sender = Column(ForeignKey("users.username",ondelete="CASCADE"))
    receiver = Column(ForeignKey("users.username", ondelete="CASCADE"))
    dm = Column(ForeignKey("dms.id",ondelete="CASCADE"))
    count = Column(Integer,default=1)
class Server(Base):
    __tablename__ = "server"
    id = Column(Integer,primary_key=True)
    owner = Column(ForeignKey("users.username",ondelete="CASCADE"))
    name = Column(String,nullable=False)
    profile = Column(String,default="https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/defaultserver.png?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8")
class Server_User(Base):
    __tablename__ = "server_user"
    id = Column(Integer, primary_key=True)
    username = Column(ForeignKey("users.username",ondelete="CASCADE"))
    server_id = Column(ForeignKey("server.id",ondelete="CASCADE"))
