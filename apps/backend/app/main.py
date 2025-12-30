from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import AppException
from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from app.routers import auth_router, users_router, routes_router
from app.services.user import UserService
from app.schemas.common import HealthResponse

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("application_starting", app_name=settings.APP_NAME)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create admin user if not exists
    async with AsyncSessionLocal() as session:
        try:
            service = UserService(session)
            admin = await service.create_admin_if_not_exists(
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
            )
            if admin:
                logger.info("admin_created", email=admin.email)
            await session.commit()
        except Exception as e:
            logger.error("admin_creation_failed", error=str(e))
            await session.rollback()
    
    logger.info("application_started")
    yield
    
    logger.info("application_stopping")
    await engine.dispose()
    logger.info("application_stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API для управления маршрутами грузоперевозок и отправками",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error("unexpected_error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": [],
            }
        },
    )


# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(routes_router)


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version=settings.APP_VERSION)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
