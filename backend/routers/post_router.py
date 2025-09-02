from fastapi import APIRouter, Query
from typing import Annotated
from database import SessionDep
from uuid import UUID
from schemas.post_schemas import PostUpdate, PostCreate, PostPublic
import services.post_service

router = APIRouter(prefix='/posts', tags=['posts'])

@router.post('/create', response_model=PostPublic)
async def create_post(post: PostCreate, session: SessionDep):
    post = services.post_service.create_post_object(post, session)
    return post

@router.get('/{post_id}', response_model=PostPublic)
async def get_post_by_id(post_id: UUID, session: SessionDep):
    post = services.post_service.get_post(post_id, session)
    return post

@router.get('/', response_model=dict[str, list[PostPublic]])
async def get_posts(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    posts = services.post_service.get_posts(session, offset, limit)
    return {"posts": posts}

@router.delete('/{post_id}')
async def delete_post(post_id: UUID, session: SessionDep) -> dict:
    services.post_service.delete_post(post_id, session)
    return {'Ok': True}

@router.put('/{post_id}', response_model=PostPublic)
async def update_post(post_id: UUID, post: PostUpdate, session: SessionDep):
    updated_post = services.post_service.update_post(post_id, post, session)
    return updated_post