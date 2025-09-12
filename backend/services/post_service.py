from sqlalchemy import func, select
from models.models import Post, User, Comment, Like
from schemas.post_schemas import PostCreate, PostUpdate
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime, timezone
from schemas.comment_schemas import CommentCreate
from dependencies import SessionDep
from settings import logger
"""
post_service.py

Handles posts-related logic, including:
- Creating a post
- Get a post object based on ID
- Get a list of posts
- Update a post object based on ID
- Delete a post object based on ID
- Create a comment to specific post
- Like a specific post
- Remove like to specific post


This module integrates with:
- SQLAlchemy ORM models (Post, User, Comment, Like)
"""

def get_likes_and_comments_count(post_id: UUID, session: SessionDep) -> tuple[int, int]:

    logger.debug('Getting likes and comments count', extra={'post_id': post_id})
    likes_count = session.execute(select(func.count(Like.user_id)).where(Like.post_id == post_id)).scalar_one()
    comments_count = session.execute(select(func.count(Comment.id)).where(Comment.post_id == post_id)).scalar_one()
    logger.info('Retrieved likes and comment count', extra={'likes_count': likes_count, 'comments_count': comments_count})
    return likes_count, comments_count

def create_post_object(post: PostCreate, owner_id: UUID, session: SessionDep) -> Post:
    """Creates a new post object"""
    logger.debug('Creating a new post', extra={'fields': list(post.model_dump().keys()), 'values': list(post.model_dump().values()),'user_id': owner_id})
    user_exist = session.get(User, owner_id)
    if not user_exist:
        logger.warning("User was not found", extra={'user_id': owner_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user does not exist')
    
    db_post = Post(**post.model_dump(), owner_id=owner_id)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    logger.info('Created a new post', extra={'fields': list(post.model_dump().keys()), 'values': list(post.model_dump().values()),'user_id': owner_id, 'post_id': db_post.id})
    return db_post

def get_post_with_liked_by(post_id, session: SessionDep) -> Post:
    post = get_post(post_id, session)
    liked_by = [like.user.username for like in post.likes]
    post.liked_by = liked_by
    return post

def get_post(post_id: UUID, session: SessionDep) -> Post:
    """Get a post based on ID"""
    logger.debug('Getting a post by ID', extra={'post_id': post_id})
    post = session.get(Post, post_id)
    if not post:
        logger.warning("post was not found", extra={'post_id': post_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    
    likes_count, comments_count = get_likes_and_comments_count(post.id, session)
    post.likes_count = likes_count
    post.comments_count = comments_count
    logger.info('Post retrieved', extra={'post': post.__dict__, 'post_id': post_id})
    return post

def get_posts(session: SessionDep, offset: int, limit: int) -> list[Post]:
    """Get a paginated list of post"""
    logger.debug('Getting posts from DB', extra={'offset': offset, 'limit': limit})
    posts = session.execute(select(Post).offset(offset).limit(limit)).scalars().all()
    for post in posts:
        likes_count, comments_count = get_likes_and_comments_count(post.id, session)
        post.likes_count = likes_count
        post.comments_count = comments_count
    logger.info('Retrieved posts from DB', extra={'count': len(posts)})
    return list(posts)

def delete_post(post_id: UUID, owner_id: UUID, session: SessionDep) -> None:
    """Delete a post if the owner_id matches the user that created the post"""
    logger.debug('Deleting post request', extra={'post_id': post_id, 'user_id': owner_id})
    post = session.get(Post, post_id)
    if not post:
        logger.warning("post was not found", extra={'post_id': post_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')
    
    if post.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Cannot delete a post that is not yours')
    
    session.delete(post)
    session.commit()
    logger.info('Post deleted', extra={'post_id': post_id, 'user_id': owner_id})

def update_post(post_id: UUID, post: PostUpdate, owner_id: UUID, session: SessionDep) -> Post:
    """Update existing post based on ID, if owner_id matches the user created the post"""
    logger.debug('Updating post request', extra={'post_id': post_id, 'user_id': owner_id, 'fields': list(post.model_dump().keys()), 'values': list(post.model_dump().values())})
    db_post = session.get(Post, post_id)
    if not db_post:
        logger.warning("post was not found", extra={'post_id': post_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')
    
    if db_post.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Cannot update a post that is not yours')
    
    updated_data = post.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(db_post, field, value)

    setattr(db_post, 'updated_at', datetime.now(timezone.utc))

    session.add(db_post)
    session.commit()
    session.refresh(db_post)

    likes_count, comments_count = get_likes_and_comments_count(db_post.id, session)
    db_post.likes_count = likes_count
    db_post.comments_count = comments_count
    logger.info('Updated post with new values', extra={'post_id': post_id, 'user_id': owner_id, 'post': db_post.__dict__})
    return db_post

def create_comment(post_id: UUID, comment: CommentCreate, owner_id: UUID, session: SessionDep) -> Comment:
    """Creates a new comment object to a specific post"""

    logger.debug('Creating comments for post', extra={'post_id': post_id, 'user_id': owner_id, 'fields': list(comment.model_dump().keys()), 'values': list(comment.model_dump().values())})
    post = session.get(Post, post_id)
    if not post:
        logger.warning("post was not found", extra={'post_id': post_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    
    user = session.get(User, owner_id)
    if not user:
        logger.warning("user was not found", extra={'user_id': owner_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    
    db_comment = Comment(**comment.model_dump())
    db_comment.owner_id = owner_id
    db_comment.post_id = post_id
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    logger.info('Created comment for post', extra={'post_id': post_id, 'user_id': owner_id, 'comment': db_comment.__dict__})
    return db_comment

def like_post(post_id: UUID, user_id: UUID, session: SessionDep) -> Like:
    """Creates a like object to a specific post"""
    logger.debug('Liking post', extra={'post_id': post_id, 'user_id': user_id})
    db_post = session.get(Post, post_id)
    if not db_post:
        logger.warning("post was not found", extra={'post_id': post_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    db_user = session.get(User, user_id)
    if not db_user:
        logger.warning("user was not found", extra={'user_id': user_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    
    if db_post.owner_id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='cannot like own post')
    
    stmt = select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    already_liked = session.execute(stmt).scalar_one_or_none()
    if already_liked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='already liked the post')
    
    like = Like(post_id=post_id, user_id=user_id)
    session.add(like)
    session.commit()
    session.refresh(like)
    logger.info('Post was liked successfully', extra={'like': like.__dict__, 'post_id': post_id, 'user_id': user_id})
    return like

def delete_like(post_id: UUID, user_id: UUID, session: SessionDep) -> None:
    """Delete a like object on specific post"""
    db_post = session.get(Post, post_id)
    if not db_post:
        logger.warning("post was not found", extra={'post_id': post_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    db_user = session.get(User, user_id)
    if not db_user:
        logger.warning("user was not found", extra={'user_id': user_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    
    stmt = select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    like = session.execute(stmt).scalar_one_or_none()
    if not like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='you have not liked this post')
    
    session.delete(like)
    session.commit()
    logger.info('Removed a like from post successfully', extra={'like': like.__dict__, 'post_id': post_id, 'user_id': user_id})