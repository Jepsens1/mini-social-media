from database import Base
from sqlalchemy import String, UUID, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
import uuid
from datetime import datetime, timezone

"""
models.py

This module contains SQLAlchemy ORM models for the API.

It defines the database schema for:
- User
- Post
- Comment
- Like
- RefreshToken

Relationships:
- User has many Posts, Comments, Likes, and RefreshTokens
- Post belongs to a User and has many Comments and Likes
- Comment belongs to a User and a Post
- Like links a User and a Post
- RefreshToken belongs to a User and is unique per device

These models are used for Alembic migrations, database interactions, and FastAPI endpoints.
"""

class User(Base):
    """
    Represents a user in the system


    Attributes:
        id (UUID): Unique identifier for the user.
        username (str): Unique username for login.
        is_active (bool): Whether the user is active.
        full_name (str | None): Optional full name.
        hashed_password (str): Hashed password.
        created_at (datetime): Timestamp for when the user was created.
        posts (list[Post]): Posts created by the user.
        comments (list[Comment]): Comments created by the user.
        likes (list[Like]): Likes made by the user.
        refresh_tokens (list[RefreshToken]): Active refresh tokens for the user.
    """
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="owner", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="owner", cascade="all, delete-orphan")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

class Post(Base):
    """
    Represents a post created by a user.

    Attributes:
        id (UUID): Unique identifier for the post.
        title (str): Title of the post.
        content (str): Content of the post.
        created_at (datetime): Creation timestamp.
        updated_at (datetime | None): Timestamp of last update.
        owner_id (UUID): ID of the user who created the post.
        owner (User): Relationship to the user.
        comments (list[Comment]): Comments on this post.
        likes (list[Like]): Likes on this post.
    """
    __tablename__ = 'posts'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    owner_id = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    """
    Represents a comment made by a user for a post.

    Attributes:
        id: (UUID): Unique identifier for the comment.
        content (str): Content of the comment.
        created_at (datetime): Creation timestamp.
        last_edited (datetime | None): Timestamp of when the comment last was edited.
        post_id (UUID): ID of the post commented on.
        owner_id (UUID): ID of the user who made the comment.
        post (Post): Relationship to the post.
        owner (User): Relationship to the user.
    """
    __tablename__ = 'comments'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    last_edited: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('posts.id'), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    owner: Mapped["User"] = relationship("User", back_populates="comments")

class Like(Base):
    """
    Represents a like made by a user on a post.

    Attributes:
        user_id (UUID): ID of the user who liked the post
        post_id (UUID): ID of the post that was liked.
        liked_at: (datetime): Timestamp of when the like was made
        user (User): Relationship to the user.
        post (Post): Relationship to the post.
    """
    __tablename__ = 'likes'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("posts.id"), primary_key=True)
    liked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    user: Mapped["User"] = relationship("User", back_populates="likes")
    post: Mapped["Post"] = relationship("Post", back_populates="likes")

class RefreshToken(Base):
    """
    Represents a refresh-token for multi-session authentication.

    Attributes:
        id (UUID): Unique identifier for the token.
        user_id (UUID): ID of the user this token belongs to.
        token (str): The refresh-token string.
        created_at (datetime): Timestamp for when the refresh-token was issued.
        expires_at (datetime): Timestamp for when token expires.
        revoked (bool): Whether the token is revoked.
        device_name (str): Identifier for the device/session.
        user (User): Relationship to the user.
    """
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        UniqueConstraint("user_id", "device_name", name="uix_user_device"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    device_name: Mapped[str] = mapped_column(String(255), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")