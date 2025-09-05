from sqlalchemy import func, select
from models.models import Post, User, Comment, Like
from schemas.post_schemas import PostCreate, PostUpdate
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime, timezone
from schemas.comment_schemas import CommentCreate
from dependencies import SessionDep


def create_post_object(post: PostCreate, owner_id: UUID, session: SessionDep):
    user_exist = session.get(User, owner_id)
    if not user_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user does not exist')
    
    db_post = Post(**post.model_dump(), owner_id=owner_id)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

def get_post(post_id: UUID, session: SessionDep) -> Post:
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    
    comment_count = session.execute(select(func.count(Comment.id)).where(Comment.post_id == post_id)).scalar_one()
    post.comment_count = comment_count
    return post

def get_posts(session: SessionDep, offset: int, limit: int) -> list[Post]:
    stmt = (select(Post, func.count(Comment.id).label('comment_count'))
            .outerjoin(Comment, Comment.post_id == Post.id)
            .group_by(Post.id)
            .offset(offset)
            .limit(limit)
            )
    result = session.execute(stmt)
    posts_with_counts = []
    for post, comment_count in result:
        post.comment_count = comment_count
        posts_with_counts.append(post)
    return posts_with_counts

def delete_post(post_id: UUID, owner_id: UUID, session: SessionDep):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')
    
    if post.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot delete a post that is not yours')
    
    session.delete(post)
    session.commit()

def update_post(post_id: UUID, post: PostUpdate, owner_id: UUID, session: SessionDep):
    db_post = session.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')
    
    if db_post.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot update a post that is not yours')
    
    updated_data = post.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(db_post, field, value)

    setattr(db_post, 'updated_at', datetime.now(timezone.utc))

    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

def create_comment(post_id: UUID, comment: CommentCreate, owner_id: UUID, session: SessionDep):
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

def like_post(post_id: UUID, user_id: UUID, session: SessionDep):
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

def delete_like(post_id: UUID, user_id: UUID, session: SessionDep):
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