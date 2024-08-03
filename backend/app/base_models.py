from sqlalchemy.orm import Mapped, mapped_column, declared_attr, as_declarative
from sqlalchemy import UniqueConstraint, CheckConstraint


@as_declarative()
class BaseMixin:
    @declared_attr.directive
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)


class Message(BaseMixin):
    chat: Mapped[str] = mapped_column()

    __mapper_args__ = {
        "polymorphic_identity": "message",
        "polymorphic_on": "chat"
    }

class SelfRelationship(BaseMixin):
    UniqueConstraint("sender_id", "receiver_id")
    CheckConstraint('sender_id > receiver_id')

    @classmethod
    def check_and_create(cls, **attributes):
        if attributes["sender_id"] < attributes["receiver_id"]: # violates constraint
            attributes["sender_id"], attributes["receiver_id"] = attributes["receiver_id"], attributes["sender_id"]
        return cls(**attributes)