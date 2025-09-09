from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from schemas.post_schemas import PostPublic
from schemas.comment_schemas import CommentPublic
from schemas.likes_schemas import LikePublic


#Base class containing shared fields
class UserBase(BaseModel):
    model_config = {'from_attributes': True, 'extra': 'forbid'}
    username: str = Field(max_length=20, pattern=r'^[a-zA-Z0-9_]{3,20}$')
    full_name: str | None = Field(default=None, max_length=40, pattern=r'^[a-zA-ZæøåÆØÅ ]{3,40}$')


#User object for displaying public user information
class UserPublic(UserBase):
    is_active: bool = True
    id: UUID
    created_at: datetime

class UserWithPosts(UserPublic):
    posts: list[PostPublic]

class UserWithComments(UserPublic):
    comments: list[CommentPublic]

class UserWithLike(UserPublic):
    likes: list[LikePublic]

#Pydantic model for creating user
class UserRegister(UserBase):
    password: str = Field(min_length=8, max_length=40)

#Pydantic model for PUT or PATCH
class UserUpdate(UserBase):
   username: str | None = Field(default=None, max_length=20, pattern=r'^[a-zA-Z0-9_]{3,20}$') # type: ignore
   full_name: str | None = Field(default=None, max_length=40, pattern=r'^[a-zA-ZæøåÆØÅ ]{3,40}$')
   