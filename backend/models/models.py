from database import Base
from sqlalchemy import Column, String, UUID, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime, timezone


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    
    posts = relationship("Post", back_populates="owner")

class Post(Base):
    __tablename__ = 'posts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(40), nullable=False, index=True)
    content = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True)

    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    owner = relationship("User", back_populates="posts")

    