from fastapi import APIRouter, Query
from typing import Annotated
from schemas.user_schemas import UserPublic, UserRegister, UserUpdate
from database import SessionDep
from uuid import UUID
import services.user_service

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/create', response_model=UserPublic)
async def create_user(user: UserRegister, session: SessionDep):
    db_user = services.user_service.create_user_object(user, session)
    return db_user

@router.get('/', response_model=dict[str,list[UserPublic]])
async def read_users(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    users = services.user_service.read_users_from_db(session, offset, limit)
    return {'users': users}

@router.get('/{user_id}', response_model=UserPublic)
async def read_user(user_id: UUID, session: SessionDep):
    user = services.user_service.read_user(user_id, session)
    return user

@router.delete('/{user_id}')
async def delete_user(user_id: UUID, session: SessionDep) -> dict:
    services.user_service.delete_user(user_id, session)
    return {'Ok': True}

@router.put('/{user_id}', response_model=UserPublic)
async def update_user(user_id: UUID, user: UserUpdate, session: SessionDep):
    updated_user = services.user_service.update_user(user_id, user, session)
    return updated_user