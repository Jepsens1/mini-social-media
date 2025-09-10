from sqlalchemy import func, select
from models.models import Post, User, Comment, Like
from schemas.post_schemas import PostCreate, PostUpdate
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime, timezone
from schemas.comment_schemas import CommentCreate
from dependencies import SessionDep

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
    likes_count = session.execute(select(func.count(Like.user_id)).where(Like.post_id == post_id)).scalar_one()
    comments_count = session.execute(select(func.count(Comment.id)).where(Comment.post_id == post_id)).scalar_one()

    return likes_count, comments_count

def create_post_object(post: PostCreate, owner_id: UUID, session: SessionDep) -> Post:
    """Creates a new post object"""
    user_exist = session.get(User, owner_id)
    if not user_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user does not exist')
    
    db_post = Post(**post.model_dump(), owner_id=owner_id)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

def get_post_with_liked_by(post_id, session: SessionDep) -> Post:
    post = get_post(post_id, session)
    liked_by = [like.user.username for like in post.likes]
    post.liked_by = liked_by
    return post

def get_post(post_id: UUID, session: SessionDep) -> Post:
    """Get a post based on ID"""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    
    likes_count, comments_count = get_likes_and_comments_count(post.id, session)
    post.likes_count = likes_count
    post.comments_count = comments_count
    return post

def get_posts(session: SessionDep, offset: int, limit: int) -> list[Post]:
    """Get a paginated list of post"""

    posts = session.execute(select(Post).offset(offset).limit(limit)).scalars().all()
    for post in posts:
        likes_count, comments_count = get_likes_and_comments_count(post.id, session)
        post.likes_count = likes_count
        post.comments_count = comments_count
    return list(posts)

def delete_post(post_id: UUID, owner_id: UUID, session: SessionDep) -> None:
    """Delete a post if the owner_id matches the user that created the post"""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')
    
    if post.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Cannot delete a post that is not yours')
    
    session.delete(post)
    session.commit()

def update_post(post_id: UUID, post: PostUpdate, owner_id: UUID, session: SessionDep) -> Post:
    """Update existing post based on ID, if owner_id matches the user created the post"""
    db_post = session.get(Post, post_id)
    if not db_post:
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
    return db_post

def create_comment(post_id: UUID, comment: CommentCreate, owner_id: UUID, session: SessionDep) -> Comment:
    """Creates a new comment object to a specific post"""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    
    user = session.get(User, owner_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    
    db_comment = Comment(**comment.model_dump())
    db_comment.owner_id = owner_id
    db_comment.post_id = post_id
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment

def like_post(post_id: UUID, user_id: UUID, session: SessionDep) -> Like:
    """Creates a like object to a specific post"""
    db_post = session.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    db_user = session.get(User, user_id)
    if not db_user:
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

    return like

def delete_like(post_id: UUID, user_id: UUID, session: SessionDep) -> None:
    """Delete a like object on specific post"""
    db_post = session.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    
    stmt = select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
    like = session.execute(stmt).scalar_one_or_none()
    if not like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='you have not liked this post')
    
    session.delete(like)
    session.commit()