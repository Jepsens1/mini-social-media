from fastapi import APIRouter, Query, Depends
from typing import Annotated
from schemas.user_schemas import UserPublic, UserRegister, UserUpdate, UserWithPosts, UserWithComments, UserWithLike
from database import SessionDep
from models.models import User
from uuid import UUID
import services.user_service
from services.authentication_service import get_current_active_user
router = APIRouter(prefix='/users', tags=['users'])

CurrentUser = Annotated[User, Depends(get_current_active_user)]


@router.post('/', response_model=UserPublic)
async def create_user(user: UserRegister, session: SessionDep):
    db_user = services.user_service.create_user_object(user, session)
    return db_user

@router.get('/', response_model=dict[str,list[UserPublic]])
async def read_users(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    users = services.user_service.read_users_from_db(session, offset, limit)
    return {'users': users}

@router.get('/me', response_model=UserPublic)
async def read_user_me(current_user: CurrentUser):
    return current_user

@router.delete('/me')
async def delete_me(session: SessionDep, current_user: CurrentUser) -> dict:
    services.user_service.delete_user(current_user.id, session)
    return {'Ok': True}

@router.put('/me', response_model=UserPublic)
async def update_user(user: UserUpdate, session: SessionDep, current_user: CurrentUser):
    updated_user = services.user_service.update_user(current_user.id, user, session)
    return updated_user

@router.get('/{user_id}', response_model=UserPublic)
async def read_user(user_id: UUID, session: SessionDep):
    user = services.user_service.read_user(user_id, session)
    return user

@router.get('/{user_id}/posts', response_model=UserWithPosts)
async def read_user_posts(user_id: UUID, session: SessionDep):
    user = services.user_service.read_user(user_id, session)
    return user

@router.get('/{user_id}/comments', response_model=UserWithComments)
async def read_user_comments(user_id: UUID, session: SessionDep):
    user = services.user_service.read_user(user_id, session)
    return user

@router.get('/{user_id}/likes', response_model=UserWithLike)
async def read_user_likes(user_id: UUID, session: SessionDep):
    user = services.user_service.read_user(user_id, session)
    return user
