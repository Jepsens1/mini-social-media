from sqlalchemy import select
from models.models import User
from schemas.user_schemas import UserRegister, UserUpdate
from uuid import UUID
from fastapi import HTTPException, status
from .authentication_service import hash_password
from dependencies import SessionDep

def create_user_object(user: UserRegister, session: SessionDep) -> User:
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
    users = session.query(User).offset(offset).limit(limit).all()
    return users

def read_user(user_id: UUID, session: SessionDep) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

def delete_user(user_id: UUID, session: SessionDep) -> None:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    session.delete(user)
    session.commit()

def update_user(user_id: UUID, user: UserUpdate, session: SessionDep) -> User:
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