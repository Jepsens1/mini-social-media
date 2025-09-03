from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from schemas.post_schemas import PostPublic

class LikeBase(BaseModel):
    user_id: UUID
    post_id: UUID

class LikePublic(LikeBase):
    liked_at: datetime
    post: PostPublic