from fastapi import FastAPI
from src.controllers.user_api import router as user_router

app = FastAPI(title='User API Service')

app.include_router(user_router)
