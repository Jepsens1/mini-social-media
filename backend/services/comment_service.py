from models.models import  Comment
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime, timezone
from schemas.comment_schemas import CommentUpdate
from dependencies import SessionDep

def get_comment(comment_id: UUID, session: SessionDep) -> Comment:
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='comment not found')
    return comment

def update_comment(comment_id: UUID, comment: CommentUpdate, session: SessionDep, owner_id: UUID) -> Comment:
    db_comment = session.get(Comment, comment_id)
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='comment not found')
    
    if db_comment.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='cannot change comment with a different user')
    
    db_comment.content = comment.content
    db_comment.last_edited = datetime.now(timezone.utc)

    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment

def delete_comment(comment_id: UUID, owner_id: UUID, session: SessionDep) -> None:
    db_comment = session.get(Comment, comment_id)
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='comment not found')
    
    if db_comment.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='cannot delete comment with a different user')
    
    session.delete(db_comment)
    session.commit()