from fastapi import APIRouter

# Create the main API router
api_router = APIRouter()


# Health check endpoint for API v1
@api_router.get("/health")
async def api_health_check():
    """
    API v1 health check endpoint.
    """
    return {"status": "healthy", "api_version": "v1"}


# Import and include routers
from app.api.v1.endpoints import achievements, auth, classes, grades, reports, students, terms

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])
api_router.include_router(grades.router, prefix="/grades", tags=["grades"])
api_router.include_router(achievements.router, prefix="/achievements", tags=["achievements"])
api_router.include_router(terms.router, prefix="/terms", tags=["terms"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
