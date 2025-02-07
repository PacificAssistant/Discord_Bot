from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    BigInteger,
    Date,
    Boolean,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from datetime import date
from database.database import Base


class Audio(Base):
    __tablename__ = "audio"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(
        String(255), nullable=True
    )  # ID файлу (наприклад, UUID)
    file_path: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Шлях до файлу (або URL)
    created_at: Mapped[date] = mapped_column(Date, default=date.today)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="audios")

    def __repr__(self):
        return f"<User(id={self.id}, file_id='{self.file_id}', file_path={self.file_path}, created_at={self.created_at},user_id={self.user_id} )>"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    join_date: Mapped[date] = mapped_column(Date, default=date.today)
    user_roles: Mapped[list["UserRoles"]] = relationship(
        "UserRoles", back_populates="user", cascade="all, delete"
    )

    #  Доступ до ролей через зв’язок many-to-many
    roles: Mapped[list["Roles"]] = relationship(
        "Roles", secondary="user_roles", viewonly=True  #  Не дозволяє змінювати напряму
    )
    audios: Mapped[list["Audio"]] = relationship(
        back_populates="user", cascade="all, delete"
    )

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', join_date={self.join_date}, roles={self.roles})>"


class Roles(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    about: Mapped[str] = mapped_column(String, nullable=False)
    role_value: Mapped[int] = mapped_column(Integer, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user_roles: Mapped[list["UserRoles"]] = relationship(
        "UserRoles", back_populates="role", cascade="all, delete"
    )

    #  Доступ до користувачів через зв’язок many-to-many
    users: Mapped[list["User"]] = relationship(
        "User", secondary="user_roles", viewonly=True  #  Не дозволяє змінювати напряму
    )

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', about={self.about}, role_value={self.role_value},is_admin={self.is_admin} )>"


class UserRoles(Base):
    __tablename__ = "user_roles"

    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id = Column(
        BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )

    user = relationship("User", back_populates="user_roles")
    role = relationship("Roles", back_populates="user_roles")
