import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.logger import LOGGING_CONFIG
from core.settings import app_settings

app = FastAPI(
    title=app_settings.APP_TITLE,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse
)


if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=True,
        log_config=LOGGING_CONFIG
    )
