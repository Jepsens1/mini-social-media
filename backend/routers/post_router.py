from fastapi import APIRouter, Query
from typing import Annotated
from database import SessionDep
from uuid import UUID
from schemas.post_schemas import PostUpdate, PostCreate, PostPublic, PostWithComments, PostWithLikes
from schemas.likes_schemas import LikePublic
from schemas.comment_schemas import CommentPublic, CommentCreate
import services.post_service

router = APIRouter(prefix='/posts', tags=['posts'])

@router.post('/', response_model=PostPublic)
async def create_post(post: PostCreate, session: SessionDep):
    post = services.post_service.create_post_object(post, session)
    return post


@router.get('/', response_model=dict[str, list[PostPublic]])
async def get_posts(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    posts = services.post_service.get_posts(session, offset, limit)
    return {"posts": posts}


@router.get('/{post_id}', response_model=PostPublic)
async def get_post_by_id(post_id: UUID, session: SessionDep):
    post = services.post_service.get_post(post_id, session)
    return post


@router.delete('/{post_id}')
async def delete_post(post_id: UUID, session: SessionDep) -> dict:
    services.post_service.delete_post(post_id, session)
    return {'Ok': True}


@router.put('/{post_id}', response_model=PostPublic)
async def update_post(post_id: UUID, post: PostUpdate, session: SessionDep):
    updated_post = services.post_service.update_post(post_id, post, session)
    return updated_post


@router.get('/{post_id}/comments', response_model=PostWithComments, tags=['comments'])
async def read_posts_comments(post_id: UUID, session: SessionDep):
    post_with_comments = services.post_service.get_post(post_id, session)
    return post_with_comments


@router.get('/{post_id}/likes', response_model=PostWithLikes, tags=['likes'])
async def read_posts_likes(post_id: UUID, session: SessionDep):
    post_with_likes = services.post_service.get_post(post_id, session)
    return post_with_likes


@router.post('/{post_id}/comments', response_model=CommentPublic, tags=['comments'])
async def create_comment_to_post(post_id: UUID, comment: CommentCreate, session: SessionDep):
    created_comment = services.post_service.create_comment(post_id, comment, session)
    return created_comment

@router.post('/{post_id}/like', response_model=LikePublic, tags=['likes'])
async def like_post(post_id: UUID, user_id: UUID, session: SessionDep):
    liked_post = services.post_service.like_post(post_id, user_id, session)
    return liked_post

@router.delete('/{post_id}/like', tags=['likes'])
async def delete_like(post_id: UUID, user_id: UUID, session: SessionDep) -> dict:
    services.post_service.delete_like(post_id, user_id, session)
    return {'Ok': True}