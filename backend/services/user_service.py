from sqlalchemy import select
from models.models import User
from schemas.user_schemas import UserRegister, UserUpdate
from uuid import UUID
from fastapi import HTTPException, status
from .authentication_service import hash_password
from .post_service import get_likes_and_comments_count
from dependencies import SessionDep

"""
user_service.py

Handles posts-related logic, including:
- Creating a user
- Get a user by ID
- Get a list of users
- Update a user object based on ID
- Delete a user object based on ID


This module integrates with:
- SQLAlchemy ORM models (User)
"""
def create_user_object(user: UserRegister, session: SessionDep) -> User:
    """Creates a new user object if the user does not already exist"""
    statement = select(User).where(User.username == user.username)
    user_exist = session.execute(statement).first()
    if user_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exist')
    
    user_data = user.model_dump(exclude={'password'})
    user_data['hashed_password'] = hash_password(user.password)
    db_user = User(**user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def read_users_from_db(session: SessionDep, offset: int, limit: int) -> list[User]:
    """Get a paginated list off users"""
    stmt = select(User).offset(offset).limit(limit)
    users = session.execute(stmt).scalars().all()
    return list(users)

def read_user_including_counts(user_id: UUID, session: SessionDep) -> User:
    """Get a user including likes_count and comments_count based on ID"""
    user = read_user(user_id, session)
    for post in user.posts:
        likes_count, comments_count = get_likes_and_comments_count(post.id, session)
        post.likes_count = likes_count
        post.comments_count = comments_count

    return user

def read_user(user_id: UUID, session: SessionDep) -> User:
    """Get a user based on ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

def delete_user(user_id: UUID, session: SessionDep) -> None:
    """Delete a user based on ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    session.delete(user)
    session.commit()

def update_user(user_id: UUID, user: UserUpdate, session: SessionDep) -> User:
    """Update existing user based on ID"""
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found') 
    updated_data = user.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(db_user, field, value)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user