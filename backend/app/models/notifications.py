from app.db.base_class import BaseMixin
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import ForeignKey




class Notifications(BaseMixin):
    sender: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    receiver: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"))
    dm: Mapped[int] = mapped_column(ForeignKey("dms.id", ondelete="CASCADE"))
    count: Mapped[int] = mapped_column(default=1)
    def __repr__(self):
        return f"Notifications(id={self.id},sender={self.sender},receiver={self.receiver},dm={self.dm},count={self.count})"