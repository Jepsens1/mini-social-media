from models.models import Comment
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime, timezone
from schemas.comment_schemas import CommentUpdate
from dependencies import SessionDep
from settings import logger

"""
comment_service.py

Handles comments-related logic, including:
- Get a comment object based on ID
- Update a comment object based on ID
- Delete a comment object based on ID


This module integrates with:
- SQLAlchemy ORM models (Comment)
"""

def get_comment(comment_id: UUID, session: SessionDep) -> Comment:
    """Get a comment based on ID"""
    logger.debug('Getting comment from DB by ID', extra={'comment_id': comment_id})
    comment = session.get(Comment, comment_id)
    if not comment:
        logger.warning('comment not found', extra={'comment_id': comment_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='comment not found')
    return comment

def update_comment(comment_id: UUID, comment: CommentUpdate, session: SessionDep, owner_id: UUID) -> Comment:
    """Update existing comment based on ID, if owner_id matches the user created the comment"""
    logger.debug('Updating comment from post', extra={'comment_id': comment_id, 'fields': list(comment.model_dump().keys()), 'values': list(comment.model_dump().values())})
    db_comment = session.get(Comment, comment_id)
    if not db_comment:
        logger.warning('comment not found', extra={'comment_id': comment_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='comment not found')
    
    if db_comment.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='cannot change comment with a different user')
    
    db_comment.content = comment.content
    db_comment.last_edited = datetime.now(timezone.utc)

    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    logger.info('Comment was updated', extra={'comment_id': comment_id, 'comment': db_comment.__dict__})
    return db_comment

def delete_comment(comment_id: UUID, owner_id: UUID, session: SessionDep) -> None:
    """Delete a comment if the owner_id matches the user that created the comment"""
    logger.debug('Deleting comment from post', extra={'comment_id': comment_id, 'user_id': owner_id})
    db_comment = session.get(Comment, comment_id)
    if not db_comment:
        logger.warning('comment not found', extra={'comment_id': comment_id})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='comment not found')
    
    if db_comment.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='cannot delete comment with a different user')
    
    session.delete(db_comment)
    session.commit()
    logger.info('Comment was deleted successfully', extra={'comment_id': comment_id, 'user_id': owner_id})