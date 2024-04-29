from sqlalchemy.orm import Mapped, mapped_column, declared_attr, as_declarative


@as_declarative()
class BaseMixin:
    @declared_attr.directive
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)
