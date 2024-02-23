from fastapi import APIRouter

from .users.auth import auth_router
from .handlers.files import file_router

v1_router = APIRouter(prefix='/api')
v1_router.include_router(router=auth_router)
v1_router.include_router(router=file_router)
