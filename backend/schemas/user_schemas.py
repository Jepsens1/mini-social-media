from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from schemas.post_schemas import PostPublic
from schemas.comment_schemas import CommentPublic
from schemas.likes_schemas import LikePublic

"""
user_schemas.py

Defines the Pydantic models (schemas) for user.

These schemas are used for request validation and response serialization.
"""
class UserBase(BaseModel):
    """Base schema for user, shared between input and output models."""
    model_config = {'from_attributes': True, 'extra': 'forbid'}
    username: str = Field(max_length=20, pattern=r'^[a-zA-Z0-9_]{3,20}$') #Only a-z/A-Z/0-9_ allowed
    full_name: str | None = Field(default=None, max_length=40, pattern=r'^[a-zA-ZæøåÆØÅ ]{3,40}$') #Only a-z/A-ZæøåÆØÅ allowed

class UserPublic(UserBase):
    """Public representation of a user, returned in API responses."""
    is_active: bool = True
    id: UUID
    created_at: datetime

class UserWithPosts(UserPublic):
    """Public representation of a user including posts made, returned in API responses."""
    posts: list[PostPublic]

class UserWithComments(UserPublic):
    """Public representation of a user including comments made, returned in API responses."""
    comments: list[CommentPublic]

class UserWithLike(UserPublic):
    """Public representation of a user including liked posts, returned in API responses."""
    likes: list[LikePublic]

class UserRegister(UserBase):
    """Schema for creating a new user"""
    password: str = Field(min_length=8, max_length=40)

class UserUpdate(UserBase):
   """Schema for updating a existing user"""
   username: str | None = Field(default=None, max_length=20, pattern=r'^[a-zA-Z0-9_]{3,20}$') # type: ignore
   full_name: str | None = Field(default=None, max_length=40, pattern=r'^[a-zA-ZæøåÆØÅ ]{3,40}$')
   