from sqlalchemy import (
    Column,
    String,
    Uuid,
    DateTime,
    ForeignKey,
    select,
    column,
    text,
    Integer,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4
from src.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), default=func.now()
    )
    role_id = Column(
        Uuid,
        ForeignKey("roles.id"),
        default=select(column("id"))
        .where(column("name") == "user")
        .select_from(text("roles")),
    )
    role = relationship("Role", back_populates="users", lazy="joined")
    images = relationship("Image", back_populates="user", lazy="selectin")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Uuid, primary_key=True, default=uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String)
    users = relationship(
        "User", back_populates="role", order_by="User.created_at", lazy="selectin"
    )


class Image(Base):
    __tablename__ = "images"

    id = Column(Uuid, primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    location = Column(String, unique=True, nullable=False)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="images", lazy="joined")
