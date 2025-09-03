from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from schemas.comment_schemas import CommentPublic

class PostBase(BaseModel):
    model_config = {'from_attributes': True, 'extra': 'forbid'}
    title: str = Field(max_length=40)
    content: str = Field(max_length=255)

class PostCreate(PostBase):
    owner_id: UUID

class PostPublic(PostBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    
class PostWithComments(PostPublic):
    comments: list[CommentPublic]

class PostWithLikes(PostPublic):
    likes_count: int = 0

class PostUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=40)
    content: str | None = Field(default=None, max_length=255)

