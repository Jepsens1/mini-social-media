from fastapi import FastAPI, Depends, HTTPException, status, Request
from datetime import timedelta
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers import user_router, post_router, comment_router
from fastapi.security import OAuth2PasswordRequestForm
from dependencies import SessionDep
from services.authentication_service import create_access_token, verify_refresh_token, create_refresh_token, authenticate_user ,ACCESS_TOKEN_EXPIRE_MINUTES, Token, revoke_refresh_token
from slowapi import _rate_limit_exceeded_handler, Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

"""
main.py 

Entry point for the whole FastAPI application

Handles FastAPI setup, including:
- Setup rate-limit (slowapi)
- Include routers (user, post, comment)
- Add CORS middleware

Defines the /auth/* endpoints.

Endpoint:
- GET   / -> main entry point for the api
- POST  /auth/token -> Login endpoint using oauth2 password flow, returning short-lived (JWT) and long-lived (refresh-token)
- POST  /auth/refresh -> Refresh endpoint for receiving new short-lived and long-lived tokens
- DELETE    /auth/logout -> Revokes a current device/session refresh-token
"""

app = FastAPI()

#rate limit using slowapi
limiter = Limiter(key_func=get_remote_address, strategy="moving-window",default_limits=["10/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore
app.add_middleware(SlowAPIMiddleware)

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


@app.post('/auth/token', response_model=Token)
async def login(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    """Creates a Token object containing access_token and refresh_token if the user is authenticated"""
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password',
                            headers={'WWW-Authenticate': 'Bearer'})
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    user_agent = request.headers.get("user-agent", "Unknown")
    refresh_token = create_refresh_token(user.id, user_agent, session)
    return Token(access_token=access_token, refresh_token=refresh_token.token, token_type='bearer')

@app.post('/auth/refresh', response_model=Token)
async def refresh_token(request: Request, refresh_token: str, session: SessionDep):
    """Creates a Token object containing access_token and refresh_token if the input refresh_token is valid"""
    db_token = verify_refresh_token(refresh_token, session)
    user_agent = request.headers.get("user-agent", "Unknown")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(data={"sub": str(db_token.user_id)}, expires_delta=access_token_expires)
    new_refresh_token = create_refresh_token(db_token.user_id, user_agent, session)

    return Token(access_token=new_access_token, refresh_token=new_refresh_token.token, token_type='bearer')

@app.delete('/auth/logout')
async def revoke_token(refresh_token: str, session: SessionDep):
    """Revokes a current device/session"""
    revoke_refresh_token(refresh_token, session)
    return {'msg': "Logged out"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)