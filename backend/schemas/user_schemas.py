from pydantic import BaseModel, Field
from uuid import UUID


#Base class containing shared fields
class UserBase(BaseModel):
    model_config = {'from_attributes': True}
    username: str = Field(max_length=20)
    full_name: str | None = Field(default=None, max_length=40)


#User object for displaying public user information
class UserPublic(UserBase):
    is_active: bool = True
    id: UUID

#Pydantic model for creating user
class UserRegister(UserBase):
    password: str = Field(min_length=8, max_length=40)

#Pydantic model for PUT or PATCH
class UserUpdate(UserBase):
   username: str | None = Field(default=None, max_length=20) # type: ignore
   full_name: str | None = Field(default=None, max_length=40)
   