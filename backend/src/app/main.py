from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.middleware import (
    CSRFMiddleware,
    SessionMiddleware,
    SessionSecurityMiddleware,
)


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    # Set up CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add authentication middleware (order matters!)
    # 1. Session middleware - handles session validation and extension
    app.add_middleware(
        SessionMiddleware,
        cleanup_interval=100,  # Clean up expired sessions every 100 requests
    )

    # 2. Session security middleware - additional security checks
    app.add_middleware(
        SessionSecurityMiddleware,
        enable_ip_validation=not settings.DEBUG,  # Disable IP validation in debug mode
        enable_user_agent_validation=not settings.DEBUG,  # Disable UA validation in debug mode
    )

    # 3. CSRF middleware - protects against CSRF attacks
    app.add_middleware(
        CSRFMiddleware,
        protected_methods={"POST", "PUT", "DELETE", "PATCH"},
        exempt_paths=[
            "/docs",
            "/redoc",
            "/openapi.json",
            f"{settings.API_V1_STR}/auth/login",
            f"{settings.API_V1_STR}/health",
            "/health",
        ],
        require_referer_check=not settings.DEBUG,
        allowed_hosts=["localhost", "127.0.0.1"] if settings.DEBUG else [],
    )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Report Card Assistant API",
            "version": settings.VERSION,
            "docs": f"{settings.API_V1_STR}/docs",
        }

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


# Create the application instance
app = create_application()


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Perform startup tasks.
    """
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")

    # Initialize database (ensure tables exist)
    try:
        from app.core.database import init_db, test_connection
        from app.core.seed_data import seed_database

        # Test database connection
        if test_connection():
            print("✅ Database connection successful")

            # Initialize database tables
            init_db()
            print("✅ Database tables initialized")
            
            # Seed database with initial data
            seed_database()
            print("✅ Database seeded with initial data")
        else:
            print("❌ Database connection failed")

    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        # In production, you might want to exit here
        # raise e


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Perform cleanup tasks.
    """
    print(f"Shutting down {settings.PROJECT_NAME}")
