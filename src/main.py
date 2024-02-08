import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from api.v1 import auth_router, file_router
from core.logger import LOGGING_CONFIG
from core.settings import app_settings

app = FastAPI(
    title=app_settings.APP_TITLE,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse
)
app.include_router(auth_router)
app.include_router(file_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.ALLOWED_ORIGINS.split(),
    allow_credentials=True,
    allow_headers=['*'],
    allow_methods=['*']
)


if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=True,
        log_config=LOGGING_CONFIG
    )
