from fastapi import APIRouter
from uuid import UUID
from dependencies import SessionDep
from schemas.comment_schemas import CommentPublic, CommentUpdate
import services.comment_service
from services.authentication_service import CurrentUser

router = APIRouter(prefix='/comments', tags=['comments'])

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