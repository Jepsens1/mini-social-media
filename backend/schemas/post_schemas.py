from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class PostBase(BaseModel):
    model_config = {'from_attributes': True}
    title: str = Field(max_length=40)
    content: str = Field(max_length=255)
    created_at: datetime

class PostCreate(PostBase):
    owner_id: UUID

class PostPublic(PostBase):
    id: UUID
    owner_id: UUID
    updated_at: datetime | None = None

class PostUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=40)
    content: str | None = Field(default=None, max_length=255)

