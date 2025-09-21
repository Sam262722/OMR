"""
Main FastAPI application for OMR Evaluation System
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import os

# Import application modules
from app.api.omr_routes import router as omr_router
from app.core.config import get_settings
from app.core.database import init_db

# Get settings
settings = get_settings()

# Create FastAPI instance
app = FastAPI(
    title="OMR Evaluation System API",
    description="Backend API for automated OMR sheet evaluation with high accuracy bubble detection",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Create necessary directories
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/results", StaticFiles(directory="results"), name="results")

# Include API routes
app.include_router(
    omr_router,
    prefix="/api/omr",
    tags=["OMR Processing"]
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("🚀 Starting OMR Evaluation System Backend...")
    
    # Initialize database connection
    await init_db()
    
    # Create upload and result directories
    os.makedirs("uploads/omr_sheets", exist_ok=True)
    os.makedirs("uploads/answer_keys", exist_ok=True)
    os.makedirs("results/processed", exist_ok=True)
    os.makedirs("results/reports", exist_ok=True)
    
    print("✅ Backend initialization complete")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔒 Authentication: {'Enabled' if settings.REQUIRE_AUTH else 'Disabled'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    print("🛑 Shutting down OMR Evaluation System Backend...")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "OMR Evaluation System API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "High-accuracy OMR sheet processing",
            "Automatic bubble detection and scoring",
            "Batch processing support",
            "Multiple export formats (JSON, CSV)",
            "Real-time processing status",
            "Comprehensive error handling"
        ],
        "endpoints": {
            "documentation": "/api/docs",
            "health_check": "/health",
            "omr_processing": "/api/omr/"
        }
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    
    # Check OMR engine availability
    omr_status = "available"
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'omr_engine'))
        from omr_processor import process_omr_sheet
    except ImportError:
        omr_status = "unavailable"
    
    # Check directories
    directories_ok = all([
        UPLOAD_DIR.exists(),
        RESULTS_DIR.exists(),
        (UPLOAD_DIR / "omr_sheets").exists(),
        (RESULTS_DIR / "processed").exists()
    ])
    
    return {
        "status": "healthy" if omr_status == "available" and directories_ok else "degraded",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "components": {
            "omr_engine": omr_status,
            "directories": "ok" if directories_ok else "error",
            "database": "configured" if settings.SUPABASE_URL else "not_configured"
        },
        "limits": {
            "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024),
            "max_batch_size": settings.MAX_BATCH_SIZE,
            "allowed_file_types": settings.ALLOWED_FILE_TYPES
        }
    }


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with detailed error information."""
    return {
        "error": True,
        "message": exc.detail,
        "status_code": exc.status_code,
        "path": str(request.url.path)
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    error_detail = str(exc) if settings.DEBUG else "An unexpected error occurred"
    
    return {
        "error": True,
        "message": "Internal server error",
        "status_code": 500,
        "detail": error_detail,
        "path": str(request.url.path)
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )