from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from database import create_db_and_tables
from routers import user_router, post_router, comment_router


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
    return {'message': 'Hello World!'}

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)