from database import Base
from sqlalchemy import String, UUID, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from datetime import datetime, timezone


class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="owner")

class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    owner_id = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = 'comments'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    last_edited: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('posts.id'), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    post = relationship("Post", back_populates="comments")
    owner = relationship("User", back_populates="comments")

    