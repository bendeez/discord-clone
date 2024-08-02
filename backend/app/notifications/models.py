from app.db.base_class import BaseMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint


class Notifications(BaseMixin):
    sender: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE")
    )
    receiver: Mapped[str] = mapped_column(
        ForeignKey("users.username", ondelete="CASCADE")
    )
    UniqueConstraint(sender, receiver)
    dm: Mapped[int] = mapped_column(ForeignKey("dms.id", ondelete="CASCADE"))
    count: Mapped[int] = mapped_column(default=1)

    parent_dm: Mapped["Dms"] = relationship(
        foreign_keys=[dm], cascade="all", passive_deletes=True
    )
    sender_user: Mapped["Users"] = relationship(foreign_keys=[sender])
    receiver_user: Mapped["Users"] = relationship(
        foreign_keys=[receiver], back_populates="received_notifications"
    )

    @classmethod
    def save_notification(cls, data: dict):
        return cls(
            **{
                k: v
                for k, v in data.items()
                if k in [column.name for column in cls.__table__.columns]
            }
        )

    def __repr__(self):
        return f"Notifications(id={self.id},sender={self.sender},receiver={self.receiver},dm={self.dm},count={self.count})"
