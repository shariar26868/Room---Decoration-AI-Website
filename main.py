

"""
Room Designer AI - Main Application
====================================

FastAPI application for AI-powered interior design.

Author: Room Designer Team
Version: 1.0.0
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv
import sys
import io

# Load environment variables
load_dotenv()

# Force UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ===================================================================
# Initialize FastAPI App
# ===================================================================
app = FastAPI(
    title="Room Designer AI API",
    description="""
    AI-powered interior design platform with furniture search and visualization.
    
    ## Features
    - Room image upload
    - Room type and theme selection
    - Furniture selection with auto-dimension calculation
    - Price-based furniture search
    - AI image generation with Replicate
    - AWS S3 storage
    
    ## Workflow
    1. Upload room image
    2. Select room type
    3. Select design theme
    4. Enter room dimensions
    5. Select furniture (with subtypes)
    6. Set price range
    7. Search furniture from theme websites
    8. Generate design image with AI
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===================================================================
# CORS Configuration
# ===================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================================================================
# Initialize AWS Service
# ===================================================================
try:
    from ai_backend.services.aws_service import init_aws_service
    from ai_backend.config import (
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY,
        AWS_S3_BUCKET,
        AWS_REGION
    )
    
    aws_service = init_aws_service(
        access_key=AWS_ACCESS_KEY_ID,
        secret_key=AWS_SECRET_ACCESS_KEY,
        bucket=AWS_S3_BUCKET,
        region=AWS_REGION
    )
    
    # Test connection
    if aws_service.test_connection():
        logger.info("AWS S3 service initialized and connected")
    else:
        logger.warning("AWS S3 connection test failed")
    
except Exception as e:
    logger.error(f"Failed to initialize AWS: {e}")
    logger.warning("Application will start but image uploads will fail")


# ===================================================================
# Import and Register Routers
# ===================================================================
from ai_backend.api import upload, selection, furniture, generation

app.include_router(
    upload.router,
    prefix="/api/upload",
    tags=["Step 1: Upload Room Image"]
)

app.include_router(
    selection.router,
    prefix="/api/selection",
    tags=["Steps 2-5: Room Selection & Furniture"]
)

app.include_router(
    furniture.router,
    prefix="/api/furniture",
    tags=["Steps 6-7: Furniture Search"]
)

app.include_router(
    generation.router,
    prefix="/api/generation",
    tags=["Steps 8-9: AI Image Generation"]
)


# ===================================================================
# Root Endpoint
# ===================================================================
@app.get(
    "/",
    summary="API Root",
    description="Welcome endpoint with API information"
)
async def root():
    """API Root - Health Check and Information"""
    return {
        "message": "Room Designer AI API",
        "version": "1.0.0",
        "status": "running",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "workflow": [
            "1. POST /api/upload/upload - Upload room image",
            "2. GET /api/selection/options/room-types - Get room type dropdown",
            "3. POST /api/selection/room-type - Select room type",
            "4. GET /api/selection/options/themes - Get theme dropdown",
            "5. POST /api/selection/theme - Select design theme",
            "6. POST /api/selection/dimensions - Enter room dimensions",
            "7. GET /api/selection/options/furniture-types/{session_id} - Get furniture dropdown",
            "8. GET /api/selection/options/furniture-subtypes/{session_id}/{type} - Get subtype dropdown",
            "9. POST /api/selection/furniture/select - Select furniture",
            "10. POST /api/furniture/price-range - Set price range",
            "11. POST /api/furniture/search - Search furniture",
            "12. POST /api/generation/generate - Generate design image"
        ],
        "endpoints": {
            "upload": "/api/upload/upload",
            "room_type_options": "/api/selection/options/room-types",
            "room_type": "/api/selection/room-type",
            "theme_options": "/api/selection/options/themes",
            "theme": "/api/selection/theme",
            "dimensions": "/api/selection/dimensions",
            "furniture_type_options": "/api/selection/options/furniture-types/{session_id}",
            "furniture_subtype_options": "/api/selection/options/furniture-subtypes/{session_id}/{type}",
            "furniture_select": "/api/selection/furniture/select",
            "fit_check": "/api/selection/furniture/fit-check",
            "price_range": "/api/furniture/price-range",
            "search": "/api/furniture/search",
            "generate": "/api/generation/generate",
            "session": "/api/furniture/session/{session_id}"
        }
    }


# ===================================================================
# Health Check
# ===================================================================
@app.get(
    "/health",
    summary="Health Check",
    description="Check API and service health"
)
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    
    # Check AWS connection
    aws_status = "disconnected"
    try:
        from ai_backend.services.aws_service import get_aws_service
        aws = get_aws_service()
        if aws.test_connection():
            aws_status = "connected"
    except:
        pass
    
    # Check Replicate API token
    replicate_status = "configured" if os.getenv("REPLICATE_API_TOKEN") else "missing"
    
    # Check furniture data
    furniture_data_status = "loaded"
    try:
        from ai_backend.api.selection import FURNITURE_DATA
        if not FURNITURE_DATA:
            furniture_data_status = "missing"
    except:
        furniture_data_status = "error"
    
    return {
        "status": "healthy",
        "timestamp": str(datetime.now()),
        "services": {
            "aws_s3": aws_status,
            "replicate_api": replicate_status,
            "furniture_data": furniture_data_status
        },
        "configuration": {
            "bucket": os.getenv("AWS_S3_BUCKET"),
            "region": os.getenv("AWS_REGION"),
            "use_local_storage": os.getenv("USE_LOCAL_STORAGE", "false")
        }
    }


# ===================================================================
# Error Handlers
# ===================================================================
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": "Not Found",
            "detail": "The requested resource was not found",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later."
        }
    )


# ===================================================================
# Startup Event
# ===================================================================
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    from datetime import datetime
    
    logger.info("=" * 60)
    logger.info("Starting Room Designer AI API")
    logger.info("=" * 60)
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Version: 1.0.0")
    logger.info("=" * 60)


# ===================================================================
# Shutdown Event
# ===================================================================
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("=" * 60)
    logger.info("Shutting down Room Designer AI API")
    logger.info("=" * 60)


# ===================================================================
# Run Server
# ===================================================================
if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    
    logger.info("\n" + "=" * 60)
    logger.info("Room Designer AI - Starting Server")
    logger.info("=" * 60)
    logger.info(f"API Documentation: http://localhost:8000/docs")
    logger.info(f"ReDoc: http://localhost:8000/redoc")
    logger.info(f"Health Check: http://localhost:8000/health")
    logger.info(f"Base URL: http://localhost:8000")
    logger.info("=" * 60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )