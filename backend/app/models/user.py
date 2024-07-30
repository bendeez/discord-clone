from app.db.base_class import BaseMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

DEFAULT_USER_PROFILE = "https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/default.png?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8"


class Users(BaseMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[Optional[str]] = mapped_column()
    password: Mapped[Optional[str]] = mapped_column()
    profile: Mapped[str] = mapped_column(default=DEFAULT_USER_PROFILE)
    status: Mapped[str] = mapped_column(default="offline")

    sent_friends: Mapped[list["Friends"]] = relationship(
        foreign_keys="Friends.sender",
        back_populates="sender_user",
        cascade="all",
        passive_deletes=True,
    )
    received_friends: Mapped[list["Friends"]] = relationship(
        foreign_keys="Friends.receiver",
        back_populates="receiver_user",
        cascade="all",
        passive_deletes=True,
    )
    sent_friend_requests: Mapped[list["FriendRequests"]] = relationship(
        foreign_keys="FriendRequests.sender",
        back_populates="sender_user",
        cascade="all",
        passive_deletes=True,
    )
    received_friend_requests: Mapped[list["FriendRequests"]] = relationship(
        foreign_keys="FriendRequests.receiver",
        back_populates="receiver_user",
        cascade="all",
        passive_deletes=True,
    )
    sent_dms: Mapped[list["Dms"]] = relationship(
        foreign_keys="Dms.sender",
        back_populates="sender_user",
        cascade="all",
        passive_deletes=True,
    )
    received_dms: Mapped[list["Dms"]] = relationship(
        foreign_keys="Dms.receiver",
        back_populates="receiver_user",
        cascade="all",
        passive_deletes=True,
    )
    dm_messages: Mapped[list["Dm_Messages"]] = relationship(
        back_populates="user", cascade="all", passive_deletes=True
    )
    received_notifications: Mapped[list["Notifications"]] = relationship(
        foreign_keys="Notifications.receiver",
        back_populates="receiver_user",
        cascade="all",
        passive_deletes=True,
    )
    server_associations: Mapped[list["Server_User"]] = relationship(
        back_populates="user", cascade="all", passive_deletes=True
    )
    server_messages: Mapped[list["Server_Messages"]] = relationship(
        back_populates="user", cascade="all", passive_deletes=True
    )
    owned_servers: Mapped[list["Server"]] = relationship(
        back_populates="owner_user", cascade="all", passive_deletes=True
    )
