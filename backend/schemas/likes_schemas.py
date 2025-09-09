from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from schemas.post_schemas import PostPublic

"""
likes_schemas.py

Defines the Pydantic models (schemas) for like.

These schemas are used for request validation and response serialization.
"""
class LikeBase(BaseModel):
    """Base schema for likes, shared between input and output models."""
    user_id: UUID
    post_id: UUID

class LikePublic(LikeBase):
    """Public representation of a like, returned in API responses."""
    liked_at: datetime
    post: PostPublic