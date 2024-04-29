from app.db.base_class import BaseMixin
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional


class Users(BaseMixin):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[Optional[str]] = mapped_column()
    password: Mapped[Optional[str]] = mapped_column()
    profile: Mapped[str] = mapped_column(
        default="https://firebasestorage.googleapis.com/v0/b/discord-83cd2.appspot.com/o/default.png?alt=media&token=c27e7352-b75a-4468-b14b-d06b74839bd8")
    status: Mapped[str] = mapped_column(default="offline")

    def __repr__(self):
        return f"Users(username={self.username},email={self.email},profile={self.profile},status={self.status})"
