from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

"""
comment_schemas.py

Defines the Pydantic models (schemas) for comment.

These schemas are used for request validation and response serialization.
"""

class CommentBase(BaseModel):
    """Base schema for comment, shared between input and output models."""
    model_config = {'from_attributes': True, 'extra': 'forbid'}
    content: str = Field(max_length=255)

class CommentCreate(CommentBase):
    """Schema for creating a new comment."""
    pass

class CommentPublic(CommentBase):
    """Public representation of a comment, returned in API responses."""
    id: UUID
    owner_id: UUID
    post_id: UUID
    created_at: datetime
    last_edited: datetime | None = None

class CommentUpdate(CommentBase):
    """Schema for updating a existing comment."""
    pass