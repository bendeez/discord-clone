from app.db.base_class import BaseMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey


class Friends(BaseMixin):
    sender: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    receiver: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))

    def __repr__(self):
        return f"Friends(id={self.id},sender={self.sender},receiver={self.receiver})"
