from database import SessionDep
from sqlalchemy import func, select
from models.models import Post, User, Comment
from schemas.post_schemas import PostCreate, PostUpdate
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime, timezone
from schemas.comment_schemas import CommentCreate, CommentUpdate


def create_post_object(post: PostCreate, session: SessionDep):
    user_exist = session.get(User, post.owner_id)
    if not user_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user does not exist')
    
    db_post = Post(**post.model_dump())
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

def delete_post(post_id: UUID, session: SessionDep):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')
    
    session.delete(post)
    session.commit()

def update_post(post_id: UUID, post: PostUpdate, session: SessionDep):
    db_post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')
    
    updated_data = post.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(db_post, field, value)

    setattr(db_post, 'updated_at', datetime.now(timezone.utc))

    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

def create_comment_to_post(post_id: UUID, comment: CommentCreate, session: SessionDep) -> Comment:
    user = session.get(User, comment.owner_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')
    
    db_comment = Comment(**comment.model_dump())
    setattr(db_comment, "post_id", post_id)
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment

def get_comments_from_post(post_id: UUID, offset: int, limit: int, session: SessionDep):
    stmt = select(Comment).where(Comment.post_id == post_id).offset(offset).limit(limit)
    result = session.execute(stmt)
    comments = result.scalars().all()
    return comments

def get_comment_from_post(post_id: UUID, comment_id: UUID, session: SessionDep) -> Comment:
    stmt = select(Comment).where((Comment.id == comment_id) & (Comment.post_id ==  post_id))
    comment = session.execute(stmt).scalars().first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='comment not found')
    return comment

def delete_comment_from_post(post_id: UUID, comment_id: UUID, session: SessionDep):
    stmt = select(Comment).where((Comment.id == comment_id) & (Comment.post_id ==  post_id))
    comment = session.execute(stmt).scalars().first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='comment not found')
    
    session.delete(comment)
    session.commit()

def update_comment_from_post(post_id: UUID, updated_comment: CommentUpdate, comment_id: UUID, session: SessionDep) -> Comment:
    stmt = select(Comment).where((Comment.id == comment_id) & (Comment.post_id ==  post_id))
    db_comment = session.execute(stmt).scalars().first()
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='comment not found')
    updated_data = updated_comment.model_dump()
    for field, value in updated_data.items():
        setattr(db_comment, field, value)
    setattr(db_comment, "last_edited", datetime.now(timezone.utc))
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment