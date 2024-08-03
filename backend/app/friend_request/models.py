from app.db.base_class import BaseMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint


class FriendRequests(BaseMixin):
    sender: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE")
    )
    receiver: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE")
    )
    UniqueConstraint(sender, receiver)

    sender_user: Mapped["Users"] = relationship(foreign_keys=[sender])
    receiver_user: Mapped["Users"] = relationship(foreign_keys=[receiver])

    def __repr__(self):
        return f"FriendRequests(id={self.id},sender={self.sender},receiver={self.receiver})"
