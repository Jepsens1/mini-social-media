from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class CommentBase(BaseModel):
    model_config = {'from_attributes': True}
    content: str = Field(max_length=255)

class CommentCreate(CommentBase):
    owner_id: UUID # TODO for now until auth is setup

class CommentPublic(CommentBase):
    id: UUID
    owner_id: UUID
    post_id: UUID
    created_at: datetime
    last_edited: datetime | None = None

class CommentUpdate(CommentBase):
    owner_id: UUID