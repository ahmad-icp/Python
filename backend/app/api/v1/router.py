from fastapi import APIRouter

from app.modules.authentication.router import router as authentication_router
from app.modules.settings.router import router as settings_router
from app.modules.students.router import router as students_router

api_router = APIRouter()
api_router.include_router(authentication_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
api_router.include_router(students_router, prefix="/students", tags=["Student Information System"])


@api_router.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Return API health status for load balancers and uptime checks."""
    return {"status": "ok", "service": "college-erp-platform"}
