from fastapi import APIRouter, Query
from typing import Annotated
from database import SessionDep
from uuid import UUID
from schemas.comment_schemas import CommentPublic, CommentUpdate
import services.comment_service

router = APIRouter(prefix='/comments', tags=['comments'])

@router.get('/{comment_id}', response_model=CommentPublic)
async def get_comment(comment_id: UUID, session: SessionDep):
    comment = services.comment_service.get_comment(comment_id, session)
    return comment

@router.put('/{comment_id}', response_model=CommentPublic)
async def update_comment(comment_id: UUID, comment: CommentUpdate, session: SessionDep):
    updated_comment = services.comment_service.update_comment(comment_id, comment, session)
    return updated_comment

@router.delete('/{comment_id}')
async def delete_comment(comment_id: UUID, owner_id: UUID, session: SessionDep) -> dict:
    services.comment_service.delete_comment(comment_id, owner_id, session)
    return {'Ok': True}