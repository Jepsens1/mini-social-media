from fastapi import APIRouter, Query
from typing import Annotated
from uuid import UUID
from schemas.post_schemas import PostUpdate, PostCreate, PostPublic, PostWithComments, PostWithLikes
from schemas.likes_schemas import LikePublic
from schemas.comment_schemas import CommentPublic, CommentCreate
import services.post_service
from dependencies import SessionDep
from services.authentication_service import CurrentUser

"""
post_router.py

Defines the /posts/* API endpoints.

Endpoints:
- POST  /posts/ -> Create a post (requires authentication)
- GET   /posts/ -> Get a list of posts
- GET   /posts/{post_id} -> Get a single post
- DELETE    /posts/{post_id} -> Delete a post (requires authentication)
- PUT   /posts/{post_id} -> Update a post (requires authentication)
- GET   /posts/{post_id}/comments -> Get a single post including comments
- GET   /posts/{post_id}/likes -> Get a single post including likes
- POST  /posts/{post_id}/comments -> Create a comment to post (requires authentication)
- POST  /posts/{post_id}/like -> Like a post (requires authentication)
- DELETE    /posts/{post_id}/like -> Delete a like to post (requires authentication)
"""

router = APIRouter(prefix='/posts', tags=['posts'])


@router.post('/', response_model=PostPublic)
async def create_post(post: PostCreate, session: SessionDep, current_user: CurrentUser):
    """
    Create a new post owned by the authenticated user.
    """
    post = services.post_service.create_post_object(post, current_user.id, session)
    return post


@router.get('/', response_model=list[PostPublic])
async def get_posts(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100):
    """
    Get a paginated list of posts.
    """
    posts = services.post_service.get_posts(session, offset, limit)
    return posts


@router.get('/{post_id}', response_model=PostPublic)
async def get_post_by_id(post_id: UUID, session: SessionDep):
    """
    Get a specific post by ID.
    """
    post = services.post_service.get_post(post_id, session)
    return post


@router.delete('/{post_id}')
async def delete_post(post_id: UUID, session: SessionDep, current_user: CurrentUser) -> dict:
    """
    Delete a post owned by the authenticated user.
    """
    services.post_service.delete_post(post_id, current_user.id, session)
    return {'Ok': True}


@router.put('/{post_id}', response_model=PostPublic)
async def update_post(post_id: UUID, post: PostUpdate, session: SessionDep, current_user: CurrentUser):
    """
    Update a post owned by the authenticated user.
    """
    updated_post = services.post_service.update_post(post_id, post, current_user.id, session)
    return updated_post


@router.get('/{post_id}/comments', response_model=PostWithComments, tags=['comments'])
async def read_posts_comments(post_id: UUID, session: SessionDep):
    """
    Get a specific post including comments by ID.
    """
    post_with_comments = services.post_service.get_post(post_id, session)
    return post_with_comments


@router.get('/{post_id}/likes', response_model=PostWithLikes, tags=['likes'])
async def read_posts_likes(post_id: UUID, session: SessionDep):
    """
    Get a specific post including likes by ID.
    """
    post_with_likes = services.post_service.get_post(post_id, session)
    return post_with_likes


@router.post('/{post_id}/comments', response_model=CommentPublic, tags=['comments'])
async def create_comment_to_post(post_id: UUID, comment: CommentCreate, session: SessionDep, current_user: CurrentUser):
    """
    Create a comment to a specific post.
    """
    created_comment = services.post_service.create_comment(post_id, comment, current_user.id, session)
    return created_comment

@router.post('/{post_id}/like', response_model=LikePublic, tags=['likes'])
async def like_post(post_id: UUID, session: SessionDep, current_user: CurrentUser):
    """
    Like a specific post.
    """
    liked_post = services.post_service.like_post(post_id, current_user.id, session)
    return liked_post

@router.delete('/{post_id}/like', tags=['likes'])
async def delete_like(post_id: UUID, session: SessionDep, current_user: CurrentUser) -> dict:
    """
    Delete like to a specific post.
    """
    services.post_service.delete_like(post_id, current_user.id, session)
    return {'Ok': True}