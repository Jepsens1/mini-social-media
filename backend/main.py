from fastapi import FastAPI, Depends, HTTPException, status
from datetime import timedelta
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from database import create_db_and_tables
from routers import user_router, post_router, comment_router
from fastapi.security import OAuth2PasswordRequestForm
from dependencies import SessionDep
from services.authentication_service import create_access_token, authenticate_user ,ACCESS_TOKEN_EXPIRE_MINUTES, Token
#Event on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(user_router.router)
app.include_router(post_router.router)
app.include_router(comment_router.router)

origins_allowed = [
    'http://localhost:3000',
    'https://localhost:5173'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_allowed,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
async def health_status() -> dict:
    return {"info": "hello world"}


@app.post('/auth/token')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password',
                            headers={'WWW-Authenticate': 'Bearer'})
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type='bearer')

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)