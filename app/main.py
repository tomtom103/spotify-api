import logging
from typing import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.settings import CONFIG
from app.instrumentation.logging import init_logging
from app.routers.api_router import api_router

init_logging()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting application")

    yield

    logger.info("Shutting down application")


app = FastAPI(
    title=CONFIG.PROJECT_NAME,
    version=CONFIG.VERSION,
    root_path=CONFIG.PROXY_ROOT_PATH,
    openapi_url=CONFIG.OPEN_API_URL,
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
    exception_handlers={}
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=CONFIG.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/", include_in_schema=False)
def docs_redirect() -> RedirectResponse:
    return RedirectResponse(f"{CONFIG.PROXY_ROOT_PATH}/api/v1/docs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="app.main:app",
        host=CONFIG.API_HOST,
        port=CONFIG.API_PORT,
        reload=True,
        reload_dirs=["app"],
        lifespan="on",
    )
