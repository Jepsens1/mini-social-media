from fastapi import APIRouter, Query
from typing import Annotated
from database import SessionDep
from uuid import UUID
from schemas.post_schemas import PostUpdate, PostCreate, PostPublic
from schemas.comment_schemas import CommentCreate, CommentPublic, CommentUpdate
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


#Comments
@router.post('/{post_id}/comment', response_model=CommentPublic, tags=['comment'])
async def create_comment(post_id: UUID, comment: CommentCreate, session: SessionDep):
    created_comment = services.post_service.create_comment_to_post(post_id, comment, session)
    return created_comment

@router.get('/{post_id}/comment', response_model=list[CommentPublic], tags=['comment'])
async def get_comments_from_post(post_id: UUID, session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    comments_from_post = services.post_service.get_comments_from_post(post_id, offset, limit, session)
    return comments_from_post

@router.get('/{post_id}/comment/{comment_id}', response_model=CommentPublic, tags=['comment'])
async def get_comment_from_post(post_id: UUID, comment_id: UUID, session: SessionDep):
    comment_from_post = services.post_service.get_comment_from_post(post_id, comment_id, session)
    return comment_from_post

@router.delete('/{post_id}/comment/{comment_id}', tags=['comment'])
async def delete_comment_from_post(post_id: UUID, comment_id: UUID, session: SessionDep) -> dict:
    services.post_service.delete_comment_from_post(post_id, comment_id, session)
    return {"ok": True}

@router.put('/{post_id}/comment/{comment_id}', response_model=CommentPublic, tags=['comment'])
async def update_comment_from_post(post_id: UUID, comment_id: UUID, updated_comment: CommentUpdate,session: SessionDep):
    comment = services.post_service.update_comment_from_post(post_id, updated_comment, comment_id, session)
    return comment

