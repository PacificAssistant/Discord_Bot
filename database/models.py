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
    """Represents an audio recording in the database.

    This model stores information about audio recordings, including file paths,
    creation dates, and associations with users.

    Attributes:
        file_id (str): Primary key, unique identifier for the audio file.
        file_path (str): Full path to the stored audio file location.
        created_at (date): Date when the audio recording was created.
        user_id (int): Foreign key reference to the User who owns this recording.
        user (User): Relationship to the User model representing the owner.

    Relationships:
        - user: Many-to-one relationship with User model.
    """
    __tablename__ = "audio"
    file_id: Mapped[str] = mapped_column(
        String(255), nullable=True, primary_key=True
    )
    file_path: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    created_at: Mapped[date] = mapped_column(Date, default=date.today)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="audios")

    def __repr__(self):
        return f"<User(id={self.id}, file_id='{self.file_id}', file_path={self.file_path}, created_at={self.created_at},user_id={self.user_id} )>"


class User(Base):
    """Represents a user in the database.

    This model stores user information and manages relationships with roles
    and audio recordings.

    Attributes:
        id (int): Primary key, unique identifier for the user.
        name (str): User's name, cannot be null.
        join_date (date): Date when the user joined, defaults to current date.
        user_roles (list[UserRoles]): List of user-role associations.
        roles (list[Roles]): List of roles assigned to the user (read-only).
        audios (list[Audio]): List of audio recordings associated with the user.

    Relationships:
        - roles: Many-to-many relationship with Roles through UserRoles table.
        - audios: One-to-many relationship with Audio recordings.
        - user_roles: One-to-many relationship with UserRoles association table.
    """
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
    """Represents a role in the database.

    This model defines different roles that can be assigned to users,
    including administrative privileges and role hierarchies.

    Attributes:
        id (int): Primary key, unique identifier for the role.
        name (str): Name of the role, cannot be null.
        about (str): Description or information about the role.
        role_value (int): Numeric value representing role hierarchy/priority.
        is_admin (bool): Flag indicating if role has administrative privileges.
        user_roles (list[UserRoles]): List of user-role associations.
        users (list[User]): List of users assigned to this role (read-only).

    Relationships:
        - users: Many-to-many relationship with User through UserRoles table.
        - user_roles: One-to-many relationship with UserRoles association table.
    """
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
    """Association table for the many-to-many relationship between Users and Roles.

    This model represents the junction table that manages the many-to-many
    relationship between users and roles.

    Attributes:
        user_id (int): Part of composite primary key, foreign key to users table.
        role_id (int): Part of composite primary key, foreign key to roles table.
        user (User): Relationship to the associated User model.
        role (Roles): Relationship to the associated Roles model.

    Relationships:
        - user: Many-to-one relationship with User model.
        - role: Many-to-one relationship with Roles model.

    Notes:
        - Both foreign keys have CASCADE delete behavior.
    """
    __tablename__ = "user_roles"

    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id = Column(
        BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )

    user = relationship("User", back_populates="user_roles")
    role = relationship("Roles", back_populates="user_roles")
