from app.db.base_class import BaseMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from typing import Optional


class Friends(BaseMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    sender: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    receiver: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    UniqueConstraint(sender, receiver)

    sender_user: Mapped["Users"] = relationship(foreign_keys=[sender])
    receiver_user: Mapped["Users"] = relationship(foreign_keys=[receiver])
    dm_id: Mapped[Optional[int]] = mapped_column(ForeignKey("dms.id",ondelete="CASCADE"))
    dm: Mapped["Dms"] = relationship(back_populates="friend")

    def __repr__(self):
        return f"Friends(id={self.id},sender={self.sender},receiver={self.receiver})"
