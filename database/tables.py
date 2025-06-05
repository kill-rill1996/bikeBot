import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class User(Base):
    """Пользователи"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[str] = mapped_column(index=True, unique=True)
    tg_username: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime]
    role: Mapped[str] = mapped_column()  # admin, mechanic
    lang: Mapped[str] = mapped_column()  # en, ru, es
    is_active: Mapped[bool] = mapped_column(default=True)


class AllowedUsers(Base):
    """Tg id пользователей, которым разрешен доступ в бота"""
    __tablename__ = "allowed_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[str] = mapped_column(index=True, unique=True)


class Operation(Base):
    """Выполненные работы"""
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[str] = mapped_column(index=True)
    transport_id: Mapped[int] = mapped_column(nullable=False)        # bicycles, ebicycles, segways
    duration: Mapped[int] = mapped_column(nullable=False)       # в минутах
    location_id: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime]
    updated_at: Mapped[datetime.datetime] = mapped_column(nullable=True, default=None)

    jobs: Mapped[list["Job"]] = relationship(
        back_populates="operations",
        secondary="operations_jobs"
    )


class Job(Base):
    """Разновидности работ"""
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    jobtype_id: Mapped[int] = mapped_column(nullable=False)

    operations: Mapped[list["Operation"]] = relationship(
        back_populates="jobs",
        secondary="operations_jobs"
    )


class OperationsJobs(Base):
    """Работы входящие в операцию"""
    __tablename__ = "operations_jobs"

    operation_id: Mapped[int] = mapped_column(
        ForeignKey("operations.id"),
        primary_key=True
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        primary_key=True
    )


class Jobtype(Base):
    """Группы узлов"""
    __tablename__ = "jobtypes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    emoji: Mapped[str] = mapped_column(nullable=True)

    transport_categories: Mapped[list["Category"]] = relationship(
        back_populates="jobtypes",
        secondary="categories_jobtypes"
    )


class Transport(Base):
    """Транспорт"""
    __tablename__ = "transports"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(nullable=False)
    subcategory_id: Mapped[int] = mapped_column(nullable=False)
    serial_number: Mapped[int] = mapped_column(nullable=False, index=True)


class Category(Base):
    """Категории транспорта"""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False, index=True)
    emoji: Mapped[str] = mapped_column(nullable=True)

    jobtypes: Mapped[list["Jobtype"]] = relationship(
        back_populates="transport_categories",
        secondary="categories_jobtypes"
    )


class CategoryJobtypes(Base):
    """Many-to-many relationship"""
    __tablename__ = "categories_jobtypes"

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True
    )

    jobtype_id: Mapped[int] = mapped_column(
        ForeignKey("jobtypes.id", ondelete="CASCADE"),
        primary_key=True
    )


class Subcategory(Base):
    """Подкатегории транспорта"""
    __tablename__ = "subcategories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(nullable=False, index=True)


class Location(Base):
    """Местоположения"""
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

