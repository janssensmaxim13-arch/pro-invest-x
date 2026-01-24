# ============================================================================
# ProInvestiX Enterprise API - Main Application
# ============================================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
import sys

from app.config import settings
from app.db.database import init_db, close_db
from app.api.v1.router import api_router
from app.core.exceptions import ProInvestiXException


# =============================================================================
# LOGGING SETUP
# =============================================================================

# Remove default logger
logger.remove()

# Add custom logger
if settings.LOG_FORMAT == "json":
    logger.add(
        sys.stdout,
        format="{message}",
        serialize=True,
        level=settings.LOG_LEVEL,
    )
else:
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
    )


# =============================================================================
# LIFESPAN (STARTUP/SHUTDOWN)
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting ProInvestiX API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ProInvestiX API...")
    await close_db()
    logger.info("Database connection closed")


# =============================================================================
# APPLICATION FACTORY
# =============================================================================

def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="""
        ## ProInvestiX Enterprise API
        
        National Investment Platform for Football Development.
        
        ### Features
        
        * **NTSP** - National Talent Scouting Platform
        * **Transfers** - Transfer Management & Compensation
        * **Academy** - Academy Management
        * **TicketChain** - Blockchain Ticketing
        * **Foundation Bank** - Sadaka Jaaria Foundation
        * **Diaspora Wallet** - Digital Wallet for Diaspora
        * **FanDorpen** - WK 2030 Fan Villages
        * **And more...**
        
        ### Authentication
        
        All protected endpoints require a JWT Bearer token.
        Obtain a token via `/api/v1/auth/login`.
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # =========================================================================
    # CORS MIDDLEWARE
    # =========================================================================
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # =========================================================================
    # EXCEPTION HANDLERS
    # =========================================================================
    
    @app.exception_handler(ProInvestiXException)
    async def proinvestix_exception_handler(
        request: Request,
        exc: ProInvestiXException,
    ) -> JSONResponse:
        """Handle custom ProInvestiX exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.detail,
                },
            },
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation failed",
                    "details": exc.errors(),
                },
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                },
            },
        )
    
    # =========================================================================
    # ROUTES
    # =========================================================================
    
    @app.get("/", tags=["Health"])
    async def root():
        """Root endpoint - API information."""
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
        }
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    return app


# =============================================================================
# CREATE APP INSTANCE
# =============================================================================

app = create_application()


# =============================================================================
# RUN WITH UVICORN (for development)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS,
    )
