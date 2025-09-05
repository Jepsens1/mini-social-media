from fastapi import APIRouter, Query, Depends
from typing import Annotated
from database import SessionDep
from uuid import UUID
from schemas.comment_schemas import CommentPublic, CommentUpdate
from schemas.user_schemas import UserPublic
import services.comment_service
from services.authentication_service import get_current_active_user

router = APIRouter(prefix='/comments', tags=['comments'])

CurrentUser = Annotated[UserPublic, Depends(get_current_active_user)]

@router.get('/{comment_id}', response_model=CommentPublic)
async def get_comment(comment_id: UUID, session: SessionDep):
    comment = services.comment_service.get_comment(comment_id, session)
    return comment

@router.put('/{comment_id}', response_model=CommentPublic)
async def update_comment(comment_id: UUID, comment: CommentUpdate, session: SessionDep, current_user: CurrentUser):
    updated_comment = services.comment_service.update_comment(comment_id, comment, session, current_user.id)
    return updated_comment

@router.delete('/{comment_id}')
async def delete_comment(comment_id: UUID, session: SessionDep, current_user: CurrentUser) -> dict:
    services.comment_service.delete_comment(comment_id, current_user.id, session)
    return {'Ok': True}