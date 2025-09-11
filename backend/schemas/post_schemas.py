from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from schemas.comment_schemas import CommentPublic

"""
post_schemas.py

Defines the Pydantic models (schemas) for post.

These schemas are used for request validation and response serialization.
"""
class PostBase(BaseModel):
    """Base schema for post, shared between input and output models."""
    model_config = {'from_attributes': True, 'extra': 'forbid'}
    title: str = Field(max_length=40, examples=['This might be the coolest post'])
    content: str = Field(max_length=255, examples=['Just look at this content i am sharing.'])

class PostCreate(PostBase):
    """Schema for creating a new post."""
    pass

class PostPublic(PostBase):
    """Public representation of a post, returned in API responses."""
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    likes_count: int = 0
    comments_count: int = 0
    
class PostWithComments(PostPublic):
    """Public representation of a post including comments, returned in API responses."""
    comments: list[CommentPublic]

class PostWithLikes(PostPublic):
    """Public representation of a post including likes, returned in API responses."""
    liked_by: list[str] = []

class PostUpdate(BaseModel):
    """Schema for updating a existing post"""
    title: str | None = Field(default=None, max_length=40, examples=['This might be the coolest and greatest post on this platform'])
    content: str | None = Field(default=None, max_length=255, examples=['Just look at this content i am sharing.'])

