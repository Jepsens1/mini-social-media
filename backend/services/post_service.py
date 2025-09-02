from database import SessionDep
from models.models import Post, User
from schemas.post_schemas import PostCreate, PostUpdate
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime, timezone


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
    return post

def get_posts(session: SessionDep, offset: int, limit: int) -> list[Post]:
    posts = session.query(Post).offset(offset).limit(limit).all()
    return posts

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
