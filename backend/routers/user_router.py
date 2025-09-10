from fastapi import APIRouter, Query
from typing import Annotated
from schemas.user_schemas import UserPublic, UserRegister, UserUpdate, UserWithPosts, UserWithComments, UserWithLike
from uuid import UUID
import services.user_service
from dependencies import SessionDep
from services.authentication_service import CurrentUser

"""
user_router.py

Defines the /users/* API endpoints.

Endpoints:
- POST  /users/ -> Create a user
- GET   /users/ -> Get a list of users
- GET   /users/me -> Get information about authenticated user (requires authentication)
- DELETE    /users/me -> Delete authenticated user(requires authentication)
- PUT   /users/me -> Update authenticated user information (requires authentication)
- GET   /users/{user_id} -> Get a single user
- GET   /users/{user_id}/posts -> Get a single user including posts made
- GET   /users/{user_id}/comments -> Get a single user including comments made
- GET   /users/{user_id}/likes -> Get a single user including liked posts
"""
router = APIRouter(prefix='/users', tags=['users'])

@router.post('/', response_model=UserPublic)
async def create_user(user: UserRegister, session: SessionDep):
    """
    Create a new user
    """
    db_user = services.user_service.create_user_object(user, session)
    return db_user

@router.get('/', response_model=list[UserPublic])
async def read_users(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    """
    Get a paginated list of users.
    """
    users = services.user_service.read_users_from_db(session, offset, limit)
    return users

@router.get('/me', response_model=UserPublic)
async def read_user_me(current_user: CurrentUser):
    """
    Get authenticated user information
    """
    return current_user

@router.delete('/me')
async def delete_me(session: SessionDep, current_user: CurrentUser) -> dict:
    """
    Delete authenticated user
    """
    services.user_service.delete_user(current_user.id, session)
    return {'Ok': True}

@router.put('/me', response_model=UserPublic)
async def update_user(user: UserUpdate, session: SessionDep, current_user: CurrentUser):
    """
    Update authenticated user information
    """
    updated_user = services.user_service.update_user(current_user.id, user, session)
    return updated_user

@router.get('/{user_id}', response_model=UserPublic)
async def read_user(user_id: UUID, session: SessionDep):
    """
    Get user information by ID
    """
    user = services.user_service.read_user(user_id, session)
    return user

@router.get('/{user_id}/posts', response_model=UserWithPosts)
async def read_user_posts(user_id: UUID, session: SessionDep):
    """
    Get user information including posts by ID
    """
    user = services.user_service.read_user_including_counts(user_id, session)
    return user

@router.get('/{user_id}/comments', response_model=UserWithComments)
async def read_user_comments(user_id: UUID, session: SessionDep):
    """
    Get user information including comments by ID
    """
    user = services.user_service.read_user(user_id, session)
    return user

@router.get('/{user_id}/likes', response_model=UserWithLike)
async def read_user_likes(user_id: UUID, session: SessionDep):
    """
    Get user information including likes by ID
    """
    user = services.user_service.read_user(user_id, session)
    return user
