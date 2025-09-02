from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from schemas.post_schemas import PostPublic


#Base class containing shared fields
class UserBase(BaseModel):
    model_config = {'from_attributes': True}
    username: str = Field(max_length=20)
    is_active: bool = True
    full_name: str | None = Field(default=None, max_length=40)


#User object for displaying public user information
class UserPublic(UserBase):
    id: UUID
    posts: list["PostPublic"] | None = None

#Pydantic model for creating user
class UserRegister(UserBase):
    password: str = Field(min_length=8, max_length=40)

#Pydantic model for PUT or PATCH
class UserUpdate(UserBase):
   username: str | None = Field(default=None, max_length=20) # type: ignore
   full_name: str | None = Field(default=None, max_length=40)
   