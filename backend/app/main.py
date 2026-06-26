from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    """Create and configure the College ERP FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        description="Multi-tenant College ERP Platform API",
    )
    app.include_router(api_router, prefix=settings.API_PREFIX)
    return app


app = create_app()
